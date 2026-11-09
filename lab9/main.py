"""HTTP/API-слой: маршруты, коды ответов, маппинг доменных ошибок в HTTP."""
import logging
from functools import lru_cache

from fastapi import Depends, FastAPI, Path, Query, Request, Response
from fastapi.responses import JSONResponse

from config import get_settings
from models import CODE_PATTERN, CourseCreate, CourseOut, ErrorOut, RoomUpdate
from repository import (
    DuplicateCourseError,
    MongoCourseRepository,
    RepositoryError,
    StorageUnavailableError,
)
from service import CourseNotFoundError, CourseService

logging.basicConfig(
    level=get_settings().log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("api")

app = FastAPI(title="Lab 9: Courses API (MongoDB)")


# ---------- зависимости (DI) ----------
@lru_cache
def get_repository():
    s = get_settings()
    return MongoCourseRepository(s.mongodb_uri, s.db_name, s.server_selection_timeout_ms)


def get_service(repo=Depends(get_repository)) -> CourseService:
    return CourseService(repo)


CodePath = Path(..., pattern=CODE_PATTERN, description="Код курса, напр. NOSQL301")


# ---------- маппинг ошибок ----------
@app.exception_handler(CourseNotFoundError)
async def _not_found(_: Request, exc: CourseNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Course not found"})


@app.exception_handler(DuplicateCourseError)
async def _duplicate(_: Request, exc: DuplicateCourseError):
    return JSONResponse(status_code=409, content={"detail": "Course with this code already exists"})


@app.exception_handler(StorageUnavailableError)
async def _unavailable(_: Request, exc: StorageUnavailableError):
    return JSONResponse(status_code=503, content={"detail": "Storage temporarily unavailable"})


@app.exception_handler(RepositoryError)
async def _storage_error(_: Request, exc: RepositoryError):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(Exception)
async def _unexpected(_: Request, exc: Exception):
    log.exception("Unhandled error")  # подробности только в серверном логе
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------- endpoints ----------
@app.get("/health")
def health(repo=Depends(get_repository)):
    repo.ping()
    return {"status": "ok"}


@app.post("/courses", response_model=CourseOut, status_code=201,
          responses={409: {"model": ErrorOut}, 422: {}, 503: {"model": ErrorOut}})
def create_course(body: CourseCreate, svc: CourseService = Depends(get_service)):
    return svc.create_course(body.model_dump())


@app.get("/courses", response_model=list[CourseOut])
def list_courses(
    teacher: str | None = Query(None, min_length=2, max_length=80),
    svc: CourseService = Depends(get_service),
):
    return svc.list_courses(teacher)


@app.get("/courses/{code}", response_model=CourseOut,
         responses={404: {"model": ErrorOut}, 503: {"model": ErrorOut}})
def get_course(code: str = CodePath, svc: CourseService = Depends(get_service)):
    return svc.get_course(code)


@app.patch("/courses/{code}/room", response_model=CourseOut,
           responses={404: {"model": ErrorOut}})
def update_room(body: RoomUpdate, code: str = CodePath,
                svc: CourseService = Depends(get_service)):
    return svc.update_room(code, body.room)


@app.delete("/courses/{code}", status_code=204,
            responses={404: {"model": ErrorOut}})
def delete_course(code: str = CodePath, svc: CourseService = Depends(get_service)):
    svc.delete_course(code)
    return Response(status_code=204)
