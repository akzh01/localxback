from fastapi import FastAPI
from app.routes import users, tours, bookings

app = FastAPI(title="LocalX API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно заменить на URL фронта, если он хостится отдельно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Подключаем маршруты
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tours.router, prefix="/tours", tags=["Tours"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

@app.get("/")
def root():
    return {"message": "Welcome to LocalX API!"}

from app.routes import bookings