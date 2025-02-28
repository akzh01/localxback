from fastapi import APIRouter, HTTPException, Depends
from app.config.database import db
from app.auth.auth import get_current_user, get_admin_user
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# 📌 Pydantic модель для бронирования
class BookingModel(BaseModel):
    id: Optional[str] = None
    tour_id: str
    user_id: Optional[str] = None
    date: str
    status: str = "pending"

# 📌 1. Создать бронирование (только авторизованные пользователи)
@router.post("/", summary="Создать бронирование", operation_id="create_booking", response_model=BookingModel)
async def create_booking(booking: BookingModel, user: dict = Depends(get_current_user)):
    booking_data = booking.dict()
    booking_data["user_id"] = user["id"]
    booking_data["status"] = "pending"
    booking_data["date"] = datetime.strptime(booking.date, "%Y-%m-%dT%H:%M:%S")

    result = await db.bookings.insert_one(booking_data)
    booking_data["id"] = str(result.inserted_id)

    return booking_data

# 📌 2. Получить список бронирований текущего пользователя
@router.get("/", summary="Получить бронирования пользователя", operation_id="get_user_bookings", response_model=List[BookingModel])
async def list_user_bookings(user: dict = Depends(get_current_user)):
    bookings = []
    async for booking in db.bookings.find({"user_id": user["id"]}):
        booking["id"] = str(booking["_id"])
        del booking["_id"]
        bookings.append(booking)
    return bookings

# 📌 3. Получить список всех бронирований (только для админов)
@router.get("/all", summary="Получить все бронирования (админ)", operation_id="get_all_bookings", response_model=List[BookingModel])
async def list_all_bookings(admin: dict = Depends(get_admin_user)):
    bookings = []
    async for booking in db.bookings.find():
        booking["id"] = str(booking["_id"])
        del booking["_id"]
        bookings.append(booking)
    return bookings

# 📌 4. Пользователь отменяет своё бронирование
@router.delete("/{booking_id}", summary="Отменить бронирование", operation_id="cancel_user_booking")
async def cancel_booking(booking_id: str, user: dict = Depends(get_current_user)):
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id), "user_id": user["id"]})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not allowed to cancel")

    await db.bookings.delete_one({"_id": ObjectId(booking_id)})
    return {"message": "Booking canceled"}

# 📌 5. Администратор отменяет любое бронирование
@router.delete("/{booking_id}/admin", summary="Админ отменяет бронирование", operation_id="cancel_admin_booking")
async def cancel_booking_admin(booking_id: str, admin: dict = Depends(get_admin_user)):
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.bookings.delete_one({"_id": ObjectId(booking_id)})
    return {"message": "Booking canceled by admin"}

# 📌 6. Администратор подтверждает бронирование
@router.patch("/{booking_id}/confirm", summary="Подтвердить бронирование", operation_id="confirm_booking_admin")
async def confirm_booking(booking_id: str, admin: dict = Depends(get_admin_user)):
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "confirmed"}}
    )

    return {"message": "Booking confirmed"}