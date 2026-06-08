from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, incidents, routes, risk, sms
from app.services.ml_service import MLService
app = FastAPI(
    title="AI Traffic Management System",
    description="Smart Traffic & Emergency Response System",
    version="1.0.0",
    docs_url="/docs"
)

# CORS - MUST be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow any origin (for development)
    allow_credentials=True,
    allow_methods=["*"],           # Allow GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],           # Allow any headers
)

# OPTIONS handler for preflight (backup)
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return {}

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["Routing"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Prediction"])
app.include_router(sms.router, prefix="/api/v1/sms", tags=["SMS Notifications"])

@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("Starting AI Traffic Management System...")
    MLService.load_models()
    print("Server ready!")
    print("=" * 50)

@app.get("/")
def root():
    return {"message": "AI Traffic Management System API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

