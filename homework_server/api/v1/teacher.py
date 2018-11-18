from flask import Blueprint, current_app, g, jsonify, request, url_for

from .auth import check_user, token_auth
from homework_server import db
from homework_server.models import Course, Homework, Solution, Student, Teacher
from homework_server.pagination import PaginatedQuery

teacher_api = Blueprint('teacher_api', __name__)

@teacher_api.route('/courses', methods=['GET'])
@token_auth.login_required
@check_user(Teacher)
def get_courses():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    paginate = PaginatedQuery(
        Course.query.order_by(Course.name),
        Course.query.count(),
        'teacher_api.get_courses',
        'courses',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@teacher_api.route('/courses', methods=['POST'])
@token_auth.login_required
@check_user(Teacher)
def create_course():
    data = request.get_json() or {}
    if not all(field in data for field in ['name', 'description']):
        return '', 400
    course = Course()
    course.teacher_id = g.current_user.id
    course.from_dict(data)
    db.session.add(course)
    db.session.commit()
    return '', 200

@teacher_api.route('/course/<int:id>', methods=['DELETE'])
@token_auth.login_required
@check_user(Teacher)
def remove_course(id):
    course = Course.query.filter_by(id=id).first()
    if course is None:
        return '', 410
    db.session.delete(course)
    db.session.commit()
    return '', 200

@teacher_api.route('/course/<int:id>/homeworks', methods=['GET'])
@token_auth.login_required
@check_user(Teacher)
def get_homeworks(id):
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Homework.query.join(Course, Course.id==Homework.course_id) \
                               .filter(Course.id==id)
    paginate = PaginatedQuery(
        base_query.order_by(Homework.name),
        base_query.count(),
        'teacher_api.get_homeworks',
        'homeworks',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@teacher_api.route('/course/<int:id>/homeworks', methods=['POST'])
@token_auth.login_required
@check_user(Teacher)
def create_homework(id):
    data = request.get_json() or {}
    if not all(field in data for field in ['name', 'description', 'deadline', 'headcount', 'self_assignable']):
        return '', 400
    homework = Homework()
    homework.from_dict(data)
    homework.course_id = id
    db.session.add(homework)
    db.session.commit()
    return '', 200

@teacher_api.route('/homework/<int:id>', methods=['PUT'])
@token_auth.login_required
@check_user(Teacher)
def modify_homework(id):
    data = request.get_json() or {}
    if not any(field in data for field in ['name', 'description', 'deadline', 'headcount', 'self_assignable', 'students']):
        return '', 400
    homework = Homework.query.filter_by(id=id).first()
    if homework is None:
        return '', 410
    homework.from_dict(data)
    db.session.commit()
    return '', 200

@teacher_api.route('/homework/<int:id>', methods=['DELETE'])
@token_auth.login_required
@check_user(Teacher)
def remove_homework(id):
    homework = Homework.query.filter_by(id=id).first()
    if homework is None:
        return '', 410
    db.session.delete(homework)
    db.session.commit()
    return '', 200

@teacher_api.route('/course/<int:id>/students', methods=['GET'])
@token_auth.login_required
@check_user(Teacher)
def get_students(id):
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Student.query.join(Course, Student.courses)
    paginate = PaginatedQuery(
        base_query.order_by(Student.name),
        base_query.count(),
        'teacher_api.get_students',
        'students',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@teacher_api.route('/homework/<int:id>/solutions', methods=['GET'])
@token_auth.login_required
@check_user(Teacher)
def get_solutions(id):
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    base_query = Solution.query.join(Homework, Homework.id==Solution.homework_id) \
                               .filter(Homework.id==id)
    paginate = PaginatedQuery(
        base_query.order_by(Solution.submitted_at.desc()),
        base_query.count(),
        'teacher_api.get_solutions',
        'solutions',
        start,
        limit
    )
    result = paginate.execute()
    return jsonify(result)

@teacher_api.route('/solution/<int:id>', methods=['GET'])
@token_auth.login_required
@check_user(Teacher)
def get_solution(id):
    solution = Solution.query.filter_by(id=id).first()
    if solution is None:
        return '', 410
    return jsonify({
        'solution': solution.to_dict()
    })

@teacher_api.route('/solution/<int:id>', methods=['PUT'])
@token_auth.login_required
@check_user(Teacher)
def modify_solution(id):
    data = request.get_json() or {}
    if 'status' not in data:
        return '', 400
    solution = Solution.query.filter_by(id=id).first()
    if solution is None:
        return '', 410
    solution.from_dict(data)
    db.session.commit()
    return '', 200