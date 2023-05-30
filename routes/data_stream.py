from fastapi import APIRouter, Request, HTTPException, Depends
from config.db import collection2
from fastapi.templating import Jinja2Templates
<<<<<<< HEAD
from fastapi.responses import HTMLResponse,JSONResponse
=======
from fastapi.responses import HTMLResponse
>>>>>>> origin/master
from routes.user import get_current_user_from_cookie

data_stream = APIRouter()

templates = Jinja2Templates(directory="web")

# device data stream get method

@data_stream.get("/device", response_class=HTMLResponse)
<<<<<<< HEAD
def datastream(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    response_data = {"welcome to device data stream page"}
    if request.headers.get("accept") == "application/json":
        return JSONResponse(status_code=200, content=response_data)
=======
def home(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
>>>>>>> origin/master
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=401, detail="Admins only Authorised")
    data = collection2.find()
    return templates.TemplateResponse("devices.html", {"request": request, "data": data})
