from datetime import datetime
import json

from tests import BaseApiTest

from homework_server import db
from homework_server.models import Course, Homework, Solution, Teacher

class TeacherApiTest(BaseApiTest):
    def test_get_courses(self):
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
        rv = self.client.get('/api/v1/teacher/courses', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get('/api/v1/teacher/courses', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['courses', 'next', 'prev']))
        self.assertEquals(len(data['courses']), 1)
        self.assertTrue(all(item in data['courses'][0] for item in ['id', 'name', 'description', 'teacher']))
        self.assertIsNotNone(data['courses'][0]['id'])
        self.assertEquals(data['courses'][0]['name'], 'course')
        self.assertEquals(data['courses'][0]['description'], 'course')
        self.assertEquals(data['courses'][0]['teacher'], 'teacher')

    def test_create_course(self):
        # try to access with basic authentication
        rv = self.client.post('/api/v1/teacher/courses', headers=self.basic_auth_header('teacher', 'teacher'), \
                              data=json.dumps({'name': 'f1', 'description': 'f2'}))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post('/api/v1/teacher/courses', headers=self.token_auth_header(token), \
                              data=json.dumps({'name': 'f1', 'description': 'f2'}))
        self.assertEquals(rv.status_code, 200)

        # check if course was created
        course = Course.query.filter_by(name='f1').first()
        self.assertIsNotNone(course)
        self.assertEquals(course.name, 'f1')
        self.assertEquals(course.description, 'f2')
        self.assertEquals(course.teacher_id, self.teacher.id)
        self.assertEquals(len(course.students), 0)

        # try to create course without all the necessary fields
        data = {
            'name': 'n',
            'description': 'd'
        }
        request_datas = self.insufficient_datas(data)
        for d in request_datas:
            rv = self.client.post('/api/v1/teacher/courses', headers=self.token_auth_header(token), data=json.dumps(d))
            self.assertEquals(rv.status_code, 400)

    def test_remove_course(self):
        # create a course
        course = Course()
        course.from_dict({
            'name': 'course',
            'description': 'course'
        })
        course.teacher_id = self.teacher.id
        db.session.add(course)
        db.session.commit()

        number_of_courses_before = len(Course.query.all())

        # try to access with basic authentication
        rv = self.client.delete(f'/api/v1/teacher/course/{course.id}', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.delete(f'/api/v1/teacher/course/{course.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        number_of_courses_after = len(Course.query.all())
        self.assertEquals(number_of_courses_before - number_of_courses_after, 1)

        # try to remove a nonexistent course
        rv = self.client.delete(f'/api/v1/teacher/course/{course.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 410)

    def test_get_homeworks(self):
        # create a course
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
        db.session.add(homework)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.get(f'/api/v1/teacher/course/{course.id}/homeworks', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/teacher/course/{course.id}/homeworks', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['homeworks', 'next', 'prev']))
        self.assertEquals(len(data['homeworks']), 1)
        self.assertTrue(all(item in data['homeworks'][0] for item in \
            ['id', 'name', 'description', 'deadline', 'headcount', 'self_assignable', 'course']))
        self.assertIsNotNone(data['homeworks'][0]['id'])
        self.assertEquals(data['homeworks'][0]['name'], 'homework')
        self.assertEquals(data['homeworks'][0]['description'], 'homework')
        self.assertEquals(data['homeworks'][0]['deadline'], '2018-11-08 08:48:11')
        self.assertEquals(data['homeworks'][0]['headcount'], 4)
        self.assertEquals(data['homeworks'][0]['self_assignable'], False)
        self.assertEquals(data['homeworks'][0]['course'], 'course')

    def test_create_homework(self):
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
        rv = self.client.post(f'/api/v1/teacher/course/{course.id}/homeworks', headers=self.basic_auth_header('teacher', 'teacher'), \
                              data=json.dumps({'name': 'f1', 'description': 'f2', 'deadline': '2018-11-08 08:48:11', \
                                               'headcount': 4, 'self_assignable': False, 'students': [self.student.id,]}))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post(f'/api/v1/teacher/course/{course.id}/homeworks', headers=self.token_auth_header(token), \
                              data=json.dumps({'name': 'f1', 'description': 'f2', 'deadline': '2018-11-08 08:48:11', \
                                               'headcount': 4, 'self_assignable': False, 'students': [self.student.id,]}))
        self.assertEquals(rv.status_code, 200)

        # check if homework was created
        homework = Homework.query.filter_by(name='f1').first()
        self.assertIsNotNone(homework)
        self.assertEquals(homework.name, 'f1')
        self.assertEquals(homework.description, 'f2')
        self.assertEquals(homework.deadline, datetime.strptime('2018-11-08 08:48:11', '%Y-%m-%d %H:%M:%S'))
        self.assertEquals(homework.headcount, 4)
        self.assertEquals(homework.self_assignable, False)
        self.assertEquals(homework.course_id, course.id)
        self.assertEquals(len(homework.students), 1)

        # try to create homework without all the necessary fields
        data = {
            'name': 'f1',
            'description': 'f2',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False
        }
        request_datas = self.insufficient_datas(data)
        for d in request_datas:
            rv = self.client.post(f'/api/v1/teacher/course/{course.id}/homeworks', \
                                  headers=self.token_auth_header(token), data=json.dumps(d))
            self.assertEquals(rv.status_code, 400)

    def test_modify_homeworks(self):
        # create a course
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
        db.session.add(homework)
        db.session.commit()

        # try to access with basic authentication
        rv = self.client.put(f'/api/v1/teacher/homework/{homework.id}', headers=self.basic_auth_header('teacher', 'teacher'), \
                             data=json.dumps({'name': 'f1', 'description': 'f2', 'deadline': '2018-11-08 08:48:11', \
                                              'headcount': 4, 'self_assignable': False}))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.put(f'/api/v1/teacher/homework/{homework.id}', headers=self.token_auth_header(token), \
                             data=json.dumps({'name': 'f1', 'description': 'f2', 'deadline': '2018-11-08 08:48:11', \
                                              'headcount': 4, 'self_assignable': False}))
        self.assertEquals(rv.status_code, 200)

        # check if homework was modified
        homework = Homework.query.filter_by(name='f1').first()
        self.assertIsNotNone(homework)
        self.assertEquals(homework.name, 'f1')
        self.assertEquals(homework.description, 'f2')
        self.assertEquals(homework.deadline, datetime.strptime('2018-11-08 08:48:11', '%Y-%m-%d %H:%M:%S'))
        self.assertEquals(homework.headcount, 4)
        self.assertEquals(homework.self_assignable, False)
        self.assertEquals(homework.course_id, course.id)
        self.assertEquals(len(homework.students), 0)

        # try to modify homework with any of the necessary fields
        data = {
            'name': 'f1',
            'description': 'f2',
            'deadline': '2018-11-08 08:48:11',
            'headcount': 4,
            'self_assignable': False,
            'students': [self.student.id,]
        }
        request_datas = self.insufficient_datas(data)
        for d in request_datas:
            rv = self.client.put(f'/api/v1/teacher/homework/{homework.id}', \
                                 headers=self.token_auth_header(token), data=json.dumps(d))
            self.assertEquals(rv.status_code, 200)

    def test_remove_homework(self):
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
        db.session.add(homework)
        db.session.commit()

        number_of_homeworks_before = len(Homework.query.all())

        # try to access with basic authentication
        rv = self.client.delete(f'/api/v1/teacher/homework/{homework.id}', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.delete(f'/api/v1/teacher/homework/{homework.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        number_of_homeworks_after = len(Homework.query.all())
        self.assertEquals(number_of_homeworks_before - number_of_homeworks_after, 1)

        # try to remove a nonexistent homework
        rv = self.client.delete(f'/api/v1/teacher/homework/{homework.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 410)

    def test_get_students(self):
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
        rv = self.client.get(f'/api/v1/teacher/course/{course.id}/students', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/teacher/course/{course.id}/students', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['students', 'next', 'prev']))
        self.assertEquals(len(data['students']), 1)
        self.assertTrue(all(item in data['students'][0] for item in ['id', 'name', 'username']))
        self.assertIsNotNone(data['students'][0]['id'])
        self.assertEquals(data['students'][0]['name'], 'student')
        self.assertEquals(data['students'][0]['username'], 'student')

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
        rv = self.client.get(f'/api/v1/teacher/homework/{homework.id}/solutions', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/teacher/homework/{homework.id}/solutions', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['solutions', 'next', 'prev']))
        self.assertEquals(len(data['solutions']), 1)
        self.assertTrue(all(item in data['solutions'][0] for item in ['id', 'status', 'submitted_at']))
        self.assertIsNotNone(data['solutions'][0]['id'])
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
        rv = self.client.get(f'/api/v1/teacher/solution/{solution.id}', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get(f'/api/v1/teacher/solution/{solution.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue('solution' in data)
        self.assertTrue(all(item in data['solution'] for item in ['id', 'status', 'submitted_at']))
        self.assertIsNotNone(data['solution']['id'])
        self.assertEquals(data['solution']['status'], 'status')
        self.assertTrue(abs((submitted_at - datetime.strptime(data['solution']['submitted_at'], '%Y-%m-%d %H:%M:%S')).seconds) < 1)

    def test_modify_solution(self):
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
        rv = self.client.put(f'/api/v1/teacher/solution/{solution.id}', headers=self.basic_auth_header('teacher', 'teacher'), \
                             data=json.dumps({'status': 'f1'}))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('teacher', 'teacher'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.put(f'/api/v1/teacher/solution/{solution.id}', headers=self.token_auth_header(token), \
                             data=json.dumps({'status': 'f1'}))
        self.assertEquals(rv.status_code, 200)

        # check if solution was modified
        solution = Solution.query.filter_by(status='f1').first()
        self.assertIsNotNone(solution)
        self.assertEquals(solution.status, 'f1')
        self.assertEquals(solution.file_path, 'f')

        # try to modify homework without all the necessary fields
        data = {
            'status': 'f1'
        }
        request_datas = self.insufficient_datas(data)
        for d in request_datas:
            rv = self.client.put(f'/api/v1/teacher/solution/{solution.id}', \
                                 headers=self.token_auth_header(token), data=json.dumps(d))
            self.assertEquals(rv.status_code, 400)