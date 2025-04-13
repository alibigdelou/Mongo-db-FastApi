from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional
from bson.json_util import dumps
from pydantic import BaseModel

client = MongoClient("xxxx")

db = client["g7"]  
properties_collection = db["Properties"]
contracts_collection = db["Contracts"]
payments_collection = db["Payments"]
users_collection = db["Users"]

app = FastAPI()


def convert_objectid(data):
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    return data

@app.get("/properties")
async def get_all_properties():
    try:
        properties = list(properties_collection.find())
        if not properties:
            raise HTTPException(status_code=404, detail="No properties found")
        return {"properties": convert_objectid(properties)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contracts")
async def get_all_contracts():
    try:
        contracts = list(contracts_collection.find())
        if not contracts:
            raise HTTPException(status_code=404, detail="No contracts found")
        return {"contracts": convert_objectid(contracts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users")
async def get_all_users():
    try:
        users = list(users_collection.find())
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return {"users": convert_objectid(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payments")
async def get_all_payments():
    try:
        payments = list(payments_collection.find())
        if not payments:
            raise HTTPException(status_code=404, detail="No payments found")
        return {"payments": convert_objectid(payments)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/properties/search")
async def search_properties(
    property_type: Optional[str] = None, 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None, 
    neighborhood: Optional[str] = None
):
    try:
        query = {}
        if property_type:
            query["type"] = property_type
        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price
        if neighborhood:
            query["location.neighborhood"] = neighborhood

        properties = list(properties_collection.find(query))
        if not properties:
            raise HTTPException(status_code=404, detail="No matching properties found")
        return {"properties": convert_objectid(properties)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contracts/{contract_id}/payments")
async def get_payments_by_contract(contract_id: int):
    try:
        payments = list(payments_collection.find({"contract_id": contract_id}))
        if not payments:
            raise HTTPException(status_code=404, detail="No payments found for this contract")
        return {"payments": convert_objectid(payments)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/properties/{property_id}/visits")
async def get_visits_by_property(property_id: int):
    try:
        property_data = properties_collection.find_one({"_id": property_id})
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        visits = property_data.get("visits", [])
        return {"visits": convert_objectid(visits)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class Property(BaseModel):
    _id: int
    type: str
    price: float
    location: dict
    size: float
    bedrooms: int
    bathrooms: int
    features: list
    available: bool
    agent: dict
    visits: list

class Contract(BaseModel):
    _id: int
    property_id: int
    agent_id: int
    contract_date: str
    price: float
    status: str
    customer_info: dict
    payment: dict


@app.post("/properties/add")
async def add_property(property: Property):
    try:
        if properties_collection.find_one({"_id": property._id}):
            raise HTTPException(status_code=400, detail="Property with this ID already exists")
        
        properties_collection.insert_one(property.dict())
        return {"message": "Property added successfully", "property": property}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contracts/add")
async def add_contract(contract: Contract):
    try:
        if contracts_collection.find_one({"_id": contract._id}):
            raise HTTPException(status_code=400, detail="Contract with this ID already exists")
        
        contracts_collection.insert_one(contract.dict())
        return {"message": "Contract added successfully", "contract": contract}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))