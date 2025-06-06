from pydantic import BaseModel, EmailStr
from datetime import datetime

# This is a Pydantic model that will be used to represent a User
# fetched from the database. It helps with type hinting and validation.
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    xp: int

    class Config:
        # This 'orm_mode' tells Pydantic to read the data even if it
        # is not a dict, but an ORM model (or any other arbitrary object
        # with attributes). This is what allows it to work with the
        # database cursor's results.
        from_attributes = True