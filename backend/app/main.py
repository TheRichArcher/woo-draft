from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
# from backend.app.routes import auth, players, draft #, results, admin # Uncomment when results & admin routes are implemented
from .routes import auth, players, draft #, results, admin # Use relative import

app = FastAPI(title="Woo Draft API")

# Configure CORS
# Adjust origins as needed for your frontend development and production environments
origins = [
    "http://localhost:3000",  # Example for local frontend development
    "http://localhost:5173",  # Example for local frontend development (Vite)
    # Add your frontend production URL here
    # "https://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(draft.router, prefix="/draft", tags=["draft"])
# app.include_router(results.router, prefix="/results", tags=["results"]) # Uncomment when implemented
# app.include_router(admin.router, prefix="/admin", tags=["admin"])     # Uncomment when implemented

@app.get("/")
def read_root():
    return {"message": "Woo Draft API is running"}

# Add other application setup like database connections, etc.
# from app.core.db import init_db # Changed potential future import to be relative
# @app.on_event("startup")
# async def startup_event():
#     await init_db() 