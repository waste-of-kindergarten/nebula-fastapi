import unittest as test 
import sys 
sys.path.append(".")

from Entity import *
from Service import *

class UserServiceTest(test.TestCase):
    def setUp(self):
        print('⇓⇓ UserService Test Start ⇓⇓')
        self.vuser = Validation(username="user",password="pswd")
        self.user = User(username="user",password="pswd",email="2698531708@qq.com",privilege=True,address=None,phone=None,introduction=None)
        self.user1 = User(username="user",password="pswd1",email="2698531708@qq.com",privilege=True,address=None,phone=None,introduction=None)
        cursor.execute("drop table if exists User")
        #print("---Test Case initDataBase---")
        initDataBase(UserService.entity)
    def test_registerUser(self):
        print("---Test Case registerUser---")
        UserService.registerUser(self.user)
    def test_validateUser(self):
        print("---Test Case validateUser---")
        UserService.registerUser(self.user)
        self.assertTrue(UserService.validateUser(self.vuser))
    def test_getUser(self):
        print("---Test Case getUser---")
        UserService.registerUser(self.user)
        self.assertEqual(UserService.getUser(self.user),('user', 'pswd', '2698531708@qq.com', 1, None, None, None))
    def test_updateUser(self):
        print("---Test Case updateUser---")
        UserService.registerUser(self.user)
        UserService.updateUser(self.user1)
        self.assertEqual(UserService.getUser(self.user1),tuple(self.user1.items()))
    def tearDown(self):
        print('~~ UserService Test Finish ~~')    

if __name__ == "__main__":
    test.main()