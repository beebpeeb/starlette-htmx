from datetime import date, datetime
import json
import logging
import re

from babel.dates import format_date
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel, Field, parse_obj_as
from pydantic.dataclasses import dataclass


app = FastAPI()

templates = Jinja2Templates(directory="templates")

regex = re.compile(r"(\W+)e.?\s*$", re.MULTILINE)


class Listing(BaseModel):
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


Listings = list[Listing]


async def get_listings() -> Listings:
    async with httpx.AsyncClient() as client:
        listings = []
        try:
            url = "https://apis.is/tv/ruv"
            response = await client.get(url)
            results = response.json().get("results")
            return [parse_obj_as(Listing, listing) for listing in results]
        except (httpx.RequestError, json.JSONDecodeError) as error:
            logging.error(error)
        return listings


@app.get("/", response_class=HTMLResponse)
def homepage_route(request: Request):
    title = "Dagskrá RÚV"
    today = format_date(date.today(), format="full", locale="is")
    template = "index.html"
    context = dict(request=request, title=title, today=today)
    return templates.TemplateResponse(template, context)


@app.get("/_listings", response_class=HTMLResponse)
async def listings_route(request: Request):
    listings: Listings = await get_listings()
    template = "_listings.html"
    context = dict(request=request, listings=listings)
    return templates.TemplateResponse(template, context)
