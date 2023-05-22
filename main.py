from datetime import date, datetime
from json import JSONDecodeError
import logging

from babel.dates import format_date
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient, RequestError
from pydantic import BaseModel, Field, parse_obj_as


class Listing(BaseModel):
    description: str
    is_live: bool = Field(..., alias="live")
    start_time: datetime = Field(..., alias="startTime")
    title: str

    class Config:
        anystr_strip_whitespace = True

    @property
    def is_repeat(self) -> bool:
        return self.description.endswith(" e.")

    @property
    def stripped_description(self) -> str:
        return self.description.rstrip(" e.")

    @property
    def time(self) -> str:
        return self.start_time.strftime("%H:%M")


Listings = list[Listing]


async def get_listings() -> Listings:
    async with AsyncClient() as client:
        listings = []
        try:
            response = await client.get("https://apis.is/tv/ruv")
            results = response.json()["results"]
            listings = [parse_obj_as(Listing, listing) for listing in results]
        except (RequestError, JSONDecodeError, LookupError) as error:
            logging.error(error)
        return listings


app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def homepage_route(request: Request):
    title = "Dagskrá RÚV"
    today = format_date(date.today(), format="full", locale="is")
    context = dict(request=request, title=title, today=today)
    return templates.TemplateResponse("index.html", context)


@app.get("/_listings", response_class=HTMLResponse)
async def listings_route(request: Request):
    listings = await get_listings()
    context = dict(request=request, listings=listings)
    return templates.TemplateResponse("_listings.html", context)
