import os

from flask import Blueprint, current_app, g, jsonify, request, url_for
from werkzeug.utils import secure_filename

from .auth import check_user, token_auth
from homework_server import db
from homework_server.models import Course, Homework, Solution, Student
from homework_server.pagination import PaginatedQuery

student_api = Blueprint('student_api', __name__)

@student_api.route('/courses/all', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_courses():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    paginate = PaginatedQuery(
        Course.query.order_by(Course.name),
        Course.query.count(),
        'student_api.get_courses',
        'courses',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@student_api.route('/courses', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_applied_courses():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Course.query.join(Student, Course.students) \
                             .filter(Student.id==g.current_user.id)
    paginate = PaginatedQuery(
        base_query.order_by(Course.name),
        base_query.count(),
        'student_api.get_applied_courses',
        'courses',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@student_api.route('/course/<int:id>', methods=['POST'])
@token_auth.login_required
@check_user(Student)
def apply_for_course(id):
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return '', 410
    if g.current_user in course.students:
        return '', 304
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
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Homework.query.join(Course, Course.id==Homework.course_id) \
                               .filter(Course.id==id)
    paginate = PaginatedQuery(
        base_query.order_by(Homework.name),
        base_query.count(),
        'student_api.get_homeworks_for_course',
        'homeworks',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@student_api.route('/homework/<int:id>', methods=['POST'])
@token_auth.login_required
@check_user(Student)
def apply_for_homework(id):
    homework = Homework.query.filter_by(id=id).first()
    if homework is None:
        return '', 410
    if not homework.self_assignable:
        return '', 409
    if g.current_user in homework.students:
        return '', 304
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
    student = Student.query.filter_by(id=g.current_user.id).first()
    if student not in homework.students:
        return '', 403
    course = Course.query.join(Homework, Homework.course_id==Course.id) \
                         .filter(Homework.id==id) \
                         .first()
    if course is None:
        return '', 410
    solution = Solution()
    solution.homework_id = homework.id
    course_folder = course.name
    homework_folder = homework.name
    filename = secure_filename(request.files['file'].filename)
    solution.file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], course_folder, homework_folder, filename)
    parent_dir = os.path.abspath(os.path.join(solution.file_path, os.pardir))
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    request.files['file'].save(solution.file_path)
    db.session.add(solution)
    db.session.commit()
    return '', 200

@student_api.route('/homeworks', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_homeworks():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Homework.query.join(Student, Homework.students) \
                               .filter(Student.id==g.current_user.id)
    paginate = PaginatedQuery(
        base_query.order_by(Homework.name),
        base_query.count(),
        'student_api.get_homeworks',
        'homeworks',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@student_api.route('/homework/<int:id>/solutions', methods=['GET'])
@token_auth.login_required
@check_user(Student)
def get_solutions(id):
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Solution.query.join(Homework, Homework.id==Solution.homework_id) \
                              .join(Student, Homework.students) \
                              .filter(Student.id==g.current_user.id, Homework.id==id)
    paginate = PaginatedQuery(
        base_query.order_by(Homework.name),
        base_query.count(),
        'student_api.get_solutions',
        'solutions',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

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
