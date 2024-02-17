from fastapi import Depends, FastAPI, Request,Cookie , HTTPException, Response
from fastapi.responses import HTMLResponse,RedirectResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
from typing import Union
from typing_extensions import Annotated
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier

from uuid import UUID , uuid4



from Service import *
from Entity import *

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SessionData(BaseModel):
    username: str
    access : str


cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)



#initDataBase()

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="./static/template")

@app.get("/",response_class=HTMLResponse)
async def hello(request : Request):
    return templates.TemplateResponse(request=request,name="login.html")

@app.get("/register",response_class=HTMLResponse)
async def register(request : Request):
    return templates.TemplateResponse(request=request,name="register.html")

@app.post("/register")
async def register(user : User):
    euser = User_Entity(user)
    if not UserService.getUser(euser):
        UserService.registerUser(euser)
        mail_host = "smtp.qq.com"
        mail_user = "2698531708"
        mail_pass = "reztbfnkwfqzddbh"
        sender = "2698531708@qq.com"
        message = MIMEText('通过链接 192.168.42.141:8000/activate/%s 激活邮箱'%(user.username),'plain','utf-8')
        message['Subject'] = 'Nebula Space 校验码'
        message['From'] = sender 
        message['To'] = user.email
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host,25)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(
            sender,[user.email],message.as_string())
        smtpObj.quit()
        return RedirectResponse("/register/success")
    else:
        return RedirectResponse("/register/failure")

@app.get("/activate/{username}",response_class=HTMLResponse)
async def activate(request : Request,username : str):
    UserService.activateUserPrivilege(username)
    print(username)
    return templates.TemplateResponse(request=request,name="verify_prompt.html",context = {"signal":"pass","info":"激活成功"})

@app.get("/register/success",response_class=HTMLResponse)
async def register_success(request : Request):
    return templates.TemplateResponse(request=request,name="register_prompt.html",context = {"signal":"pass" ,"info": "注册成功"})

@app.get("/register/failure",response_class=HTMLResponse)
async def register_failure(request : Request):
    return templates.TemplateResponse(request=request,name="register_prompt.html",context = {"signal":"error","info":"用户名重复"})

@app.get("/login",response_class=HTMLResponse)
async def login(request : Request):
    return templates.TemplateResponse(request=request,name="login.html",context = {"info": None})


    
@app.get("/home",response_class=HTMLResponse,dependencies=[Depends(cookie)])
async def home(request : Request , session_data: SessionData = Depends(verifier)):
    if session_data.access == "permmit":
        return templates.TemplateResponse(request=request,name="home.html")
    else:
        return RedirectResponse("/login/failure")
    #return session_data
    #return templates.TemplateResponse(request=request,name="home.html")

@app.post("/login")
async def login(user : Validation,response:Response):
    euser = Validation_Entity(user)
    if UserService.validateUser(euser):
        session = uuid4()
        data = SessionData(username=user.username,access="permmit")
        await backend.create(session,data)
        cookie.attach_to_response(response,session)
    else: 
        return RedirectResponse("/login/failure")


@app.get("/login/failure",response_class=HTMLResponse)
async def login_failure(request : Request):        
    return templates.TemplateResponse(request=request,name="login.html",context = {"info":"账号密码错误"})
    
@app.get("/forget",response_class=HTMLResponse)
async def forget(request : Request):
    return templates.TemplateResponse(request=request,name="forget.html")

@app.get("/forget/failure",response_class=HTMLResponse)
async def forget_failure(request : Request):
    return templates.TemplateResponse(request=request,name="verify_prompt.html",context = {"signal": "error","info": "校验码错误"})

@app.get("/forget/success",response_class=HTMLResponse)
async def forget_success(request : Request):
    return templates.TemplateResponse(request=request,name="register_prompt.html",context = {"signal":"pass","info":"修改密码成功"})

@app.post("/forget")
async def forget(forgetValidation : ForgetValidation):
    old_password = UserService.fetchUserPassword(forgetValidation.username)
    if old_password == forgetValidation.password:
        result = UserService.updateUserPassword(forgetValidation.username,forgetValidation.password_new)
        return RedirectResponse("/forget/success")
    else:
        return RedirectResponse("/forget/failure")

@app.get("/sendverify",response_class=HTMLResponse)
async def sendVerify(request : Request, username : Optional[str]):
    privilege = UserService.fetchUserPrivilege(username)
    #print(privilege)
    if privilege == "R":
        return templates.TemplateResponse(request=request,name="verify_prompt.html",context = {"signal":"error","info":"您的用户名不存在"})
    elif privilege is None:
        return templates.TemplateResponse(request=request,name="verify_prompt.html",context = {"signal":"error","info":"您的邮箱还没有验证"})
    else:
        password = UserService.fetchUserPassword(username)
        #print(password)
        email = UserService.fetchUserEmail(username)
        mail_host = "smtp.qq.com"
        mail_user = "2698531708"
        mail_pass = "reztbfnkwfqzddbh"
        sender = "2698531708@qq.com"
        message = MIMEText(password,'plain','utf-8')
        message['Subject'] = 'Nebula Space 校验码'
        message['From'] = sender 
        message['To'] = email
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host,25)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(
            sender,[email],message.as_string())
        smtpObj.quit()
        return templates.TemplateResponse(request=request,name="verify_prompt.html",context= {"signal":"pass","info":"校验信息已经发送至您的邮箱"})

@app.post("/create_session/{username}/{password}")
async def create_session(username: str, password : str ,response: Response):

    session = uuid4()
    data = SessionData(username=username)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)



@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"