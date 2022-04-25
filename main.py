from datetime import date, datetime
from json import JSONDecodeError
import logging
import re
from typing import Literal

from babel.dates import format_date
from httpx import AsyncClient, RequestError
import jinja_partials
from pydantic import BaseModel, Field

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


# Config
# ------

app = Starlette(debug=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

jinja_partials.register_starlette_extensions(templates)

API_URL: str = "https://apis.is/tv/ruv"


# Models
# ------

regex = re.compile(r"(\W+)e.?\s*$", re.MULTILINE)


class Show(BaseModel):
    """Pydantic model representing a TV show listing."""
    description: str
    is_live: bool = Field(..., alias="live")
    start_time: datetime = Field(..., alias="startTime")
    title: str

    class Config:
        anystr_strip_whitespace: Literal[True, False] = True

    @property
    def is_repeat(self) -> Literal[True, False]:
        return bool(regex.search(self.description))

    @property
    def stripped_description(self) -> str:
        return regex.sub(r"\1", self.description).strip()

    @property
    def time(self) -> str:
        return self.start_time.strftime("%H:%M")


# HTTP Client
# -----------

async def get_schedule() -> list[Show] | None:
    async with AsyncClient() as client:
        try:
            response = await client.get(API_URL)
            results = response.json().get("results")
            if results is not None:
                return [Show.parse_obj(r) for r in results]
        except (RequestError, JSONDecodeError) as error:
            logging.error(error)
        return None


# Routes
# ------

@app.route("/")
async def homepage_route(request: Request) -> Response:
    """Homepage"""
    title = "Dagskrá RÚV"
    today = format_date(date.today(), format="full", locale="is")
    template = "index.html"
    context = dict(request=request, title=title, today=today)
    return templates.TemplateResponse(template, context)


@app.route("/_htmx/schedule")
async def schedule_route(request: Request) -> Response:
    """Schedule"""
    schedule = await get_schedule()
    template = "partials/schedule.html"
    context = dict(request=request, schedule=schedule)
    return templates.TemplateResponse(template, context)


# Server
# ------

if __name__ == "__main__":
    import uvicorn
    host: str = "127.0.0.1"
    port: int = 8080
    uvicorn.run("main:app", host=host, port=port, reload=True)
