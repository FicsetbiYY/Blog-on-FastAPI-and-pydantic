from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import Final, List
#from datetime import datetime
from PassLogic import verify_password,create_access_token,hash_password, decode_access_token
from sqlDatabase import get_session, create_db_and_tables, AsyncSession, engine
from contextlib import asynccontextmanager
from models import Post, User, UserCreate, PostRead, PostCreate, PostUpdate
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()    # On Startup
    print('Startup')
    yield
    await engine.dispose()          # On Shutdown
    print('Shutdown')               


app: Final = FastAPI(lifespan=lifespan)
oauth2_scheme: Final = OAuth2PasswordBearer(tokenUrl="login")
origins: Final[list] = [
    "http://localhost",
    "http://localhost:3000", # Common React port
    "http://localhost:5173", # Common Vite/Vue port
    "http://127.0.0.1:5500", # Live Server port
]

# In real production, use the 'origins' list (not the "*") here:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],      # CRUD methods
    allow_headers=["*"]
)





async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    """Dependency to get the currently authenticated user."""
    # token contains username so we get it
    username = decode_access_token(token)
    
    # Searching for a user
    user_result = await session.execute(select(User).where(User.username == username))
    user = user_result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")  
    return user




# FastAPI Endpoints

@app.post("/posts", response_model=Post)
async def create_post(
    post_in: PostCreate, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User ID is missing")
    db_post = Post(**post_in.model_dump(), owner_id=current_user.id)
    
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post


@app.get("/posts", response_model=List[PostRead])
async def get_posts(
    author_name: str | None = None,
    limit: int = 5,
    session: AsyncSession = Depends(get_session)
):
    """Retrieve posts with optional filtering by author and limit."""
    # Basic @app.get('/posts')
    statement = select(Post)
    
    
    if author_name:
        user_result = await session.execute(select(User).where(User.username == author_name))
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Author not found")
        statement = statement.where(Post.owner_id == user.id)

    results = await session.execute(statement.limit(limit))
    posts=results.scalars().all()
    return posts



@app.get("/posts/{post_id}", response_model=Post)
async def get_single_post(post_id: int, session: AsyncSession = Depends(get_session)):
    """Retrieve a single post by its ID."""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post



@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific post from the database."""
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    
    if Post.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You are not the author of this post!"
        )
    
    
    await session.delete(post)
    await session.commit()
    return {"message": f"Post successfully deleted"}



# Accept UserCreate and return User
@app.post("/register", ) 
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user with checked password validation."""
    secure_hash = hash_password(user_in.password)
    
    db_user = User(
        username=user_in.username,
        hashed_password=secure_hash
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@app.post('/login')
async def log_in(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_session)
):
    statement = select(User).where(User.username == form_data.username)
    db_user_result = await session.execute(statement)
    db_user = db_user_result.scalars().first()
    
    
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.patch("/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: int, 
    post_data: PostUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_post = await session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You are not the author!")

    # exclude_unset=True means only one(title or content of the post) is required
    update_dict = post_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        setattr(db_post, key, value)

    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post
