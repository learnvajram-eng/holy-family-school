import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from models import db, Admin
from config import config

mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure gallery upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Init extensions
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'admin_bp.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Register blueprints
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Create DB tables and default admin
    with app.app_context():
        db.create_all()
        _seed_default_data()

    return app


def _seed_default_data():
    from models import Admin, Announcement
    # Create default admin if none exists
    if not Admin.query.first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # Seed sample announcements
    if not Announcement.query.first():
        announcements = [
            Announcement(
                title='Admissions Open 2024-25',
                content='Applications for LKG to Class X are now open. Apply before March 31st.',
                active=True
            ),
            Announcement(
                title='Annual Day Celebration',
                content='Annual Day will be celebrated on February 15th. All parents are invited.',
                active=True
            ),
            Announcement(
                title='Republic Day Function',
                content='Republic Day celebration at school ground on January 26th at 9:00 AM.',
                active=True
            ),
        ]
        db.session.add_all(announcements)

    db.session.commit()


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=8080)
