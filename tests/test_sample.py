import unittest
from app import app

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        
    def test_home_page(self):
        rv = self.client.get('/index')
        self.assertNotIn('404', rv.data)

if __name__ == '__main__':
    unittest.main()