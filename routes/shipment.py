from fastapi import APIRouter, Form, Request, HTTPException, Depends, Response, status
from config.db import collection1
from models.user import Shipment
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routes.user import get_current_user_from_cookie



shipment = APIRouter()

templates = Jinja2Templates(directory="web")

# myshipment get method

@shipment.get("/myshipment", response_class=HTMLResponse)
def home(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    data = collection1.find({"email":current_user["email"]})
    return templates.TemplateResponse("myshipment.html", {"request": request, "data": data})

# shipment get method

@shipment.get("/shipment", response_class=HTMLResponse)
def home(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return templates.TemplateResponse("shipments.html",  {"request": request})

# shipment post method

@shipment.post("/shipment_page", response_class=HTMLResponse, name="shipment")
async def home(request: Request, shipment_number: int = Form(...), container_number: int = Form(...), route_details: str = Form(...), goods_type: str = Form(...), device: str = Form(...), expected_delivery_date: str = Form(...), po_number: int = Form(...), delivery_number: int = Form(...), noc_number: int = Form(...), batch_id: int = Form(...), serial_number: int = Form(...), shipment_description: str = Form(...), current_user: dict = Depends(get_current_user_from_cookie)):
    if current_user is None:
        # Handle the case where the current user is not available
        raise HTTPException(status_code=401, detail="Unauthorized")
    shipmentdata = Shipment(ShipmentNumber=shipment_number, ContainerNumber=container_number, RouteDetails=route_details, GoodsType=goods_type, Device=device, ExpectedDeliveryDate=expected_delivery_date,
                            PONumber=po_number, DeliveryNumber=delivery_number, NOCNumber=noc_number, BatchId=batch_id, SerialNumberOfGoods=serial_number, ShipmentDescription=shipment_description,email=current_user["email"])
    existing_shipment=collection1.find_one( {"ShipmentNumber": shipment_number})
    try:
        if not existing_shipment:
            dataofshipment = collection1.insert_one(dict(shipmentdata))
            print(dataofshipment)
            return templates.TemplateResponse("shipments.html",{"request":request,"message":"Shipment created successfully"})
        else:
            return templates.TemplateResponse("shipments.html",{"request":request,"message1":"Shipment Exists Already"})
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing parameter: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc
    