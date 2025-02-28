from fastapi import APIRouter, HTTPException
from app.config.database import db
from app.models.tour import Tour
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_tour(tour: Tour):
    tour_dict = tour.dict()
    del tour_dict["id"]
    result = await db.tours.insert_one(tour_dict)
    return {**tour_dict, "id": str(result.inserted_id)}

@router.get("/{tour_id}")
async def get_tour(tour_id: str):
    tour = await db.tours.find_one({"_id": ObjectId(tour_id)})
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    tour["id"] = str(tour["_id"])
    del tour["_id"]
    return tour

@router.get("/")
async def list_tours():
    tours = []
    async for tour in db.tours.find():
        tour["id"] = str(tour["_id"])
        del tour["_id"]
        tours.append(tour)
    return tours
