from fastapi import FastAPI

from src.auth.router import router as auth_router


app = FastAPI()


@app.get("/", response_model=str, tags=["/"])
def status() -> str:
    return "server is running..."


app.include_router(auth_router)

