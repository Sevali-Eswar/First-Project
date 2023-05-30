
from pydantic import BaseModel

class User(BaseModel):
    # id:str
    name:str
    email:str
    password: str 
    confirmpassword:str
    role:str="user"

class Shipment(BaseModel):
    ShipmentNumber:int
    ContainerNumber:int
    RouteDetails:str
    GoodsType:str
    Device:str
    ExpectedDeliveryDate:str
    PONumber:int
    DeliveryNumber:int
    NOCNumber:int
    BatchId:int
    SerialNumberOfGoods:int
    ShipmentDescription:str
    email:str





