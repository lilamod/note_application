## Setup

1. Create a Python 3.8+ virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt

alembic init alembic

uvicorn app.main:app --reload

alembic revision --autogenerate -m "Initial migration"

run testing file  pytest

## env variables
DATABASE_URL=database url
SECRET_KEY=secret key of token 
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=token expire time limit
origins_str=frontend url