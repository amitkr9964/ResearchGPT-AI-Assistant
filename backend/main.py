"""ResearchGPT FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import advanced, auth, chat, documents, export, search
from backend.config import get_settings
from backend.database.database import init_db
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_dirs()
    await init_db()
    logger.info("ResearchGPT API started — %s v%s", settings.APP_NAME, settings.APP_VERSION)
    yield
    logger.info("ResearchGPT API shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI Research Assistant with RAG — Upload documents, ask questions, get cited answers.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    origins = settings.CORS_ORIGINS
    if isinstance(origins, str):
        import json
        try:
            origins = json.loads(origins)
        except Exception:
            origins = [o.strip() for o in origins.split(",") if o.strip()]

    allow_all = "*" in origins or not origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else origins,
        allow_credentials=not allow_all,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.API_PREFIX

    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(documents.router, prefix=api_prefix)
    app.include_router(chat.router, prefix=api_prefix)
    app.include_router(search.router, prefix=api_prefix)
    app.include_router(advanced.router, prefix=api_prefix)
    app.include_router(export.router, prefix=api_prefix)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    # Convenience aliases matching spec endpoints
    from backend.api.routers.auth import router as auth_router
    from backend.models.schemas import UserLogin, UserSignup, TokenResponse, UserResponse
    from backend.services.auth_service import AuthService
    from backend.database.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi import Depends

    @app.post("/signup", response_model=UserResponse, status_code=201, tags=["Authentication"])
    async def signup_alias(data: UserSignup, db: AsyncSession = Depends(get_db)):
        user = await AuthService.signup(db, data)
        return AuthService.to_response(user)

    @app.post("/login", response_model=TokenResponse, tags=["Authentication"])
    async def login_alias(data: UserLogin, db: AsyncSession = Depends(get_db)):
        _, token = await AuthService.login(db, data)
        return TokenResponse(access_token=token)

    return app


app = create_app()
