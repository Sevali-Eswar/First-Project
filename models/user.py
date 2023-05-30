<<<<<<< HEAD
from pydantic import BaseModel,Field
=======
from pydantic import BaseModel
>>>>>>> origin/master

class User(BaseModel):
    # id:str
    name:str
    email:str
<<<<<<< HEAD
    password:str
=======
    password: str 
>>>>>>> origin/master
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





