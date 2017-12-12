from pymongo import MongoClient
import main
import base64
import json
import unittest


class FlaskrTestCase(unittest.TestCase):

  def setUp(self):
    main.app.testing = True
    self.app = main.app.test_client()

  def tearDown(self):
    client = MongoClient(main.app.config['MONGO_URI'])

  def open_with_auth(self, url, method, **kwargs):
    return self.app.open(url,
                         method=method,
                         headers={ 'Authorization': 'Basic ' + base64.b64encode(bytes("test:testpw", 'ascii')).decode('ascii')
                         }, **kwargs
                         )

  def test_get_users(self):
    resp = self.app.get('/prt/api/v1.0/users')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users', 'GET')
    self.assertEqual(resp.status_code, 200)

  def test_get_user(self):
    resp = self.app.get('/prt/api/v1.0/users/1')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users/1', 'GET')
    self.assertEqual(resp.status_code, 200)

  def test_create_user(self):
    resp = self.app.post('/prt/api/v1.0/users')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users', 'POST',
                               data=json.dumps({
                              "firstname": "test user1",
                              "lastname": "sur",
                              "latitude": "78.9090",
                              "longitude": "90.8979"
                            }),
                               content_type='application/json')
    self.assertEqual(resp.status_code, 201)



  def test_update_user(self):
    resp = self.app.put('/prt/api/v1.0/users/2')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users/2', 'POST',
                               data=json.dumps({
                              "firstname": "updated user1"
                            }),
                               content_type='application/json')
    self.assertEqual(resp.status_code, 200)        

  def test_delete_user(self):
    resp = self.app.delete('/prt/api/v1.0/users/4')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/users/4', 'DELETE')
    self.assertEqual(resp.status_code, 200)
    

  def test_get_distances(self):
    resp = self.app.get('/prt/api/v1.0/distances')
    self.assertEqual(resp.status_code, 403)

    resp = self.open_with_auth('/prt/api/v1.0/distances', 'GET')
    self.assertEqual(resp.status_code, 200) 