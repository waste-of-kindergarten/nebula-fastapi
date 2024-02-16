from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse,RedirectResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates

from Service import *
from Entity import *

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


    
@app.get("/home",response_class=HTMLResponse)
async def home(request : Request):
    return templates.TemplateResponse(request=request,name="home.html")

@app.post("/login")
async def login(request : Request,user : Validation):
    euser = Validation_Entity(user)
    if UserService.validateUser(euser):
        return RedirectResponse("/home")
    else: 
        return RedirectResponse("/login/failure")

@app.get("/login/failure",response_class=HTMLResponse)
async def login_failure(request : Request):        
    return templates.TemplateResponse(request=request,name="login.html",context = {"info":"账号密码错误"})
    
@app.get("/forget",response_class=HTMLResponse)
async def forget(request : Request):
    return templates.TemplateResponse(request=request,name="forget.html")

@app.get("/sendverify",response_class=HTMLResponse)
async def sendVerify(request : Request, username : Optional[str]):
    privilege = UserService.fetchUserPrivilege(username)
    #print(privilege)
    if privilege == "R":
        return templates.TemplateResponse(request=request,name="verify_prompty.html",context = {"signal":"error","info":"您的用户名不存在"})
    elif privilege is None:
        return templates.TemplateResponse(request=request,name="verify_prompt.html",context = {"signal":"error","info":"您的邮箱还没有验证"})
    else:
        password = UserService.fetchUserPassword(username)
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


