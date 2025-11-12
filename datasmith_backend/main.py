import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from src.api.chat_controller import router as chat_router
from src.utils.logger import Logger
from src.constants.environment_constants import EnvironmentConstants
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


load_dotenv(".env")

Path("src/logs").mkdir(parents=True, exist_ok=True)
Path("src/data").mkdir(parents=True, exist_ok=True)
Path("src/vector_db").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Logger.log_info_message("Starting Post-Discharge Medical AI Assistant...")
    Logger.log_info_message(f"Mode: {EnvironmentConstants.APP_MODE.value}")
    Logger.log_info_message(f"Port: {EnvironmentConstants.PORT.value}")
    yield
    Logger.log_info_message("Shutting down Post-Discharge Medical AI Assistant...")

app = FastAPI(
    title="Post-Discharge Medical AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)


origins = [
    "http://localhost:8501",  # Streamlit default  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = [
        {"field": e.get("loc", ["unknown"])[-1], "message": e.get("msg")}
        for e in exc.errors()
    ]
    Logger.log_error_message(exc, "Validation error in request")
    return JSONResponse(
        status_code=400,
        content={"message": "Invalid request payload.", "errors": errors},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    Logger.log_error_message(exc, "Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error. Please try again."},
    )


@app.get("/api/v1/")
async def health_check():
    return {"status": "online", "service": "Post-Discharge Medical AI Assistant","version": "1.0.0"}


app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    Logger.log_info_message(f"Starting server on http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True,log_level="info")