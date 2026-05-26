from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define the Database Models

class Settings(BaseSettings):
    DATABASE_URL: str = ''
    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'
    TOKEN_EXPIRE: int = 30
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True) # No duplicate usernames
    hashed_password: str
    posts: list["Post"] = Relationship(back_populates="owner")
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
    owner_id: int = Field(foreign_key='user.id')
    views: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner: "User" = Relationship(back_populates="posts")

class Userlogin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str

class PostUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    
class UserPublic(SQLModel):
    id: int
    username: str

class PostRead(SQLModel):
    id: int
    title: str
    content: str
    owner_id: int
    owner: UserPublic | None = None

settings = Settings() 