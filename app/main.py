from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, incidents, routes, risk, sms
from app.services.ml_service import MLService
from app.database.postgres import init_postgres, get_db, create_tables
from app.models.user import User, UserRole
from app.core.security import get_password_hash

app = FastAPI(
    title="AI Traffic Management System",
    description="Smart Traffic & Emergency Response System",
    version="1.0.0",
    docs_url="/docs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OPTIONS handler for preflight
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return {}

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["Routing"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Prediction"])
app.include_router(sms.router, prefix="/api/v1/sms", tags=["SMS Notifications"])

# Startup event - واحد بس
@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("Starting AI Traffic Management System...")
    
    # Initialize database
    init_postgres()
    create_tables()
    print("✅ Tables created (if they didn't exist)")
    
    # Create admin user if not exists
    db = next(get_db())
    admin = db.query(User).filter(User.mobile == "01111111111").first()
    if not admin:
        admin = User(
            mobile="01111111111",
            password_hash=get_password_hash("Admin123!"),
            full_name="System Administrator",
            national_id="11111111111111",
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created")
    
    # Load ML models
    MLService.load_models()
    
    print("Server ready!")
    print("=" * 50)

@app.get("/")
def root():
    return {"message": "AI Traffic Management System API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}