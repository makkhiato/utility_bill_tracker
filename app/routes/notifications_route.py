from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Notification
from app.utils.auth import get_current_user
from app.extensions import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notification', methods=['GET'])
@jwt_required(refresh=False)
def get_notifications():
    user = get_current_user()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()

    result = []
    for notif in notifications:
        result.append({
            'id':notif.id,
            'message': notif.message,
            'created_at': notif.created_at.isoformat(),
            'is_seen': notif.is_seen
        })

    return jsonify(result), 200

@notification_bp.route('/notification/<int:notification_id>/seen',methods=['PUT'])
@jwt_required(refresh=False)
def mark_as_seen(notification_id):
    user = get_current_user()
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()

    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    notification.is_seen = True
    db.session.commit()

    return jsonify({'message': 'Notification marked as seen'}), 200

@notification_bp.route('/notification/<int:notification_id>', methods=['DELETE'])
@jwt_required(refresh=False)
def delete_notification(notification_id):
    user = get_current_user()
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()

    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    db.session.delete(notification)
    db.session.commit()

    return jsonify({'message': 'Notification deleted'}), 200