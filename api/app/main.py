from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include user routes
app.include_router(user.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Intelligent Portfolio API"}
