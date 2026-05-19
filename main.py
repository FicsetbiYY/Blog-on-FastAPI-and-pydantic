from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Final, List
from datetime import datetime
from PassLogic import verify_password,create_access_token,hash_password,engine,get_session
from contextlib import asynccontextmanager
from models import Post, User, UserCreate




def create_db_and_tables():
    """Create database tables based on SQLModel schemas."""
    SQLModel.metadata.create_all(engine)




# Create tables when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs WHEN THE SERVER STARTS
    create_db_and_tables()
    yield
    # This code runs WHEN THE SERVER SHUTS DOWN (if needed)

app: Final = FastAPI(lifespan=lifespan)






# 3. FastAPI Endpoints

@app.post("/posts", response_model=Post)
def create_post(post: Post, session: Session = Depends(get_session)):
    """Create a new post and save it to the database."""
    session.add(post)
    session.commit()
    session.refresh(post) # Fetch the generated ID from the database
    return post



@app.get("/posts", response_model=List[Post])
def get_posts(session: Session = Depends(get_session)):
    """Retrieve all posts from the database."""
    statement = select(Post)
    posts = session.exec(statement).all()
    return posts



@app.get("/posts/{post_id}", response_model=Post)
def get_single_post(post_id: int, session: Session = Depends(get_session)):
    """Retrieve a single post by its ID."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post



@app.delete("/posts/{post_id}")
def delete_post(post_id: int, session: Session = Depends(get_session)):
    """Delete a specific post from the database."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return {"message": f"Post {post_id} successfully deleted"}



@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, updated_data: Post, session: Session = Depends(get_session)):
    """Update an existing post in the database."""
    # Fetch the post from the database by ID
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Overwrite old database values with new data from the request
    db_post.title = updated_data.title
    db_post.content = updated_data.content
    db_post.author = updated_data.author
    
    # Save the updated object
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    
    return db_post


# Accept UserCreate and return User
@app.post("/register", ) #response_model=User)
def register_user(user_in: UserCreate, session: Session = Depends(get_session)):
    """Register a new user with checked password validation."""
    secure_hash = hash_password(user_in.password)
    
    db_user = User(
        username=user_in.username,
        hashed_password=secure_hash
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.post('/login', response_model=UserCreate)
def log_in(user_data: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user_data.username)
    db_user = session.exec(statement).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")    
    
    verified_password = verify_password(user_data.password, db_user.hashed_password)
    if not verified_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = create_access_token(data={"sub": db_user.username})
    
    # Return the token to the client
    return {"access_token": token, "token_type": "bearer"}
