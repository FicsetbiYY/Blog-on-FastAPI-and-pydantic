from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime


# Define the Database Model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True) # No duplicate usernames
    hashed_password: str
    
class UserCreate(SQLModel):
    username: str
    password: str # Plain password
    
    
class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    author: str
    title: str
    content: str
    date_posted: str = Field(default_factory=lambda: datetime.utcnow().strftime("%B %d, %Y"))


class Userlogin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str
