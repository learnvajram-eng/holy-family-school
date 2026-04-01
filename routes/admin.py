import os
from flask import (Blueprint, render_template, request, flash,
                   redirect, url_for, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from werkzeug.utils import secure_filename
from models import db, Admin, Announcement, Inquiry, ContactMessage, GalleryImage

admin_bp = Blueprint('admin_bp', __name__)


# ── Forms ──────────────────────────────────────────────────────────────────────

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    active = BooleanField('Active', default=True)


class GalleryUploadForm(FlaskForm):
    image = FileField('Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    caption = StringField('Caption', validators=[Length(max=300)])
    category = StringField('Category', validators=[DataRequired(), Length(max=50)])


# ── Auth ───────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_bp.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_bp.login'))


# ── Dashboard ──────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'inquiries': Inquiry.query.count(),
        'new_inquiries': Inquiry.query.filter_by(is_read=False).count(),
        'messages': ContactMessage.query.count(),
        'new_messages': ContactMessage.query.filter_by(is_read=False).count(),
        'announcements': Announcement.query.count(),
        'gallery': GalleryImage.query.count(),
    }
    recent_inquiries = Inquiry.query.order_by(Inquiry.date.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.date.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_inquiries=recent_inquiries,
                           recent_messages=recent_messages)


# ── Inquiries ──────────────────────────────────────────────────────────────────

@admin_bp.route('/inquiries')
@login_required
def inquiries():
    all_inquiries = Inquiry.query.order_by(Inquiry.date.desc()).all()
    # Mark all as read
    Inquiry.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/inquiries.html', inquiries=all_inquiries)


@admin_bp.route('/inquiries/delete/<int:id>', methods=['POST'])
@login_required
def delete_inquiry(id):
    inquiry = Inquiry.query.get_or_404(id)
    db.session.delete(inquiry)
    db.session.commit()
    flash('Inquiry deleted.', 'success')
    return redirect(url_for('admin_bp.inquiries'))


# ── Messages ───────────────────────────────────────────────────────────────────

@admin_bp.route('/messages')
@login_required
def messages():
    all_messages = ContactMessage.query.order_by(ContactMessage.date.desc()).all()
    ContactMessage.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/messages.html', messages=all_messages)


@admin_bp.route('/messages/delete/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin_bp.messages'))


# ── Announcements CRUD ─────────────────────────────────────────────────────────

@admin_bp.route('/announcements')
@login_required
def announcements():
    all_ann = Announcement.query.order_by(Announcement.date.desc()).all()
    form = AnnouncementForm()
    return render_template('admin/announcements.html', announcements=all_ann, form=form)


@admin_bp.route('/announcements/create', methods=['POST'])
@login_required
def create_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        ann = Announcement(
            title=form.title.data,
            content=form.content.data,
            active=form.active.data,
        )
        db.session.add(ann)
        db.session.commit()
        flash('Announcement created successfully.', 'success')
    else:
        flash('Please fill all required fields.', 'danger')
    return redirect(url_for('admin_bp.announcements'))


@admin_bp.route('/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    ann = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=ann)
    if form.validate_on_submit():
        ann.title = form.title.data
        ann.content = form.content.data
        ann.active = form.active.data
        db.session.commit()
        flash('Announcement updated.', 'success')
        return redirect(url_for('admin_bp.announcements'))
    return render_template('admin/edit_announcement.html', form=form, ann=ann)


@admin_bp.route('/announcements/delete/<int:id>', methods=['POST'])
@login_required
def delete_announcement(id):
    ann = Announcement.query.get_or_404(id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('admin_bp.announcements'))


@admin_bp.route('/announcements/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_announcement(id):
    ann = Announcement.query.get_or_404(id)
    ann.active = not ann.active
    db.session.commit()
    status = 'activated' if ann.active else 'deactivated'
    flash(f'Announcement {status}.', 'success')
    return redirect(url_for('admin_bp.announcements'))


# ── Gallery ────────────────────────────────────────────────────────────────────

@admin_bp.route('/gallery')
@login_required
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.upload_date.desc()).all()
    form = GalleryUploadForm()
    return render_template('admin/gallery.html', images=images, form=form,
                           categories=GalleryImage.CATEGORIES)


@admin_bp.route('/gallery/upload', methods=['POST'])
@login_required
def upload_image():
    form = GalleryUploadForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)
        # Prefix timestamp to avoid collisions
        import time
        filename = f"{int(time.time())}_{filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        image = GalleryImage(
            filename=filename,
            caption=form.caption.data,
            category=form.category.data,
        )
        db.session.add(image)
        db.session.commit()
        flash('Image uploaded successfully.', 'success')
    else:
        flash('Upload failed. Please check the file and try again.', 'danger')
    return redirect(url_for('admin_bp.gallery'))


@admin_bp.route('/gallery/delete/<int:id>', methods=['POST'])
@login_required
def delete_image(id):
    image = GalleryImage.query.get_or_404(id)
    # Remove physical file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('admin_bp.gallery'))
