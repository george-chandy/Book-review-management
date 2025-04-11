from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
from src.admin.book_management.router import router as book_router


app = FastAPI()


@app.get("/", response_model=str, tags=["/"])
def status() -> str:
    return "server is running..."


app.include_router(auth_router)
app.include_router(book_router)

