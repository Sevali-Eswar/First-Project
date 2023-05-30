from fastapi import APIRouter, Form, Request, HTTPException, Depends, Response, status
from models.user import User
from config.db import collection
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse,JSONResponse
from passlib.context import CryptContext
import re
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

user = APIRouter()

templates = Jinja2Templates(directory="web")

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
COOKIE_NAME = os.getenv("COOKIE_NAME")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(passwords: str):
    return pwd_context.hash(passwords)

def verify_password(passwords: str, hashed_password: str):
    return pwd_context.verify(passwords, hashed_password)

# Authentication part

def get_user(mail: str):
    Existing_mail = collection.find_one({'email': mail})
    if not Existing_mail:
        return False
    else:
        return Existing_mail


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

# creating the token

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# decode the generated token

def decode_token(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    if token is None:
        return None
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user(username)
        return user
    except JWTError as e:
        print(e)
        raise credentials_exception

# retrieve token from cookie for authorization

def get_current_user_from_cookie(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    user_data = decode_token(token)
    if user_data is None:
        return None
    return user_data

# email validation

def is_valid_email(mail):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, mail) is not None

# login get method

@user.get("/", response_class=HTMLResponse)
def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

# login post method

@user.post("/login")
async def login_user(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    context = {"request": request}
    email = form_data.username
    password = form_data.password
    user = authenticate_user(email, password)
    try:
        if not user:
            response_data = {"Invalid Email or Password"}
            if "application/json" in request.headers.get("accept"):
                response = JSONResponse(status_code=401, content=response_data)
                response.delete_cookie(COOKIE_NAME)
                return response
            context["error_message"] = "Invalid Email or Password"
            return templates.TemplateResponse("signin.html", context)

        access_token = create_access_token(data={"sub": user["email"]})
        response_data = {"User login successful"}

        if "application/json" in request.headers.get("accept"):
            response = JSONResponse(status_code=200, content=response_data)
        else:
            response = RedirectResponse("/Dashboard", status.HTTP_302_FOUND)

        response.set_cookie(key=COOKIE_NAME, value=f"Bearer {access_token}", httponly=True)
        return response
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing parameter: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc


# signup get method

@user.get("/signup", response_class=HTMLResponse)
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# signup post method

@user.post("/", response_class=HTMLResponse, name="signup")
async def signup(request: Request, username: str = Form(...), mail: str = Form(...), passwords: str = Form(...), confirmpasswords: str = Form(...)):
    context = {"request": request}
    existing_user = collection.find_one({"email": mail})
    if existing_user:
        response_data = {"User already exists"}
        if request.headers.get("accept") == "application/json":
            return JSONResponse(status_code=401, content=response_data)
        context["error_message1"] = "Email addresss already used "
        return templates.TemplateResponse("signup.html", context)
    if passwords != confirmpasswords:
        response_data = {"password not match"}
        if request.headers.get("accept") == "application/json":
            return JSONResponse(status_code=401, content=response_data)
        context["error_message1"] = "password not match "
        return templates.TemplateResponse("signup.html", context)
    if not is_valid_email(mail):
        response_data = {"Please enter valid email address"}
        if request.headers.get("accept") == "application/json":
            return JSONResponse(status_code=401, content=response_data)
        context["error_message1"] = "Please enter valid email address "
        return templates.TemplateResponse("signup.html", context)
    if len(passwords) < 8:
        response_data = {"Password should be at least 8 characters long"}
        if request.headers.get("accept") == "application/json":
            return JSONResponse(status_code=401, content=response_data)
        context["error_message1"] = "Password should be at least 8 characters long"
        return templates.TemplateResponse("signup.html", context)
    hashed_password = hash_password(passwords)
    usersdata = User(name=username, email=mail,
                     password=hashed_password, confirmpassword=hashed_password)
    dataofusers = collection.insert_one(dict(usersdata))
    print(dataofusers)
    response_data = {"User Successfully registered"}
    if request.headers.get("accept") == "application/json":
        return JSONResponse(status_code=401, content=response_data)
    return templates.TemplateResponse("signin.html", {"request": request})

# dashboard get method

@user.get("/Dashboard", response_class=HTMLResponse)
def dashboard(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if request.headers.get("accept") == "application/json":
        response_data = {"welcome to dashboard page"}
        return JSONResponse(status_code=200, content=response_data)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return templates.TemplateResponse("dash.html", {"request": request, "name": current_user["name"]})

# myaccount get method

@user.get("/myaccount", response_class=HTMLResponse)
def myaccount(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if request.headers.get("accept") == "application/json":
        response_data = {"welcome to myaccount page"}
        return JSONResponse(status_code=200, content=response_data)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return templates.TemplateResponse("myaccount.html", {"request": request, "name": current_user["name"], "email": current_user["email"]})

# logout get method

@user.get("/logout")
def logout_get(response: Response, request: Request):
    try:
        response_data = { "User logout successful"}
        response = RedirectResponse(url="/")
        if "application/json" in request.headers.get("accept"):
            response = JSONResponse(status_code=200, content=response_data)
        response.delete_cookie(COOKIE_NAME)
        return response
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="Cookie name not found.") from exc

    
# forgot password get method
    
@user.get("/forgotpassword",response_class=HTMLResponse)
def forgot(request:Request):
    return templates.TemplateResponse("forgotpassword.html",{"request":request})


# forgot password

user_data = {}
# Email settings
MAIL_USERNAME = "scmxperlite.official@outlook.com",
MAIL_PASSWORD = "SCMXPerLite@123",
MAIL_FROM = "scmxperlite.official@outlook.com",
MAIL_PORT = 587,
MAIL_SERVER = "smtp.office365.com",
MAIL_STARTTLS = False,
MAIL_SSL_TLS = True,
USE_CREDENTIALS = True,
VALIDATE_CERTS = True

def generate_otp():
 # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    return otp

def send_email(receiver_email, otp):
    sender_email = 'scmxperlite.official@outlook.com'
    password = 'SCMXPerLite@123'
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, password)
        smtp.send_message(msg)

# forgot password post method

@user.post("/forgot_password")
async def forgot_password_post(request: Request, mail: str = Form(...)):
    global user_data
    data = collection.find_one({"email": mail})
    if data:
        # Generate OTP
        otp = random.randint(100000, 999999)
        # Store user email and OTP in dictionary
        user_data["email"] = mail
        user_data["otp"] = otp
        user_data["otp_expiry"] = datetime.now() + timedelta(minutes=15)
        print(user_data)
        # Send the OTP to the user's email
        send_email(mail, otp)
        # Return a success response or redirect the user to an OTP verification page
        if request.headers.get("accept") == "application/json":
            response_data = {"OTP sent successfully"}
            return JSONResponse(status_code=200, content=response_data)
        return templates.TemplateResponse("resetpassword.html",{"message": "OTP sent successfully",'request':request})
    else:
        if request.headers.get("accept") == "application/json":
            response_data = {"Email not found"}
            return JSONResponse(status_code=401, content=response_data)
        return templates.TemplateResponse("forgotpassword.html",{"message1": "Email not found",'request':request})
    
# to verify otp
    
def verify_otp(otp: int) -> bool:
    global user_data
    if "email" in user_data and "otp" in user_data:
        if otp == user_data["otp"]:
            return True
    return False

# reset password post method

@user.post("/resetpassword")
async def reset_password_post(request: Request,otp:int=Form(...), passwords: str = Form(...), confirmpassword: str = Form(...)):
    global user_data
    if "email" in user_data and "otp_expiry" in user_data:
        if datetime.now() <= user_data["otp_expiry"]:
            if verify_otp(otp):
                if passwords == confirmpassword:
                    hashed_password = hash_password(passwords)
                    collection.update_one({"email": user_data["email"]}, {"$set": {"password": hashed_password}})

                    # Clear user data from dictionary
                    del user_data["email"]
                    del user_data["otp"]
                    del user_data["otp_expiry"]
                    print(user_data)
                    # Return success message
                    if request.headers.get("accept") == "application/json":
                        response_data = {"Password Reset Successfully."}
                        return JSONResponse(status_code=200, content=response_data)
                    return templates.TemplateResponse("signin.html", {"request": request, "message": "Password Reset Successfully."})
                else:
                    if request.headers.get("accept") == "application/json":
                        response_data = {"Passwords do not match."}
                        return JSONResponse(status_code=401, content=response_data)
                    return templates.TemplateResponse("resetpassword.html", {"request": request, "message1": "Passwords do not match."})
            else:
                if request.headers.get("accept") == "application/json":
                        response_data = {"Invalid OTP."}
                        return JSONResponse(status_code=401, content=response_data)
                return templates.TemplateResponse("resetpassword.html", {"request": request, "message1": "Invalid OTP."})
        else:
            if request.headers.get("accept") == "application/json":
                        response_data = {"OTP has expired."}
                        return JSONResponse(status_code=401, content=response_data)
            return templates.TemplateResponse("resetpassword.html", {"request": request, "message1": "OTP has expired."})
    else:
        if request.headers.get("accept") == "application/json":
                        response_data = {"Invalid Credentials."}
                        return JSONResponse(status_code=401, content=response_data)
        return templates.TemplateResponse("resetpassword.html", {"request": request, "message1": "Invalid Credentials."})



 