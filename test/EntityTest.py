import unittest as test

import sys
sys.path.append(".")

from Entity import * 


class ValidationTest(test.TestCase):
    def setUp(self):
        print('⇓⇓ Validation Test Start ⇓⇓') 
        self.validation = Validation(username="user",password="password")   
    def test_items(self):
        print('---Test Case items---')
        self.assertEqual(self.validation.items(),["user","password"],"`items`函数未通过")
    def tearDown(self):
        print('~~ Validation Test Finish ~~')

class UserTest(test.TestCase):
    def setUp(self):
        print('⇓⇓ Validation Test Start ⇓⇓') 
        self.user = User(username="user",password="password",email="2698531708@qq.com",privilege=True)
    def test_items(self):
        print('---Test Case items---')
        self.assertEqual(self.user.items(),["user",
                                            "password",
                                            "2698531708@qq.com",
                                            True,None,None,None],'`items` 函数未通过')
    def test_keys(self):
        print('---Test Case keys---')
        self.assertEqual(User.keys(),["username",
                "password",
                "email",
                "privilege",
                "address",
                "phone",
                "introduction"],'`keys` 函数未通过') 
    def test_str(self):
        print('---Test Case str---')
        self.assertEqual(User.__str__(),"User",'`__str__` 函数未通过')
    def tearDown(self) :
        print('~~ User Test Finish ~~')

if __name__ == "__main__":
    test.main()