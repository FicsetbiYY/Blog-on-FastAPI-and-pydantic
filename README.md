# Blogging Platform API
Technology stack: FastAPI, PostgreSQL and SQLModel (async engine), JWT authentication.

## Features
- User registration to create a new user
- Login endpoint to authenticate the user and generate a token
- User authorization
  ### User can:
- Create a new blog post

- Update an existing blog post

- Delete an existing blog post

- Get a single blog post

- Get all blog posts

- Filter blog posts by author name


## Installation and Setup

### 1. Clone the repository:
```bash
git clone https://github.com/Ficserbiyy/blog-on-fastapi-and-sqlmodel.git
```

### 2. Install Dependecies using [pip](https://pip.pypa.io/en/stable/):
```bash
pip install fastapi[standard]
pip install pyjwt
pip install bcrypt
pip install sqlmodel
pip install asyncpg
pip install alembic
```

### 3. Launch the PostgreSQL database using [Docker](https://docs.docker.com/get-started/get-docker/):
```Bash
                                            # Your password
docker run --name my-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
```
DATABASE_URL must contain **this** password!

### 4. Create a .env file in the root directory and add Environment Variables:
```.env
SECRET_KEY = "your_key" # Paste your secret key here
ALGORITHM = "HS256"
TOKEN_EXPIRE = 30       # Time after which you want the token to become invalid.

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/postgres
```

### 5. Run the Aplication:
```Bash
fastapi dev main.py
```
### And then go to http://127.0.0.1:8000/docs to see the automatic interactive API documentation.
