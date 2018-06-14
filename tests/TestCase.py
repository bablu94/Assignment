#!flask/bin/python

import unittest
import json
import time
import base64
from app import app,db,User




class TestCase(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def test_user_a(self):
        print "user"
        if User.query.filter_by(username="bablu").first() is None:
            user = User(username="bablu")

            user.hash_password("123456")
            db.session.add(user)
            db.session.commit()

    def test_user_b(self):
        print "add"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        data = '{"1":{"name" : "Bablu Kumar", "email" : "babluk@gmail.com", "mobile" : "7002926956"},"2":{"name":"abc","email":"abc@gmail.com","mobile":"7002926956"}}'
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode('bablu:123456')
        }
        response = self.app.post('/api/add',data =data,headers = headers,follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        print response.get_data(as_text=True)


    def test_user_c(self):
        print "edit"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        data = '{"1":{"name" : "User1", "email" : "babluk@gmail.com", "mobile" : "7002926956"}}'
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode('bablu:123456')
        }
        response = self.app.post('/api/edit', data=data, headers=headers, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        print response.get_data(as_text=True)


    def test_user_d(self):
        print "search"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        data = '{"email":"suryap"}'
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode('bablu:123456')
        }
        response = self.app.post('/api/search', data=data, headers=headers, follow_redirects=True)

        # print response
        self.assertEqual(response.status_code, 200)
        contact = {
            "contacts": [
                {
                    "contact email": "babluk@gmail.com",
                    "contact mobile": 7002926956,
                    "contact name": "User1"
                }
            ]
        }

        self.assertEqual(contact, json.loads(response.get_data(as_text=True)))

    def test_user_e(self):
        print "delete"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode('bablu:123456')
        }

        data = '{"1":{"name" : "User1", "email" : "babluk@gmail.com", "mobile" : "7002926956"}}'
        response = self.app.post('/api/delete', data=data, headers=headers, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # print response.content

    def test_user_f(self):
        print "search"
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode('bablu:123456')
        }

        data = '{"email":"suryap"}'
        response = self.app.post('/api/search', data=data, headers=headers, follow_redirects=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual('suryap Contact is not present',response.get_data(as_text=True))
        time.sleep(2)

    def test_user_g(self):
        print "testing unauthorized access "

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % base64.b64encode('xxxx:123456')
        }

        data = '{"1":{"name" : "Surya Pratap", "email" : "babluk@gmail.com", "mobile" : "7002926956"},"2":{"name":"abc","email":"abc@gmail.com","mobile":"7002926956"}}'

        response = self.app.post('/api/add', data=data, headers=headers, follow_redirects=True)

        self.assertEqual(response.status_code, 401)
        time.sleep(2)

    def test_user_zz_dropdown(self):
        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
    unittest.main()

