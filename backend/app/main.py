from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db, engine, Base
from app.core.logging import logger

# Initialize database tables if using sqlite or dev mode
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.warning(f"Could not initialize DB tables on startup: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "version": "1.0.0"
    }

from app.api.routes import auth, transactions, alerts, websocket, dashboard, investigations, copilot

# Mount routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(transactions.router, prefix=f"{settings.API_V1_STR}/transactions", tags=["Transactions"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_STR}/alerts", tags=["Alerts"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(investigations.router, prefix=f"{settings.API_V1_STR}/investigations", tags=["Investigations"])
app.include_router(copilot.router, prefix=f"{settings.API_V1_STR}/copilot", tags=["Copilot"])
app.include_router(websocket.router, tags=["WebSocket"])






