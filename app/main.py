from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, notes, versions
from app.database import engine, Base  
from app.utils.errors import add_exception_handlers
from app.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API with Version History", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(versions.router, prefix="/versions", tags=["Versions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Notes API"}

from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )