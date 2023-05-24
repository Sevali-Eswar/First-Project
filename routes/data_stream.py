from fastapi import APIRouter, Request, HTTPException, Depends
from config.db import collection2
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routes.user import get_current_user_from_cookie

data_stream = APIRouter()

templates = Jinja2Templates(directory="web")

# device data stream get method

@data_stream.get("/device", response_class=HTMLResponse)
def home(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=401, detail="Admins only Authorised")
    data = collection2.find()
    return templates.TemplateResponse("devices.html", {"request": request, "data": data})
