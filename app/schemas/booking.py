from pydantic import BaseModel, EmailStr

class BookingSchema(BaseModel):
    name: str
    email: EmailStr
    date: str
    time: str

class BookingResponse(BookingSchema):
    id: str
    session_id: str

    class Config:
        from_attributes = True