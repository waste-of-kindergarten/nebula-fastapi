from ast import literal_eval
from fastapi import Depends, FastAPI, Request,Cookie , HTTPException, Response
from fastapi.responses import HTMLResponse,RedirectResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import List, Union
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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request,exc):
    return RedirectResponse("/404")


#async def validation_exception_handler(request, exc : RequestValidationError):
#    return RedirectResponse("/login")

#app.add_exception_handler(RequestValidationError,validation_exception_handler)


@app.route("/404",methods=["GET","POST"])
async def _404(request : Request):
    return templates.TemplateResponse(request=request,name="404.html")

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

@app.get("/changepassword",response_class=HTMLResponse)
async def changepassword(request : Request):
    return templates.TemplateResponse(request=request,name="changepassword.html")

@app.post("/changepassword",dependencies=[Depends(cookie)])
async def changepassword(changePasswordValidation : ChangePasswordValidation,session_data: SessionData = Depends(verifier)):
    username = session_data.username 
    password = UserService.fetchUserPassword(username)
    if password == changePasswordValidation.password:
        #print("enter")
        #print(username,changePasswordValidation.password_new)
        UserService.updateUserPassword(username,changePasswordValidation.password_new)
    else:
        return RedirectResponse("/changepassword/failure")

@app.route("/changepassword/failure",methods=["GET","POST"])
async def changepassword_failure(request:Request):
    return templates.TemplateResponse(request=request,name="changepassword.html",context={"info":"原始密码错误"})
    
@app.get("/home",response_class=HTMLResponse,dependencies=[Depends(cookie)])
async def home(request : Request , session_data: SessionData = Depends(verifier)):
    if session_data.access == "permmit":
        return templates.TemplateResponse(request=request,name="home.html",context={ "username" : session_data.username, "p":["nav-link active","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white"]})
    else:
        return RedirectResponse("/login/failure",status_code=200)

@app.get("/home/person",response_class=HTMLResponse,dependencies=[Depends(cookie)])
async def home_person(request : Request, session_data: SessionData = Depends(verifier)):
    user = UserService.getUserByName(session_data.username)
    return templates.TemplateResponse(request=request,name="person.html",context=dict(zip(User_Entity.keys(),user)))

@app.post("/home/person",response_class=HTMLResponse,dependencies=[Depends(cookie)])
async def home_person(person : Person , request : Request, session_data : SessionData = Depends(verifier)):
    if session_data.username == person.username:
        username = person.username 
        user = UserService.getUserByName(username)
        #print(user)
        newuser = User(username = user[0],
                    password = user[1],
                    email = person.email,
                    privilege = user[3],
                    address = person.address,
                    phone = person.phone,
                    introduction = person.introduction)
        #print(newuser)
        euser = User_Entity(newuser)
        UserService.updateUser(euser)

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

@app.route("/login/failure",methods=["GET","POST"])
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

@app.get("/logout")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    try:
        await backend.delete(session_id)
        cookie.delete_from_response(response)
    finally:
        return RedirectResponse("/login")
    
@app.get('/home/queryvertex',dependencies=[Depends(cookie)])
async def queryvertex(request: Request,session_data: SessionData = Depends(verifier)):
    return templates.TemplateResponse(request=request,name="queryvertex.html",context={ "username" : session_data.username,"p":["nav-link text-white","nav-link active","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white"]})


example_body = '''{
    "query_type":"tags",
    "query_body":{
        "body_name":"team",
        "body_query":["NULL"]
    }
}'''

import urllib3
http = urllib3.PoolManager()

class QueryBody(BaseModel):
    body_name: str  
    body_query: List[str]

@app.post('/home/queryvertex',dependencies=[Depends(cookie)])
async def queryvertex(request:Request,querybody:QueryBody,session_data: SessionData = Depends(verifier)):
    print(querybody)
    vertexquery = '''{
    "query_type":"tags",
    "query_body":{
        "body_name":"%s",
        "body_query":%s
    }
    }'''%(querybody.body_name,querybody.body_query)
    vertexquery = vertexquery.replace("'",'"')
    #print(vertexquery)
    r = http.request('POST',"http://127.0.0.1:10000",body=vertexquery.encode('utf-8'),headers={'Content-Type':'application/json'})
    #return r.data.decode()
    demo = '''
digraph  {
node [shape=circle fontsize=16]
edge [length=100, color=gray, fontcolor=black]

%s
}
    '''%("\n".join(["%s [label=\"%s\"]"%(k,i[0][2:-1]) for k,i in enumerate(literal_eval(r.data.decode()))]))
    print(demo)
    return demo,[i[1] for i in literal_eval(r.data.decode())]

@app.get('/home/queryedge',dependencies=[Depends(cookie)])
async def queryedge(request:Request,session_data: SessionData = Depends(verifier)):
    return templates.TemplateResponse(request=request,name="queryedge.html",context={ "username" : session_data.username,"p":["nav-link text-white","nav-link text-white","nav-link active","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white"]})

@app.post('/home/queryedge',dependencies=[Depends(cookie)])
async def queryedge(request: Request,querybody:QueryBody,session_data: SessionData = Depends(verifier)):
    print(querybody)
    edgequery = '''{
    "query_type":"edges",
    "query_body":{
        "body_name":"%s",
        "body_query":%s
    }
    }'''%(querybody.body_name,querybody.body_query)
    edgequery = edgequery.replace("'",'"')
    #print(edgequery)
    r = http.request('POST',"http://127.0.0.1:10000",body=edgequery.encode('utf-8'),headers={'Content-Type':'application/json'})
    #print(r.data.decode())
    outnodeid,innodeid,allnode,edges = literal_eval(r.data.decode())
    tempnode = innodeid + outnodeid
    (nodeid1,allnode1) = ([],[])

    for i in range(len(tempnode)):
        if tempnode[i] not in nodeid1:
            nodeid1.append(tempnode[i])
            allnode1.append(allnode[i])

    edgeindex = [] 
    for i in range(len(edges)):
        edgeindex.append((nodeid1.index(outnodeid[i]),nodeid1.index(innodeid[i])))
    demo = '''
digraph  {
node [shape=circle fontsize=16]
edge [length=100, color=gray, fontcolor=black]

%s
%s
}
    '''%("\n".join(["%s [label=%s]"%(k,i[2:-1]) for k,i in enumerate(nodeid1)]),"\n".join(["%s -> %s [label=\"%s\",id=%s]"%(edgeindex[k][0],edgeindex[k][1],querybody.body_name,k) for k,i in enumerate(edges)]))
    print(demo)
    return demo,allnode1,edges 

@app.get('/home/playground',dependencies=[Depends(cookie)])
async def playground(request:Request,session_data: SessionData = Depends(verifier)):
    return templates.TemplateResponse(request=request,name="playground.html",context={"username" : session_data.username,"p":["nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link active"]})

@app.get('/home/schema',dependencies=[Depends(cookie)])
async def schema(request:Request,session_data: SessionData = Depends(verifier)):
    query='''{
    "query_type":"schema",
    "query_body":{
        "body_name":"",
        "body_query":[]
    }
    }
    '''
    r = http.request('POST',"http://127.0.0.1:10000",body=query.encode('utf-8'),headers={'Content-Type':'application/json'})
    data = literal_eval(r.data.decode())
    demo = '''
digraph  {
node [shape=circle fontsize=16]
edge [length=300, color=gray, fontcolor=black]

%s
    }'''%("\n\n".join(['%s -> %s [label=%s]'%(i[0],i[1],i[2]) for i in data]))
    print(demo)
    return templates.TemplateResponse(request=request,name="queryschema.html",context={"username" : session_data.username,"p":["nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link text-white","nav-link active","nav-link text-white"],"data" : demo})