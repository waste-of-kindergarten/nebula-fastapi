from pydantic import BaseModel
from typing import Optional

class EntityModel:
    def __init__(self,model):
        self.model = model 
    def items(self):
        NotImplemented
    @classmethod
    def keys(cls):
        NotImplemented
    @classmethod
    def __str__(cls):
        NotImplemented

class Validation(BaseModel):
    username: str
    password: str 

class ForgetValidation(BaseModel):
    username: str 
    password: str 
    password_new : str

class Validation_Entity(EntityModel):
    def __init__(self,model : Validation):
        super().__init__(model)
    def items(self):
        return [self.model.username,self.model.password]

 
class User(BaseModel):
    username: str
    password: str 
    email: str 
    privilege: Optional[str] = None
    address: Optional[str] = None 
    phone: Optional[str] = None 
    introduction: Optional[str] = None

class User_Entity(EntityModel):
    def __init__(self,model):
        super().__init__(model)
    def items(self):
        return [self.model.username,
                self.model.password,
                self.model.email,
                self.model.privilege,
                self.model.address,
                self.model.phone,
                self.model.introduction]
    @classmethod
    def keys(cls):
        return ["username",
                "password",
                "email",
                "privilege",
                "address",
                "phone",
                "introduction"] 
    @classmethod
    def __str__(cls):
        return "User"