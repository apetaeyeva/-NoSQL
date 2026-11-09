"""Service-слой: прикладная логика между API и репозиторием."""
from repository import CourseRepository


class CourseNotFoundError(Exception):
    """Курс не найден (доменная ошибка, не HTTP)."""


class CourseService:
    def __init__(self, repo: CourseRepository):
        self.repo = repo

    def create_course(self, data: dict) -> dict:
        return self.repo.create(data)

    def get_course(self, code: str) -> dict:
        item = self.repo.get_by_code(code)
        if item is None:
            raise CourseNotFoundError(code)
        return item

    def list_courses(self, teacher: str | None = None) -> list[dict]:
        return self.repo.list_by_teacher(teacher) if teacher else self.repo.list_all()

    def update_room(self, code: str, room: str) -> dict:
        item = self.repo.update_room(code, room)
        if item is None:
            raise CourseNotFoundError(code)
        return item

    def delete_course(self, code: str) -> None:
        if not self.repo.delete(code):
            raise CourseNotFoundError(code)
