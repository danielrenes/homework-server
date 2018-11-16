from datetime import datetime

from sqlalchemy.exc import IntegrityError

from tests import BaseTest

from homework_server import db
from homework_server.models import Administrator, Course, Homework, Solution, Student, Teacher

class ModelsTest(BaseTest):
    def test_administrator(self):
        # create invalid admin
        admin = Administrator()
        db.session.add(admin)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # create valid admin
        admin.from_dict({
            'name': 'admin',
            'username': 'admin',
            'password': 'admin'
        })
        db.session.add(admin)
        db.session.commit()

        # check data
        self.assertEquals(len(Administrator.query.all()), 1)
        self.assertIsNotNone(admin.id)
        self.assertNotEquals(admin.password_hash, 'admin')
        self.assertEquals(admin.type, 'administrators')
        d = admin.to_dict()
        self.assertIsNotNone(d['id'])
        self.assertEquals(d['username'], 'admin')
        self.assertEquals(d['name'], 'admin')

        # try to create admin with the same username
        admin2 = Administrator()
        admin2.from_dict({
            'name': 'admin2',
            'username': 'admin',
            'password': 'admin2'
        })
        db.session.add(admin2)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_teacher(self):
        # create invalid teacher
        teacher = Teacher()
        db.session.add(teacher)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # create valid teacher
        teacher.from_dict({
            'name': 'teacher',
            'username': 'teacher',
            'password': 'teacher'
        })
        db.session.add(teacher)
        db.session.commit()

        # check data
        self.assertEquals(len(Teacher.query.all()), 1)
        self.assertIsNotNone(teacher.id)
        self.assertNotEquals(teacher.password_hash, 'teacher')
        self.assertEquals(teacher.type, 'teachers')
        d = teacher.to_dict()
        self.assertIsNotNone(d['id'])
        self.assertEquals(d['username'], 'teacher')
        self.assertEquals(d['name'], 'teacher')

        # try to create teacher with the same username
        teacher2 = Teacher()
        teacher2.from_dict({
            'name': 'teacher2',
            'username': 'teacher',
            'password': 'teacher2'
        })
        db.session.add(teacher2)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_student(self):
        # create invalid student
        student = Student()
        db.session.add(student)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # create valid student
        student.from_dict({
            'name': 'student',
            'username': 'student',
            'password': 'student'
        })
        db.session.add(student)
        db.session.commit()

        # check data
        self.assertEquals(len(Student.query.all()), 1)
        self.assertIsNotNone(student.id)
        self.assertNotEquals(student.password_hash, 'student')
        self.assertEquals(student.type, 'students')
        d = student.to_dict()
        self.assertIsNotNone(d['id'])
        self.assertEquals(d['username'], 'student')
        self.assertEquals(d['name'], 'student')

        # try to create student with the same username
        student2 = Student()
        student2.from_dict({
            'name': 'student2',
            'username': 'student',
            'password': 'student2'
        })
        db.session.add(student2)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # create a teacher
        teacher = Teacher()
        teacher.from_dict({
            'name': 'teacher',
            'username': 'teacher',
            'password': 'teacher'
        })
        db.session.add(teacher)
        db.session.commit()

        # create a course and add student to it
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = teacher.id
        course.students.append(student)
        db.session.add(course)
        db.session.commit()

        # check if student has one course
        self.assertEquals(len(student.courses), 1)

        # create a homework and add student to it
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': datetime.utcnow(),
            'headcount': 2,
            'self_assignable': True
        })
        homework.course_id = course.id
        homework.students.append(student)
        db.session.add(homework)
        db.session.commit()

        # check if student has one homework
        self.assertEquals(len(student.homeworks), 1)

    def test_course(self):
        # create invalid course
        course = Course()
        db.session.add(course)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # try to create course without a teacher
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        db.session.add(course)

        self.assertIsNone(course.teacher_id)

        # create a teacher
        teacher = Teacher()
        teacher.from_dict({
            'name': 'teacher',
            'username': 'teacher',
            'password': 'teacher'
        })
        db.session.add(teacher)
        db.session.commit()

        # add teacher to course
        course.teacher_id = teacher.id
        db.session.add(course)
        db.session.commit()

        # check data
        self.assertEquals(len(Course.query.all()), 1)
        self.assertIsNotNone(course.id)
        self.assertEquals(course.teacher_id, teacher.id)
        d = course.to_dict()
        self.assertIsNotNone(d['id'])
        self.assertEquals(d['name'], 'course')
        self.assertEquals(d['description'], 'course')
        self.assertEquals(d['teacher'], 'teacher')

        # try to create course with the same name
        course2 = Course()
        course2.from_dict({
            'name': 'course',
            'description': 'course2'
        })
        course2.teacher_id = teacher.id
        db.session.add(course2)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_homework(self):
        # create invalid homework
        homework = Homework()
        db.session.add(homework)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # try to create homework without a course
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-10-30 10:20:32',
            'headcount': 2,
            'self_assignable': True
        })
        db.session.add(homework)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # create a teacher
        teacher = Teacher()
        teacher.from_dict({
            'name': 'teacher',
            'username': 'teacher',
            'password': 'teacher'
        })
        db.session.add(teacher)
        db.session.commit()

        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = teacher.id
        db.session.add(course)
        db.session.commit()

        # add course to homework
        homework.course_id = course.id
        db.session.add(homework)
        db.session.commit()

        # check data
        self.assertEquals(len(Homework.query.all()), 1)
        self.assertIsNotNone(homework.id)
        self.assertEquals(homework.course_id, course.id)
        d = homework.to_dict()
        self.assertIsNotNone(d['id'])
        self.assertEquals(d['name'], 'homework')
        self.assertEquals(d['description'], 'homework')
        self.assertEquals(d['deadline'], '2018-10-30 10:20:32')
        self.assertEquals(d['headcount'], 2)
        self.assertTrue(d['self_assignable'])
        self.assertEquals(d['course'], 'course')

        # try to create homework with the same name
        homework2 = Homework()
        homework2.from_dict({
            'name': 'homework',
            'description': 'homework2',
            'deadline': datetime.utcnow(),
            'headcount': 3,
            'self_assignable': False
        })
        homework2.course_id = course.id
        db.session.add(homework2)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

    def test_solution(self):
        # create invalid solution
        solution = Solution()
        db.session.add(solution)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # try to create solution without file_path
        solution.from_dict({
            'status': 'status'
        })
        db.session.add(solution)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # try to create solution without a homework
        solution.file_path = 'file_path'
        db.session.add(solution)
        self.assertRaises(IntegrityError, db.session.commit)
        db.session.rollback()

        # create a teacher
        teacher = Teacher()
        teacher.from_dict({
            'name': 'teacher',
            'username': 'teacher',
            'password': 'teacher'
        })
        db.session.add(teacher)
        db.session.commit()

        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = teacher.id
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-10-30 10:20:32',
            'headcount': 2,
            'self_assignable': True
        })
        homework.course_id = course.id
        db.session.add(homework)
        db.session.commit()

        # add homework to solution
        solution.homework_id = homework.id
        db.session.add(solution)
        db.session.commit()

        # check data
        submitted_at = datetime.utcnow()
        self.assertEquals(len(Solution.query.all()), 1)
        self.assertIsNotNone(solution.id)
        self.assertEquals(solution.homework_id, homework.id)
        d = solution.to_dict()
        self.assertIsNotNone(d['id'])
        self.assertEquals(sorted(d.keys()), ['id', 'status', 'submitted_at'])
        self.assertEquals(d['status'], 'status')
        self.assertTrue(abs((submitted_at - datetime.strptime(d['submitted_at'], '%Y-%m-%d %H:%M:%S')).seconds) < 1)