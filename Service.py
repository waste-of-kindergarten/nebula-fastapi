from sqlite3 import * 
from Entity import *


conn = connect("/home/user/demo/python/app/data.sqlite")
cursor = conn.cursor() 

def initDataBase():
    clearDataBase()
    cursor.execute("Create Table if not exists \
    User(username TEXT Primary Key, \
    password TEXT Not Null, \
    email TEXT Not Null, \
    privilege BOOL, \
    address TEXT, \
    phone TEXT, \
    introduction TEXT)")
    conn.commit()

def clearDataBase():
    cursor.execute("Drop Table User")

class DataBaseService:
    entity = None
    @classmethod 
    def insert(cls,values):
        cursor.execute("Insert Into %s Values(?,?,?,?,?,?,?)"%cls.entity.__str__(),values)
        conn.commit()
    @classmethod
    def delete(cls,conditions = ()):
        if conditions != ():
            cursor.execute("Delete From %s Where %s"%(cls.entity.__str__(),
                                                               (" And ".join([(cls.entity.keys()[k] + " " + val[0] + " " + (str(val[1]) if type(val[1]) != str else '"' + val[1] + '"'))
                                                                    for k,val in enumerate(conditions) if val]))))
            conn.commit()
        else:
            cursor.execute("Delete From %s"%cls.entity.__str__())
            conn.commit()
    @classmethod
    def select(cls,conditions = ()):
        if conditions != ():
            return cursor.execute("Select * From %s Where %s"%(cls.entity.__str__(),
                                                                  (" And ".join([(cls.entity.keys()[k] + " " + val[0] + " " + (str(val[1]) if type(val[1]) != str else '"' + val[1] + '"'))
                                                                        for k,val in enumerate(conditions) if val]))))
        else:
            return cursor.execute("Select * From %s"%cls.entity.__str__())
    @classmethod
    def update(cls,values,conditions = ()):
        if conditions != ():
            cursor.execute("Update %s Set %s Where %s"%(cls.entity.__str__(),
                                            (" , ".join([cls.entity.keys()[k] + " = " + (str(val) if (type(val) != str) else '"' + val + '"')
                                                           for k,val in enumerate(values) if val])),
                                            (" And ".join([cls.entity.keys()[k] + " " + str(val[0]) + " " + (str(val[1]) if type(val[1]) != str else '"' + val[1] + '"') 
                                                           for k,val in enumerate(conditions) if val[1]]))))     
            conn.commit()
        else:
            cursor.execute("Update %s Set %s"%(cls.entity.__str__(),
                                            (" , ".join([cls.entity.keys()[k] + " = " + (str(val) if (type(val) != str) else '"' + val + '"')
                                                           for k,val in enumerate(values) if val]))))
            conn.commit()

class UserService(DataBaseService):
    entity = User_Entity
    @classmethod
    def validateUser(cls,vuser : Validation):
        result = cls.select(conditions=((" == ",vuser.model.username),)).fetchone()
        if result:
            return vuser.model.password == result[1]
        else: 
            return False
    @classmethod 
    def registerUser(cls,user : User):
        cls.insert(values=user.items())
    @classmethod
    def getUser(cls,user : User):
        return cls.select(conditions=((" == ",user.model.username),)).fetchone() 
    @classmethod 
    def updateUser(cls,user : User):
        cls.update(values=user.items(),conditions=((" == ",user.username),))
    @classmethod 
    def fetchUserPassword(cls,username):
        result = cls.select(conditions=((" == ",username),)).fetchone()
        if result: 
            return None 
        else:
            return result
    @classmethod
    def fetchUserPrivilege(cls,username):
        result = cls.select(conditions=((" == ",username),)).fetchone()
        if result is None:
            return "R" # Refuse 
        elif result == ():
            return None # None
        else:
            return result[3]
    @classmethod
    def activateUserPrivilege(cls,username):
        result = cls.select(conditions=((" == ",username),)).fetchone()
        if result == ():
            return None 
        else:
            result[3] = False
            cls.update(values=result,conditions=((" == ",username),))

    