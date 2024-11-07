from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from api.routers import command_router
from api.logging import init_logging, RouteFilterParams
from api.version import get_version


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_logging(suppress_routes=[RouteFilterParams(verb="GET", route="/health")])
    yield


app = FastAPI(
    title="Pin Writer API",
    version=get_version(),
    contact={
        "name": "Tucker Beck",
        "url": "https://github.com/dusktreader",
        "email": "tucker.beck@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/dusktreader/shrump/blob/main/services/pin-writer/LICENSE",
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
app.include_router(command_router)


@app.get(
    "/health",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "API is healthy"}},
)
async def health_check():
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, err: RequestValidationError):
    logger.error("There was an error serializing a response: {err}")
    raise err
