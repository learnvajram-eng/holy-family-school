from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional
from models import db, Announcement, Inquiry, ContactMessage, GalleryImage

main_bp = Blueprint('main_bp', __name__)


# ── Forms ──────────────────────────────────────────────────────────────────────

class InquiryForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired(), Length(max=150)])
    parent_name = StringField("Parent's Name", validators=[DataRequired(), Length(max=150)])
    class_applying = SelectField('Class Applying For', validators=[DataRequired()], choices=[
        ('', 'Select Class'),
        ('LKG', 'LKG'), ('UKG', 'UKG'),
        ('Class 1', 'Class I'), ('Class 2', 'Class II'), ('Class 3', 'Class III'),
        ('Class 4', 'Class IV'), ('Class 5', 'Class V'), ('Class 6', 'Class VI'),
        ('Class 7', 'Class VII'), ('Class 8', 'Class VIII'), ('Class 9', 'Class IX'),
        ('Class 10', 'Class X'),
    ])
    phone = TelField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email Address', validators=[Optional(), Email(), Length(max=150)])
    message = TextAreaField('Additional Message', validators=[Optional(), Length(max=500)])


class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(max=150)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=150)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])


# ── Routes ─────────────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    announcements = Announcement.query.filter_by(active=True).order_by(Announcement.date.desc()).limit(5).all()
    return render_template('index.html', announcements=announcements)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/academics')
def academics():
    return render_template('academics.html')


@main_bp.route('/admissions', methods=['GET', 'POST'])
def admissions():
    form = InquiryForm()
    if form.validate_on_submit():
        inquiry = Inquiry(
            student_name=form.student_name.data,
            parent_name=form.parent_name.data,
            class_applying=form.class_applying.data,
            phone=form.phone.data,
            email=form.email.data,
            message=form.message.data,
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Your inquiry has been submitted! We will contact you shortly.', 'success')
        return redirect(url_for('main_bp.admissions') + '#inquiry-form')
    return render_template('admissions.html', form=form)


@main_bp.route('/gallery')
def gallery():
    category = request.args.get('category', 'All')
    if category and category != 'All':
        images = GalleryImage.query.filter_by(category=category).order_by(GalleryImage.upload_date.desc()).all()
    else:
        images = GalleryImage.query.order_by(GalleryImage.upload_date.desc()).all()
    categories = ['All'] + GalleryImage.CATEGORIES
    return render_template('gallery.html', images=images, categories=categories, active_category=category)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg_record = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
        )
        db.session.add(msg_record)
        db.session.commit()

        # Send email notification
        try:
            from app import mail
            admin_email = current_app.config.get('ADMIN_EMAIL')
            if admin_email and current_app.config.get('MAIL_USERNAME'):
                email_msg = Message(
                    subject=f'[HFEMS Website] New Contact: {form.subject.data}',
                    recipients=[admin_email],
                    body=(
                        f'Name: {form.name.data}\n'
                        f'Email: {form.email.data}\n'
                        f'Subject: {form.subject.data}\n\n'
                        f'Message:\n{form.message.data}'
                    )
                )
                mail.send(email_msg)
        except Exception:
            pass  # Don't fail the page if email fails

        flash('Thank you for contacting us! We will get back to you within 24 hours.', 'success')
        return redirect(url_for('main_bp.contact'))
    return render_template('contact.html', form=form)
