from fastapi import APIRouter, Form,Request,HTTPException,Depends
from models.user import User,Shipment
from config.db import conn,db,coll,coll1
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext
from fastapi.staticfiles import StaticFiles
import pandas as pd
import re



user=APIRouter()

user.mount("/static", StaticFiles(directory="static",html=True), name="static")

templates=Jinja2Templates(directory="web")

db=conn["database"]
coll=db["users"]
coll1=db["shipment"]
coll2=db["Device_data_stream"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(passwords: str):
    return pwd_context.hash(passwords)

def verify_password(passwords:str, hashed_password:str):
    return pwd_context.verify(passwords, hashed_password)


@user.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("signin.html",{"request":request})

@user.get("/signup",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("signup.html",{"request":request})

@user.get("/Dashboard",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("dash.html",{"request":request})

@user.get("/myaccount",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("myaccount.html",{"request":request})

@user.get("/myshipment",response_class=HTMLResponse)
def home(request:Request):
   data = list(coll1.find())
   df=pd.DataFrame(data)
   df.drop(df.columns[0], axis=1, inplace=True)
   table_html = df.to_html(index=False)
   return templates.TemplateResponse("myshipment.html", {"request": request, "table_html": table_html})

@user.get("/shipment",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("shipments.html",{"request":request})

@user.get("/device",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("devices.html",{"request":request})
    
@user.post("/shipment_page",response_class=HTMLResponse, name="shipment")
async def home(request:Request, shipment_number:int =Form(...),container_number:int =Form(...),route_details:str =Form(...),goods_type:str =Form(...),device:str =Form(...),expected_delivery_date:str =Form(...),po_number:int =Form(...),delivery_number:int =Form(...),noc_number:int =Form(...),batch_id:int =Form(...),serial_number:int =Form(...),shipment_description:str =Form(...)):
    context={"request" : request}
    shipmentdata = Shipment(ShipmentNumber=shipment_number,ContainerNumber=container_number,RouteDetails=route_details,GoodsType=goods_type,Device=device,ExpectedDeliveryDate=expected_delivery_date,PONumber=po_number,DeliveryNumber=delivery_number,NOCNumber=noc_number,BatchId=batch_id,SerialNumberOfGoods=serial_number,ShipmentDescription=shipment_description)
    dataofshipment=coll1.insert_one(dict(shipmentdata))
    print(dataofshipment)
    return templates.TemplateResponse("shipments.html",context)

def is_valid_email(mail):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, mail) is not None
        
@user.post("/",response_class=HTMLResponse, name="signup")
async def home(request:Request, username:str =Form(...), mail:str =Form(...),passwords:str =Form(...) ,confirmpasswords: str =Form(...)):
    context = {"request": request}
    existing_user = coll.find_one({"email": mail})
    if existing_user:
        context["error_message1"] = "Email addresss already used "
        return templates.TemplateResponse("signup.html", context)
    if passwords != confirmpasswords:
        context["error_message1"] = "password not match "
        return templates.TemplateResponse("signup.html", context)
    if is_valid_email!=mail:
        context["error_message1"] = "Please enter valid email address "
        return templates.TemplateResponse("signup.html", context)
    hashed_password = hash_password(passwords)
    usersdata= User(name=username, email=mail, password = hashed_password,confirmpassword=hashed_password)
    dataofusers=coll.insert_one(dict(usersdata))
    print(dataofusers)
    return templates.TemplateResponse("dash.html",{"request":request})

@user.post("/login",response_class=HTMLResponse, name="login")
async def home(request:Request, mail:str =Form(...), passwords: str =Form(...)):
    context = {"request": request}
    dataoflogin = coll.find_one({"email": mail})
    if not dataoflogin:
        context["error_message"] = "Invalid email address "
        return templates.TemplateResponse("signin.html", context)
    if not verify_password(passwords, dataoflogin["password"]):
        context["error_message"] = "Invalid password "
        return templates.TemplateResponse("signin.html", context)
    return templates.TemplateResponse("dash.html",{"request":request})




    





