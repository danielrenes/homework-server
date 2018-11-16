import json

from tests import BaseApiTest

from homework_server import db
from homework_server.models import Teacher, Student

class AdminApiTest(BaseApiTest):
    def test_get_teachers(self):
        # try to access with basic authentication
        rv = self.client.get('/api/v1/admin/teachers', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get('/api/v1/admin/teachers', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['teachers', 'next', 'prev']))
        self.assertEquals(len(data['teachers']), 1)
        self.assertTrue(all(item in data['teachers'][0] for item in ['id', 'name', 'username']))
        self.assertIsNotNone(data['teachers'][0]['id'])
        self.assertEquals(data['teachers'][0]['name'], 'teacher')
        self.assertEquals(data['teachers'][0]['username'], 'teacher')

    def test_create_teacher(self):
        # try to access with basic authentication
        rv = self.client.post('/api/v1/admin/teachers', headers=self.basic_auth_header('admin', 'admin'), \
                              data=json.dumps({'username': 'f1', 'name': 'f2', 'password': 'f3'}))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post('/api/v1/admin/teachers', headers=self.token_auth_header(token), \
                              data=json.dumps({'username': 'f1', 'name': 'f2', 'password': 'f3'}))
        self.assertEquals(rv.status_code, 200)

        # check if teacher was created
        teacher = Teacher.query.filter_by(username='f1').first()
        self.assertIsNotNone(teacher)
        self.assertEquals(teacher.username, 'f1')
        self.assertEquals(teacher.name, 'f2')
        self.assertIsNotNone(teacher.password_hash)
        self.assertNotEquals(teacher.password_hash, 'f3')

        # try to create teacher without all the necessary fields
        data = {
            'username': 'u',
            'name': 'n',
            'password': 'p'
        }
        request_datas = self.insufficient_datas(data)
        for d in request_datas:
            rv = self.client.post('/api/v1/admin/teachers', headers=self.token_auth_header(token), data=json.dumps(d))
            self.assertEquals(rv.status_code, 400)

    def test_remove_teacher(self):
        # create a teacher
        teacher = Teacher()
        teacher.from_dict({
            'username': 'u',
            'name': 'n',
            'password': 'p'
        })
        db.session.add(teacher)
        db.session.commit()

        number_of_teachers_before = len(Teacher.query.all())

        # try to access with basic authentication
        rv = self.client.delete(f'/api/v1/admin/teacher/{teacher.id}', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.delete(f'/api/v1/admin/teacher/{teacher.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        number_of_teachers_after = len(Teacher.query.all())
        self.assertEquals(number_of_teachers_before - number_of_teachers_after, 1)

        # try to remove a nonexistent teacher
        rv = self.client.delete(f'/api/v1/admin/teacher/{teacher.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 410)

    def test_get_students(self):
        # try to access with basic authentication
        rv = self.client.get('/api/v1/admin/students', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.get('/api/v1/admin/students', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertTrue(all(item in data for item in ['students', 'next', 'prev']))
        self.assertEquals(len(data['students']), 1)
        self.assertTrue(all(item in data['students'][0] for item in ['id', 'name', 'username']))
        self.assertIsNotNone(data['students'][0]['id'])
        self.assertEquals(data['students'][0]['name'], 'student')
        self.assertEquals(data['students'][0]['username'], 'student')

    def test_create_student(self):
        # try to access with basic authentication
        rv = self.client.post('/api/v1/admin/students', headers=self.basic_auth_header('admin', 'admin'), \
                              data=json.dumps({'username': 'f1', 'name': 'f2', 'password': 'f3'}))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.post('/api/v1/admin/students', headers=self.token_auth_header(token), \
                              data=json.dumps({'username': 'f1', 'name': 'f2', 'password': 'f3'}))
        self.assertEquals(rv.status_code, 200)

        # check if student was created
        student = Student.query.filter_by(username='f1').first()
        self.assertIsNotNone(student)
        self.assertEquals(student.username, 'f1')
        self.assertEquals(student.name, 'f2')
        self.assertIsNotNone(student.password_hash)
        self.assertNotEquals(student.password_hash, 'f3')

        # try to create student without all the necessary fields
        data = {
            'username': 'u',
            'name': 'n',
            'password': 'p'
        }
        request_datas = self.insufficient_datas(data)
        for d in request_datas:
            rv = self.client.post('/api/v1/admin/students', headers=self.token_auth_header(token), data=json.dumps(d))
            self.assertEquals(rv.status_code, 400)

    def test_remove_student(self):
        # create a student
        student = Student()
        student.from_dict({
            'username': 'u',
            'name': 'n',
            'password': 'p'
        })
        db.session.add(student)
        db.session.commit()

        number_of_students_before = len(Student.query.all())

        # try to access with basic authentication
        rv = self.client.delete(f'/api/v1/admin/student/{student.id}', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 401)

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token
        rv = self.client.delete(f'/api/v1/admin/student/{student.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        number_of_students_after = len(Student.query.all())
        self.assertEquals(number_of_students_before - number_of_students_after, 1)

        # try to remove a nonexistent student
        rv = self.client.delete(f'/api/v1/admin/student/{student.id}', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 410)