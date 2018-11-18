import json

from tests import BaseApiTest

from homework_server import db
from homework_server.models import Administrator, Course, Homework, Solution, Student, Teacher

class PaginationTest(BaseApiTest):
    def test_pagination(self):
        # remove default teacher
        db.session.delete(self.teacher)

        # create 55 teachers
        for i in range(55):
            t = Teacher()
            t.name = f't{i:02}'
            t.username = f't{i:02}'
            t.set_password(f't{i:02}')
            db.session.add(t)
        
        db.session.commit()

        # get token
        rv = self.client.post('/api/v1/auth/token', headers=self.basic_auth_header('admin', 'admin'))
        self.assertEquals(rv.status_code, 200)
        token = json.loads(rv.data.decode())['token']

        # access with token (items 0-24)
        rv = self.client.get('/api/v1/admin/teachers', headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertEquals(len(data['teachers']), 25)
        for i in range(0, 25):
            self.assertEquals(data['teachers'][i]['name'], f't{i:02}')
        self.assertIsNotNone(data['next'])
        self.assertIsNone(data['prev'])

        # get next page (items 25-49)
        rv = self.client.get(data['next'], headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertEquals(len(data['teachers']), 25)
        for i in range(25, 50):
            self.assertEquals(data['teachers'][i - 25]['name'], f't{i:02}')
        self.assertIsNotNone(data['next'])
        self.assertIsNotNone(data['prev'])

        # get next page (items 49-54)
        rv = self.client.get(data['next'], headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertEquals(len(data['teachers']), 5)
        for i in range(50, 55):
            self.assertEquals(data['teachers'][i - 50]['name'], f't{i:02}')
        self.assertIsNone(data['next'])
        self.assertIsNotNone(data['prev'])

        # get previous page (items 25-49)
        rv = self.client.get(data['prev'], headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertEquals(len(data['teachers']), 25)
        for i in range(25, 50):
            self.assertEquals(data['teachers'][i - 25]['name'], f't{i:02}')
        self.assertIsNotNone(data['next'])
        self.assertIsNotNone(data['prev'])

        # get previous page (items 0-24)
        rv = self.client.get(data['prev'], headers=self.token_auth_header(token))
        self.assertEquals(rv.status_code, 200)

        # check returned data
        data = json.loads(rv.data.decode())
        self.assertEquals(len(data['teachers']), 25)
        for i in range(0, 25):
            self.assertEquals(data['teachers'][i]['name'], f't{i:02}')
        self.assertIsNotNone(data['next'])
        self.assertIsNone(data['prev'])