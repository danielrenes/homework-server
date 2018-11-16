from flask import Blueprint, jsonify, request, url_for

from .auth import check_user, token_auth
from homework_server import db
from homework_server.models import Administrator, Teacher, Student

admin_api = Blueprint('admin_api', __name__)

@admin_api.route('/teachers', methods=['GET'])
@token_auth.login_required
@check_user(Administrator)
def get_teachers():
    start = request.args.get('start', 0)
    limit = request.args.get('limit', 25)
    teachers = Teacher.query.order_by(Teacher.name).paginate(start, limit, False).items
    url_next = url_for('admin_api.get_teachers', **{'start': start + limit + 1, 'limit': limit}) \
                if len(teachers) > (start + limit) else None
    url_prev = url_for('admin_api.get_teachers', **{'start': start - limit - 1, 'limit': limit}) \
                if (start - limit - 1) > 0 else None
    return jsonify({
        'teachers': [teacher.to_dict() for teacher in teachers],
        'next': url_next,
        'prev': url_prev
    })

@admin_api.route('/teachers', methods=['POST'])
@token_auth.login_required
@check_user(Administrator)
def create_teacher():
    data = request.get_json() or {}
    if not all(field in data for field in ['name', 'username', 'password']):
        return '', 400
    teacher = Teacher()
    teacher.from_dict(data)
    db.session.add(teacher)
    db.session.commit()
    return '', 200

@admin_api.route('/teacher/<int:id>', methods=['DELETE'])
@token_auth.login_required
@check_user(Administrator)
def remove_teacher(id):
    teacher = Teacher.query.filter_by(id=id).first()
    if teacher is None:
        return '', 410
    db.session.delete(teacher)
    db.session.commit()
    return '', 200

@admin_api.route('/students', methods=['GET'])
@token_auth.login_required
@check_user(Administrator)
def get_students():
    start = request.args.get('start', 0)
    limit = request.args.get('limit', 25)
    students = Student.query.order_by(Student.name).paginate(start, limit, False).items
    url_next = url_for('admin_api.get_students', **{'start': start + limit + 1, 'limit': limit}) \
                if len(students) > (start + limit) else None
    url_prev = url_for('admin_api.get_students', **{'start': start - limit - 1, 'limit': limit}) \
                if (start - limit - 1) > 0 else None 
    return jsonify({
        'students': [student.to_dict() for student in students],
        'next': url_next,
        'prev': url_prev
    })

@admin_api.route('/students', methods=['POST'])
@token_auth.login_required
@check_user(Administrator)
def create_studetns():
    data = request.get_json() or {}
    if not all(field in data for field in ['name', 'username', 'password']):
        return '', 400
    student = Student()
    student.from_dict(data)
    db.session.add(student)
    db.session.commit()
    return '', 200

@admin_api.route('/student/<int:id>', methods=['DELETE'])
@token_auth.login_required
@check_user(Administrator)
def remove_student(id):
    student = Student.query.filter_by(id=id).first()
    if student is None:
        return '', 410
    db.session.delete(student)
    db.session.commit()
    return '', 200