from flask import Blueprint, jsonify
from models import Announcement, GalleryImage

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/announcements')
def get_announcements():
    announcements = Announcement.query.filter_by(active=True).order_by(Announcement.date.desc()).all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'content': a.content,
        'date': a.date.strftime('%d %b %Y'),
    } for a in announcements])


@api_bp.route('/gallery')
def get_gallery():
    images = GalleryImage.query.order_by(GalleryImage.upload_date.desc()).all()
    return jsonify([{
        'id': img.id,
        'filename': img.filename,
        'caption': img.caption,
        'category': img.category,
    } for img in images])
