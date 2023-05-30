from fastapi import APIRouter, Form, Request, HTTPException, Depends
from config.db import collection1
from models.user import Shipment
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
from routes.user import get_current_user_from_cookie



shipment = APIRouter()

templates = Jinja2Templates(directory="web")

# myshipment get method


@shipment.get("/myshipment")
def myshipment(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    data = collection1.find({"email": current_user["email"]})
    response_data = [shipment for shipment in data]
    if request.headers.get("accept") == "application/json":
        return JSONResponse(content=response_data)
    return templates.TemplateResponse("myshipment.html", {"request": request, "data": response_data})

# shipment get method

@shipment.get("/shipment", response_class=HTMLResponse)
def shipment_page(request: Request, current_user: dict = Depends(get_current_user_from_cookie)):
    if request.headers.get("accept") == "application/json":
        response_data = {"welcome to shipment page"}
        return JSONResponse(status_code=200, content=response_data)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return templates.TemplateResponse("shipments.html",  {"request": request})

# shipment post method

@shipment.post("/shipment_page", response_class=HTMLResponse, name="shipment")
async def shipment_page(request: Request, shipment_number: int = Form(...), container_number: int = Form(...), route_details: str = Form(...), goods_type: str = Form(...), device: str = Form(...), expected_delivery_date: str = Form(...), po_number: int = Form(...), delivery_number: int = Form(...), noc_number: int = Form(...), batch_id: int = Form(...), serial_number: int = Form(...), shipment_description: str = Form(...), current_user: dict = Depends(get_current_user_from_cookie)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    shipmentdata = Shipment(ShipmentNumber=shipment_number, ContainerNumber=container_number, RouteDetails=route_details, GoodsType=goods_type, Device=device, ExpectedDeliveryDate=expected_delivery_date,
                            PONumber=po_number, DeliveryNumber=delivery_number, NOCNumber=noc_number, BatchId=batch_id, SerialNumberOfGoods=serial_number, ShipmentDescription=shipment_description,email=current_user["email"])
    existing_shipment=collection1.find_one( {"ShipmentNumber": shipment_number})
    try:
        if not existing_shipment:
            dataofshipment = collection1.insert_one(dict(shipmentdata))
            print(dataofshipment)
            response_data = {"Shipment created successfully"}
            if request.headers.get("accept") == "application/json":
                return JSONResponse(status_code=401, content=response_data)
            return templates.TemplateResponse("shipments.html",{"request":request,"message":"Shipment created successfully"})
        else:
            response_data = {"Shipment Exists Already"}
            if request.headers.get("accept") == "application/json":
                return JSONResponse(status_code=401, content=response_data)
            return templates.TemplateResponse("shipments.html",{"request":request,"message1":"Shipment Exists Already"})
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing parameter: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc
    