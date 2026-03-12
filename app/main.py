from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging
import json

from app.config import settings
from app.routers.health import router as health_router
from app.routers.projects import router as projects_router
from app.routers.tasks import router as tasks_router
from app.routers.team import router as team_router
from app.routers.clientes import router as clientes_router
from app.dependencies import verify_api_key
from app.routers.auth import router as auth_router

from app.routers.options import router as options_router

# Setup structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portal.empiezadecero.es"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_dict = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "process_time_ms": round(process_time * 1000, 2)
    }
    logger.info(json.dumps(log_dict))
    
    return response

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(options_router, dependencies=[Depends(verify_api_key)])
app.include_router(tasks_router, dependencies=[Depends(verify_api_key)])
app.include_router(team_router, dependencies=[Depends(verify_api_key)])
app.include_router(projects_router, dependencies=[Depends(verify_api_key)])
app.include_router(clientes_router, dependencies=[Depends(verify_api_key)])
