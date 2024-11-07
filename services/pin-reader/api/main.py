from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from api.logging import init_logging, RouteFilterParams
from api.version import get_version
from api.events import init_listen_thread
from api.event_handlers import event_handler
from api.routers import query_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_logging(suppress_routes=[RouteFilterParams(verb="GET", route="/health")])
    init_listen_thread(str(uuid4()), event_handler)
    yield


app = FastAPI(
    title="Pin Reader API",
    version=get_version(),
    contact={
        "name": "Tucker Beck",
        "url": "https://github.com/dusktreader",
        "email": "tucker.beck@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/dusktreader/shrump/blob/main/services/pin-reader/LICENSE",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(query_router)


@app.get(
    "/health",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "API is healthy"}},
)
async def health_check():
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, err: RequestValidationError):
    logger.error("There was an error serializing a response: {err}")
    raise err
