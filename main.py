from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, create_engine, select
from typing import Final, List
#from datetime import datetime
from PassLogic import verify_password,create_access_token,hash_password,get_session, create_db_and_tables, decode_access_token
from contextlib import asynccontextmanager
from models import Post, User, UserCreate, PostRead, PostCreate, PostUpdate
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# Create tables on Startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On Startup:
    create_db_and_tables()
    yield
    # On Shutdown:


app: Final = FastAPI(lifespan=lifespan)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """Dependency to get the currently authenticated user."""
    # token contains username so we get it
    username = decode_access_token(token)
    
    # Searching for a user
    user = session.exec(select(User).where(User.username == username)).first()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")  
    return user




# FastAPI Endpoints

@app.post("/posts", response_model=Post)
def create_post(
    post_in: PostCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User ID is missing")
    db_post = Post(**post_in.model_dump(), owner_id=current_user.id)
    
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.get("/posts", response_model=List[PostRead])
def get_posts(
    author_name: str | None = None,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    """Retrieve posts with optional filtering by author and limit."""
    # Basic @app.get('/posts')
    statement = select(Post)
    
    
    if author_name:
        user = session.exec(select(User).where(User.username == author_name)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Author not found")
        statement = statement.where(Post.owner_id == user.id)

    results = session.exec(statement.limit(limit)).all()
    return results



@app.get("/posts/{post_id}", response_model=Post)
def get_single_post(post_id: int, session: Session = Depends(get_session)):
    """Retrieve a single post by its ID."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post



@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific post from the database."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    
    if Post.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You are not the author of this post!"
        )
    
    
    session.delete(post)
    session.commit()
    return {"message": f"Post successfully deleted"}



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


@app.post('/login')
def log_in(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == form_data.username)
    db_user = session.exec(statement).first()
    
    
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.patch("/posts/{post_id}", response_model=Post)
def update_post(
    post_id: int, 
    post_data: PostUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You are not the author!")

    # exclude_unset=True means only one(title or content of the post) is required
    update_dict = post_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(db_post, key, value)

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post
