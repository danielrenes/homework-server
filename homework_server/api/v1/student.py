import os

from flask import Blueprint, current_app, g, jsonify, request, url_for
from werkzeug.utils import secure_filename

from .auth import check_user, token_auth
from homework_server import db
from homework_server.models import Course, Homework, Solution, Student

student_api = Blueprint('student_api', __name__)

@student_api.route('/courses', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_applied_courses():
    start = request.args.get('start', 0)
    limit = request.args.get('limit', 25)
    courses = Course.query.join(Student, Course.students) \
                          .filter(Student.id==g.current_user.id) \
                          .order_by(Course.name) \
                          .paginate(start, limit, False) \
                          .items
    url_next = url_for('student_api.get_applied_courses', id=id, **{'start': start + limit + 1, 'limit': limit}) \
                if len(courses) > (start + limit) else None
    url_prev = url_for('student_api.get_applied_courses', id=id, **{'start': start - limit - 1, 'limit': limit}) \
                if (start - limit - 1) > 0 else None 
    return jsonify({
        'courses': [course.to_dict() for course in courses],
        'next': url_next,
        'prev': url_prev
    })

@student_api.route('/course/<int:id>', methods=['POST'])
@token_auth.login_required
@check_user(Student)
def apply_for_course():
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return '', 410
    course.students.append(g.current_user)
    db.session.commit()
    return '', 200

@student_api.route('/course/<int:id>', methods=['DELETE'])
@token_auth.login_required
@check_user(Student)
def abandon_course(id):
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return '', 410
    if g.current_user not in course.students:
        return '', 304
    course.students.remove(g.current_user)
    db.session.commit()
    return '', 200

@student_api.route('/course/<int:id>/homeworks', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_homeworks_for_course(id):
    start = request.args.get('start', 0)
    limit = request.args.get('limit', 25)
    homeworks = Homework.query.join(Course, Course.id==Homework.course_id) \
                              .filter(Course.id==id) \
                              .order_by(Homework.name) \
                              .paginate(start, limit, False) \
                              .items
    url_next = url_for('student_api.get_homeworks_for_course', id=id, **{'start': start + limit + 1, 'limit': limit}) \
                if len(homeworks) > (start + limit) else None
    url_prev = url_for('student_api.get_homeworks_for_course', id=id, **{'start': start - limit - 1, 'limit': limit}) \
                if (start - limit - 1) > 0 else None 
    return jsonify({
        'homeworks': [homework.to_dict() for homework in homeworks],
        'next': url_next,
        'prev': url_prev
    })

@student_api.route('/homework/<int:id>', methods=['POST'])
@token_auth.login_required
@check_user(Student)
def apply_for_homework(id):
    homework = Homework.query.filter_by(id=id).first()
    if homework is None:
        return '', 410
    homework.students.append(g.current_user)
    db.session.commit()
    return '', 200

@student_api.route('/homework/<int:id>', methods=['DELETE'])
@token_auth.login_required
@check_user(Student)
def abandon_homework(id):
    homework = Homework.query.filter_by(id=id).first()
    if homework is None:
        return '', 410
    if g.current_user not in homework.students:
        return '', 304
    homework.students.remove(g.current_user)
    db.session.commit()
    return '', 200

@student_api.route('/homework/<int:id>/submit', methods=['POST'])
@token_auth.login_required
@check_user(Student)
def submit_solution(id):
    if 'file' not in request.files:
        return '', 400
    homework = Homework.query.filter_by(id=id).first()
    if homework is None:
        return '', 410
    course = Course.query.join(Homework, Homework.course_id==Course.id) \
                         .filter(Homework.id==id) \
                         .first()
    if course is None:
        return '', 410
    course_folder = course.name
    homework_folder = homework.name
    filename = secure_filename(request.files['file'].filename)
    homework.file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], course_folder, homework_folder, filename)
    request.files['file'].save(homework.file_path)
    db.session.commit()

@student_api.route('/homeworks', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_homeworks():
    start = request.args.get('start', 0)
    limit = request.args.get('limit', 25)
    homeworks = Homework.query.join(Student, Homework.students) \
                              .filter(Student.id==g.current_user.id) \
                              .order_by(Homework.name) \
                              .paginate(start, limit, False) \
                              .items
    url_next = url_for('student_api.get_homeworks', id=id, **{'start': start + limit + 1, 'limit': limit}) \
                if len(homeworks) > (start + limit) else None
    url_prev = url_for('student_api.get_homeworks', id=id, **{'start': start - limit - 1, 'limit': limit}) \
                if (start - limit - 1) > 0 else None 
    return jsonify({
        'homeworks': [homework.to_dict() for homework in homeworks],
        'next': url_next,
        'prev': url_prev
    })

@student_api.route('/homework/<int:id>/solutions', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_solutions(id):
    start = request.args.get('start', 0)
    limit = request.args.get('limit', 25)
    solutions = Solution.query.join(Homework, Homework.id==Solution.homework_id) \
                              .join(Student, Homework.students) \
                              .filter(Student.id==g.current_user.id, Homework.id==id) \
                              .order_by(Homework.name) \
                              .paginate(start, limit, False) \
                              .items
    url_next = url_for('student_api.get_solutions', id=id, **{'start': start + limit + 1, 'limit': limit}) \
                if len(solutions) > (start + limit) else None
    url_prev = url_for('student_api.get_solutions', id=id, **{'start': start - limit - 1, 'limit': limit}) \
                if (start - limit - 1) > 0 else None 
    return jsonify({
        'solutions': [solution.to_dict() for solution in solutions],
        'next': url_next,
        'prev': url_prev
    })

@student_api.route('/solution/<int:id>', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_solution(id):
    solution = Solution.query.filter_by(id=id).first()
    if solution is None:
        return '', 410
    return jsonify({
        'solution': solution.to_dict()
    })