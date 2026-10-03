import uuid
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db, engine, Base, SessionLocal
from app.core.logging import logger, ctx_request_id
import app.models  # Crucial: registers all SQLAlchemy models with Base.metadata

# Startup security verification & table initialization
if settings.ENVIRONMENT.lower() == "production":
    if settings.is_insecure_secret():
        logger.critical("FATAL: Insecure SECRET_KEY detected in production environment. Halting startup.")
        raise RuntimeError("FATAL: In production ENVIRONMENT, SECRET_KEY must be set to a cryptographically strong secret with at least 32 characters.")
    logger.info("Production mode active: demo data seeding is strictly disabled.")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Could not verify database schema in production: {e}")
        raise e
else:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified.")
        if settings.ENABLE_DEMO_SEED:
            from app.services.seed_service import seed_demo_environment
            seed_demo_environment(clean_first=False)
    except Exception as e:
        logger.error(f"Could not initialize or seed DB on startup: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request-ID Correlation Middleware for Distributed Observability
class RequestIDCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = ctx_request_id.set(request_id)
        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            ctx_request_id.reset(token)

app.add_middleware(RequestIDCorrelationMiddleware)

# Set up CORS middleware
origins = settings.cors_origins or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in origins],
    allow_origin_regex=r"https://.*\.vercel\.app",
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

    from app.services.metrics_service import metrics_registry
    metrics_snap = metrics_registry.get_metrics_snapshot()
    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "version": "2.1.0",
        "model_version": metrics_snap["model_status"]["model_version"],
        "model_load_status": metrics_snap["model_status"]["model_load_status"],
        "degraded_responses": metrics_snap["degraded_responses"],
        "active_data_source": metrics_snap["model_status"]["active_data_source"]
    }

from app.api.routes import (
    alerts,
    audit,
    auth,
    copilot,
    dashboard,
    investigations,
    models_route,
    settings_route,
    transactions,
    websocket,
    scoring,
    metrics,
)

# Mount routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(scoring.router, prefix=f"{settings.API_V1_STR}/score", tags=["Scoring"])
app.include_router(metrics.router, prefix=f"{settings.API_V1_STR}/metrics", tags=["Metrics"])
app.include_router(transactions.router, prefix=f"{settings.API_V1_STR}/transactions", tags=["Transactions"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_STR}/alerts", tags=["Alerts"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(investigations.router, prefix=f"{settings.API_V1_STR}/investigations", tags=["Investigations"])
app.include_router(copilot.router, prefix=f"{settings.API_V1_STR}/copilot", tags=["Copilot"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit-logs", tags=["Audit"])
app.include_router(models_route.router, prefix=f"{settings.API_V1_STR}/models", tags=["Models"])
app.include_router(settings_route.router, prefix=f"{settings.API_V1_STR}/settings", tags=["Settings"])
app.include_router(websocket.router, tags=["WebSocket"])

# Serve production frontend if available (Unified Full-Stack Deployment)
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

static_dir = os.environ.get("STATIC_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.isdir(static_dir):
    cand = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist"))
    if os.path.isdir(cand):
        static_dir = cand

if os.path.isdir(static_dir):
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend build not found")
