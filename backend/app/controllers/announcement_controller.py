from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.announcement_model import Announcement
from app.models.user_model import User
from app.models.course_model import Course
from datetime import datetime


def get_announcements():
    """Get announcements for current user (student sees their enrolled courses + global)"""
    user_id = int(get_jwt_identity())
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get filter parameters
        course_id = request.args.get('course_id', type=int)
        
        # Base query - only active announcements
        query = Announcement.query.filter_by(is_active=True)
        
        if user.role == 'student':
            # Students see: global announcements + announcements from enrolled courses
            enrolled_course_ids = [e.course_id for e in user.enrollments if e.status == 'active']
            query = query.filter(
                db.or_(
                    Announcement.course_id.is_(None),  # Global announcements
                    Announcement.course_id.in_(enrolled_course_ids)  # Enrolled courses
                )
            )
        elif course_id:
            # Teachers/Admins can filter by course
            query = query.filter_by(course_id=course_id)
        
        announcements = query.order_by(Announcement.created_at.desc()).all()
        
        return jsonify([{
            'id': a.id,
            'course_id': a.course_id,
            'course_name': a.course.title if a.course else 'All Courses',
            'title': a.title,
            'content': a.content,
            'created_by': a.creator.full_name if a.creator else 'System',
            'created_at': a.created_at.isoformat() if a.created_at else '',
            'priority': a.priority,
            'is_active': a.is_active
        } for a in announcements])
    except Exception as e:
        print(f"[Error] Failed to get announcements: {e}")
        return jsonify({'error': str(e)}), 500


def create_announcement():
    """Create new announcement (Teacher/Admin only)"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        # Validate user role
        user = User.query.get(user_id)
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Create announcement
        announcement = Announcement(
            course_id=data.get('course_id'),
            title=data['title'],
            content=data['content'],
            created_by=user_id,
            priority=data.get('priority', 'normal')
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement created successfully',
            'id': announcement.id
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"[Error] Failed to create announcement: {e}")
        return jsonify({'error': str(e)}), 500


def update_announcement(announcement_id):
    """Update announcement (Teacher/Admin only)"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        user = User.query.get(user_id)
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Only creator or admin can update
        if announcement.created_by != user_id and user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update fields
        if 'title' in data:
            announcement.title = data['title']
        if 'content' in data:
            announcement.content = data['content']
        if 'priority' in data:
            announcement.priority = data['priority']
        if 'is_active' in data:
            announcement.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({'message': 'Announcement updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"[Error] Failed to update announcement: {e}")
        return jsonify({'error': str(e)}), 500


def delete_announcement(announcement_id):
    """Delete announcement (Teacher/Admin only)"""
    user_id = int(get_jwt_identity())
    
    try:
        user = User.query.get(user_id)
        if not user or user.role not in ['teacher', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Only creator or admin can delete
        if announcement.created_by != user_id and user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(announcement)
        db.session.commit()
        
        return jsonify({'message': 'Announcement deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"[Error] Failed to delete announcement: {e}")
        return jsonify({'error': str(e)}), 500


def get_announcement_detail(announcement_id):
    """Get single announcement details"""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        return jsonify({
            'id': announcement.id,
            'course_id': announcement.course_id,
            'course_name': announcement.course.title if announcement.course else 'All Courses',
            'title': announcement.title,
            'content': announcement.content,
            'created_by': announcement.creator.full_name if announcement.creator else 'System',
            'created_at': announcement.created_at.isoformat() if announcement.created_at else '',
            'priority': announcement.priority,
            'is_active': announcement.is_active
        })
    except Exception as e:
        print(f"[Error] Failed to get announcement: {e}")
        return jsonify({'error': str(e)}), 500
