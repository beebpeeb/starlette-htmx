from datetime import date, datetime
import json
import logging
import re

from babel.dates import format_date
import httpx
from pydantic import BaseModel, Field, parse_obj_as
from pydantic.dataclasses import dataclass

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Config
# ------

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates: Jinja2Templates = Jinja2Templates(directory="templates")


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
        anystr_strip_whitespace = True

    @property
    def is_repeat(self) -> bool:
        match = regex.search(self.description)
        return bool(match)

    @property
    def stripped_description(self) -> str:
        stripped = regex.sub(r"\1", self.description).strip()
        return stripped

    @property
    def time(self) -> str:
        time = self.start_time.strftime("%H:%M")
        return time


Schedule = list[Show]


# HTTP Client
# -----------


async def get_schedule() -> Schedule:
    async with httpx.AsyncClient() as client:
        schedule = []
        try:
            url: str = "https://apis.is/tv/ruv"
            response: httpx.Response = await client.get(url)
            results = response.json().get("results")
            return [parse_obj_as(Show, r) for r in results]
        except (httpx.RequestError, json.JSONDecodeError) as error:
            logging.error(error)
        return schedule


# Routes
# ------


@app.get("/", response_class=HTMLResponse)
async def homepage_route(request: Request):
    """Homepage"""
    title = "Dagskrá RÚV"
    today = format_date(date.today(), format="full", locale="is")
    template = "index.html"
    context = dict(request=request, title=title, today=today)
    return templates.TemplateResponse(template, context)


@app.get("/_schedule", response_class=HTMLResponse)
async def schedule_route(request: Request):
    """Schedule"""
    schedule: Schedule = await get_schedule()
    template = "_schedule.html"
    context = dict(request=request, schedule=schedule)
    return templates.TemplateResponse(template, context)
