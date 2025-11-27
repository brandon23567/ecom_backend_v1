from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.authentication.routes import router as auth_routes
from src.products.routes import router as products_routes

app = FastAPI(
    title="Ecomm website backend",
    description="This is the backend for our first ecom so we integrate with the frontend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_routes)
app.include_router(products_routes)

@app.get("/")
def home_root():
    return { "message": "This is the main home root" }