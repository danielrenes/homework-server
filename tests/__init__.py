import base64
import itertools
import unittest

from homework_server import create_app, db
from homework_server.models import Administrator, Student, Teacher


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

class BaseApiTest(BaseTest):
    def setUp(self):
        super(BaseApiTest, self).setUp()

        self.admin = Administrator()
        self.admin.from_dict({
            'name': 'admin',
            'username': 'admin',
            'password': 'admin'
        })
        db.session.add(self.admin)

        self.teacher = Teacher()
        self.teacher.from_dict({
            'name': 'teacher',
            'username': 'teacher',
            'password': 'teacher'
        })
        db.session.add(self.teacher)

        self.student = Student()
        self.student.from_dict({
            'name': 'student',
            'username': 'student',
            'password': 'student'
        })
        db.session.add(self.student)

        db.session.commit()

    def basic_auth_header(self, username, password):
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }
        credentials = base64.b64encode(f'{username}:{password}'.encode()).decode('utf-8')
        headers['Authorization'] = f'Basic {credentials}'
        return headers

    def token_auth_header(self, token):
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }
        headers['Authorization'] = f'Bearer {token}'
        return headers

    def insufficient_datas(self, data):
        fields = list(data.keys())

        combinations = []
        for i in range(1, len(fields)):
            combinations.append(list(itertools.combinations(fields, i)))

        request_datas = []
        for l1 in combinations:
            for l2 in l1:
                d = {}
                for f in l2:
                    d[f] = data[f]
                request_datas.append(d)

        return request_datas