from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Final, List
# from passlib.context import CryptContext
from Config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES # You have to put your own
import jwt
from datetime import datetime, timedelta
import bcrypt




# 2. Setup Database Connection
sqlite_file_name = "database.db"
sqlite_url: Final = f"sqlite:///{sqlite_file_name}"
# connect_args is needed for SQLite to work properly with multi-threaded FastAPI
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})




    
def get_session():
    with Session(engine) as session:
        yield session
        
        
        
def hash_password(password: str) -> str:
    """Securely hash a password using direct bcrypt library."""
    # 1. Convert string to bytes
    pwd_bytes = password.encode('utf-8')
    
    # 2. Manual check: bcrypt strictly forbids > 72 bytes
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
        
    # 3. Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    
    # 4. Return as string to store in DB
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
    
    # Sign the token with our secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
