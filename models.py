from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

# Define the Database Model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True) # No duplicate usernames
    hashed_password: str
    
class UserCreate(SQLModel):
    username: str
    password: str 
    
    # What user print:
class PostCreate(SQLModel):
    title: str
    content: str
    
    # What post contain:
class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author: str
    views: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Userlogin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str

class PostUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None