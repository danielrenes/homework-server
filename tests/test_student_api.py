from datetime import datetime
import json
from io import BytesIO
import shutil

from tests import BaseApiTest

from homework_server import db
from homework_server.models import Course, Homework, Solution, Student

class StudentApiTest(BaseApiTest):
    def test_get_applied_courses(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.get('/api/v1/student/courses', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get('/api/v1/student/courses', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['courses', 'next', 'prev']))
        self.assertEquals(len(data['courses']), 1)
        self.assertTrue(all(item in data['courses'][0] for item in ['name', 'description', 'teacher']))
        self.assertEquals(data['courses'][0], {'name': 'course', 'description': 'course', 'teacher': 'teacher'})

    def test_apply_for_course(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        db.session.add(course)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.post(f'/api/v1/student/course/{course.id}', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post(f'/api/v1/student/course/{course.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check data
        course = Course.query.filter_by(name='course').first()
        self.assertIsNotNone(course)
        self.assertEquals(course.name, 'course')
        self.assertEquals(course.description, 'course')
        self.assertEquals(course.teacher_id, self.teacher.id)
        self.assertEquals(len(course.students), 1)
        self.assertEquals(course.students[0].name, 'student')

    def test_abandon_course(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.delete(f'/api/v1/student/course/{course.id}', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.delete(f'/api/v1/student/course/{course.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check data
        course = Course.query.filter_by(name='course').first()
        self.assertIsNotNone(course)
        self.assertEquals(course.name, 'course')
        self.assertEquals(course.description, 'course')
        self.assertEquals(course.teacher_id, self.teacher.id)
        self.assertEquals(len(course.students), 0)

    def test_get_homeworks_for_course(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        db.session.add(homework)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.get(f'/api/v1/student/course/{course.id}/homeworks', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/student/course/{course.id}/homeworks', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['homeworks', 'next', 'prev']))
        self.assertEquals(len(data['homeworks']), 1)
        self.assertTrue(all(item in data['homeworks'][0] for item in \
            ['name', 'description', 'deadline', 'headcount', 'self_assignable', 'course']))
        self.assertEquals(data['homeworks'][0], {'name': 'homework', 'description': 'homework', \
            'deadline': '2018-11-08 08:48:11', 'headcount': 4, 'self_assignable': False, 'course': 'course'})

    def test_apply_for_homework(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        db.session.add(homework)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.post(f'/api/v1/student/homework/{homework.id}', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post(f'/api/v1/student/homework/{homework.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check data
        homework = Homework.query.filter_by(name='homework').first()
        self.assertIsNotNone(homework)
        self.assertEquals(homework.name, 'homework')
        self.assertEquals(homework.description, 'homework')
        self.assertEquals(homework.deadline, datetime.strptime('2018-11-08 08:48:11', '%Y-%m-%d %H:%M:%S'))
        self.assertEquals(homework.headcount, 4)
        self.assertEquals(homework.self_assignable, False)
        self.assertEquals(homework.course_id, course.id)
        self.assertEquals(len(homework.students), 1)
        self.assertEquals(homework.students[0].name, 'student')

    def test_abandon_homework(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        homework.students.append(self.student)
        db.session.add(homework)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.delete(f'/api/v1/student/homework/{homework.id}', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.delete(f'/api/v1/student/homework/{homework.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check data
        homework = Homework.query.filter_by(name='homework').first()
        self.assertIsNotNone(homework)
        self.assertEquals(homework.name, 'homework')
        self.assertEquals(homework.description, 'homework')
        self.assertEquals(homework.deadline, datetime.strptime('2018-11-08 08:48:11', '%Y-%m-%d %H:%M:%S'))
        self.assertEquals(homework.headcount, 4)
        self.assertEquals(homework.self_assignable, False)
        self.assertEquals(homework.course_id, course.id)
        self.assertEquals(len(homework.students), 0)

    def test_submit_solution(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        homework.students.append(self.student)
        db.session.add(homework)
        db.session.commit()

        # create another student
        student2 = Student()
        student2.from_dict({
            'name': 'student2',
            'username': 'student2'
        })
        student2.set_password('student2')
        db.session.add(student2)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.post(f'/api/v1/student/homework/{homework.id}/submit', headers=self.basic_auth_header('student', 'student'), \
                              content_type='multipart/form-data', data={'file': (BytesIO(b'tmp'), 'tmp.txt')})
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post(f'/api/v1/student/homework/{homework.id}/submit', headers=self.token_auth_header(token), \
                              content_type='multipart/form-data', data={'file': (BytesIO(b'tmp'), 'tmp.txt')})
        self.assertEquals(rv.status_code, 200)

        submitted_at = datetime.utcnow()

        # check data
        solutions = Solution.query.all()
        self.assertEquals(len(solutions), 1)
        solution = Solution.query.filter_by(status=None).first()
        self.assertTrue(all(item in solution.to_dict() for item in ['status', 'submitted_at']))
        self.assertIsNone(solution.status)
        self.assertTrue(abs((submitted_at - solution.submitted_at).seconds) < 1)
        self.assertIsNotNone(solution.file_path)

        # get token for student2
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student2', 'student2'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with student2's token
        rv = self.client.post(f'/api/v1/student/homework/{homework.id}/submit', headers=self.token_auth_header(token), \
                              content_type='multipart/form-data', data={'file': (BytesIO(b'tmp'), 'tmp.txt')})
        self.assertEquals(rv.status_code, 403)

        # clean up the upload folder
        shutil.rmtree(self.app.config['UPLOAD_FOLDER'])

    def test_get_homeworks(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        course.students.append(self.student)
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        homework.students.append(self.student)
        db.session.add(homework)
        db.session.commit()

        # create a course2
        course2 = Course()
        course2.from_dict({
            'name': 'course2',
            'description': 'course2'
        })
        course2.teacher_id = self.teacher.id
        course2.students.append(self.student)
        db.session.add(course2)
        db.session.commit()

        # create a homework2
        homework2 = Homework()
        homework2.from_dict({
            'name': 'homework2',
            'description': 'homework2',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework2.course_id = course2.id
        homework2.students.append(self.student)
        db.session.add(homework2)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.get(f'/api/v1/student/homeworks', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/student/homeworks', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['homeworks', 'next', 'prev']))
        self.assertEquals(len(data['homeworks']), 2)
        self.assertTrue(all(item in data['homeworks'][0] for item in \
            ['name', 'description', 'deadline', 'headcount', 'self_assignable', 'course']))
        self.assertEquals(data['homeworks'][0], {'name': 'homework', 'description': 'homework', \
            'deadline': '2018-11-08 08:48:11', 'headcount': 4, 'self_assignable': False, 'course': 'course'})
        self.assertTrue(all(item in data['homeworks'][1] for item in \
            ['name', 'description', 'deadline', 'headcount', 'self_assignable', 'course']))
        self.assertEquals(data['homeworks'][1], {'name': 'homework2', 'description': 'homework2', \
            'deadline': '2018-11-08 08:48:11', 'headcount': 4, 'self_assignable': False, 'course': 'course2'})

    def test_get_solutions(self):
        # create a homework
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        homework.students.append(self.student)
        db.session.add(homework)
        db.session.commit()

        # create a solution
        solution = Solution()
        solution.from_dict({
            'status': 'status'
        })
        solution.file_path = 'f'
        solution.homework_id = homework.id
        db.session.add(solution)
        db.session.commit()

        submitted_at = datetime.utcnow()

        # try to access with basic authentication
        rv = self.client.get(f'/api/v1/student/homework/{homework.id}/solutions', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/student/homework/{homework.id}/solutions', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['solutions', 'next', 'prev']))
        self.assertEquals(len(data['solutions']), 1)
        self.assertTrue(all(item in data['solutions'][0] for item in ['status', 'submitted_at']))
        self.assertEquals(data['solutions'][0]['status'], 'status')
        self.assertTrue(abs((submitted_at - datetime.strptime(data['solutions'][0]['submitted_at'], '%Y-%m-%d %H:%M:%S')).seconds) < 1)

    def test_get_solution(self):
        # create a homework
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        db.session.add(course)
        db.session.commit()

        # create a homework
        homework = Homework()
        homework.from_dict({
            'name': 'homework',
            'description': 'homework',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        })
        homework.course_id = course.id
        homework.students.append(self.student)
        db.session.add(homework)
        db.session.commit()

        # create a solution
        solution = Solution()
        solution.from_dict({
            'status': 'status'
        })
        solution.file_path = 'f'
        solution.homework_id = homework.id
        db.session.add(solution)
        db.session.commit()

        submitted_at = datetime.utcnow()

        # try to access with basic authentication
        rv = self.client.get(f'/api/v1/student/solution/{solution.id}', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('student', 'student'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/student/solution/{solution.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue('solution' in data)
        self.assertTrue(all(item in data['solution'] for item in ['status', 'submitted_at']))
        self.assertEquals(data['solution']['status'], 'status')
        self.assertTrue(abs((submitted_at - datetime.strptime(data['solution']['submitted_at'], '%Y-%m-%d %H:%M:%S')).seconds) < 1)