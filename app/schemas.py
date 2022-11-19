from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint


class PostBase(BaseModel):          #pydantic model : schema
    title: str
    content: str            #will throw error when field is not fulfilled
    published: bool = True  #defaults to true if not given a optional value


class PostCreate(PostBase):         #by default inherits all of PostBase fields
    pass                    #accepts everything PostBase


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime    #validates if its a proper datetime
    owner_id: int
    owner: UserOut

    class Config:           #tells pydantic to read the schema even tho its not in a dict B/C its in a ORM (SQLALCHEMY) model
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str




class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):         #ensures all the data that is passed into the token is actually there
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)