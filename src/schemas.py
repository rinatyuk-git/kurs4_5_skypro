from pydantic import BaseModel, Field


class Employer(BaseModel):
    name: str
    vacancies_url: str
    open_vacancies: int


class Salary(BaseModel):
    from_: float | None = Field(default=None, alias='from')
    to: float | None = None
    currency: str


class Vacancies(BaseModel):
    name: str
    salary: Salary | None = None
    alternate_url: str
    employer_id: int | None = None
