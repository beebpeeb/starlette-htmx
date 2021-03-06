from datetime import date, datetime
import json
import logging
import re
from typing import Any, Dict, Literal, Match, Pattern

from babel.dates import format_date
import httpx
import jinja_partials
from pydantic import BaseModel, Field

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


# Config
# ------

app: Starlette = Starlette(debug=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates: Jinja2Templates = Jinja2Templates(directory="templates")

jinja_partials.register_starlette_extensions(templates)


# Models
# ------

regex: Pattern = re.compile(r"(\W+)e.?\s*$", re.MULTILINE)


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
        match: Match | None = regex.search(self.description)
        return bool(match)

    @property
    def stripped_description(self) -> str:
        stripped: str = regex.sub(r"\1", self.description).strip()
        return stripped

    @property
    def time(self) -> str:
        time: str = self.start_time.strftime("%H:%M")
        return time


Schedule = list[Show] | None


# HTTP Client
# -----------

async def get_schedule() -> Schedule:
    async with httpx.AsyncClient() as client:
        try:
            url: str = "https://apis.is/tv/ruv"
            response: httpx.Response = await client.get(url)
            results = response.json().get("results")
            if results is not None:
                return [Show.parse_obj(r) for r in results]
        except (httpx.RequestError, json.JSONDecodeError) as error:
            logging.error(error)
        return None


# Routes
# ------

TemplateContext = Dict[str, Any]


@app.route("/")
async def homepage_route(request: Request) -> Response:
    """Homepage"""
    title: str = "Dagskr?? R??V"
    today: str = format_date(date.today(), format="full", locale="is")
    template: str = "index.html"
    context: TemplateContext = dict(request=request, title=title, today=today)
    return templates.TemplateResponse(template, context)


@app.route("/_htmx/schedule")
async def schedule_route(request: Request) -> Response:
    """Schedule"""
    schedule: Schedule = await get_schedule()
    template: str = "partials/schedule.html"
    context: TemplateContext = dict(request=request, schedule=schedule)
    return templates.TemplateResponse(template, context)


# Server
# ------

if __name__ == "__main__":
    import uvicorn
    host: str = "127.0.0.1"
    port: int = 8080
    uvicorn.run("main:app", host=host, port=port, reload=True)
