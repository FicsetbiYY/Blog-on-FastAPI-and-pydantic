from fastapi import Depends
from sqlmodel import Field, Session, create_engine, SQLModel
from typing import Final
from Config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES # You have to put your own
import jwt
from datetime import datetime, timedelta
import bcrypt




sqlite_url: Final = f"sqlite:///database.db"
# connect_args is needed for SQLite to work properly with multi-threaded FastAPI
engine: Final = create_engine(sqlite_url, connect_args={"check_same_thread": False})



def get_session():
    with Session(engine) as session:
        yield session
           
        
def create_db_and_tables():
    """Create database tables based on SQLModel schemas."""
    SQLModel.metadata.create_all(engine)
        
        
        
def hash_password(password: str) -> str:
    """Securely hash a password using direct bcrypt library."""
    # Convert string to bytes
    pwd_bytes = password.encode('utf-8')
    
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
        
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against the stored hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False
    



def create_access_token(data: dict) -> str:
    """Generate a secure JWT token containing user data with an expiration time."""
    to_encode = data.copy()
    
    # Calculate when the token expires 
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
