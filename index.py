from fastapi import FastAPI
from routes.user import user
from routes.shipment import shipment
from routes.data_stream import data_stream
app=FastAPI()

app.include_router(user)
app.include_router(shipment)
app.include_router(data_stream)

