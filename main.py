from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Final, List
from datetime import datetime

# 1. Define the Database Model
class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    author: str
    title: str
    content: str
    date_posted: str = Field(default_factory=lambda: datetime.utcnow().strftime("%B %d, %Y"))

# 2. Setup Database Connection
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
# connect_args is needed for SQLite to work properly with multi-threaded FastAPI
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create database tables based on SQLModel schemas."""
    SQLModel.metadata.create_all(engine)

app: Final = FastAPI()

# Create tables when the application starts
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dependency to get database session for each request
def get_session():
    with Session(engine) as session:
        yield session




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