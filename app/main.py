from __future__ import annotations

import os
import json
from datetime import datetime, timedelta, date, timezone
from typing import List, Optional, Dict

import redis.asyncio as redis
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field, constr

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r: redis.Redis = redis.from_url(REDIS_URL, decode_responses=True)

class RedisJSON:
    def __init__(self, client: redis.Redis):
        self.client = client

    async def set(self, name: str, value: dict):
        await self.client.execute_command("JSON.SET", name, "$", json.dumps(value))

    async def get(self, name: str) -> Optional[dict]:
        raw = await self.client.execute_command("JSON.GET", name)
        return json.loads(raw) if raw else None

jsondb = RedisJSON(r)

class City(BaseModel):
    region: str
    country_code: str
    state: Optional[str] = None
    country_name: str
    city_name: str


class AirportMapping(BaseModel):
    city_name: str
    airport_code: str


class Flight(BaseModel):
    origin_airport: str
    destination_airport: str
    date: date 
    departure_time: str  
    arrival_time: str  
    airline_code: str
    cabin_bags: int = Field(ge=0)
    checked_bags: int = Field(ge=0)
    stops: int = Field(ge=0)
    price: float
    currency: str
    scraped_at: datetime


class MomondoFlight(BaseModel):
    origin: str
    destination: str
    dep_time: str 
    arr_time: str  
    airline: str
    stops: int
    price: float
    currency: str
    cabin_bags: int
    checked_bags: int


app = FastAPI(title="Databricks Flight Price Tracker")

@app.post("/cities", status_code=status.HTTP_201_CREATED)
async def add_cities(cities: List[City]):
    """Bulk‑insert City rows and cache their schemas in Redis."""
    for c in cities:
        await jsondb.set(f"city:{c.city_name}", c.dict())
        await r.sadd("cities", c.city_name)
    return {"inserted": len(cities)}


@app.post("/airport-mappings", status_code=status.HTTP_201_CREATED)
async def add_airports(mappings: List[AirportMapping]):
    for m in mappings:
        await r.sadd(f"airports:{m.city_name}", m.airport_code)
    return {"inserted": len(mappings)}


@app.post("/scrape-routes", status_code=status.HTTP_202_ACCEPTED)
async def scrape_routes(
    origins: List[str],
    destinations: List[str],
    background_tasks: BackgroundTasks,
):
    """Kick‑off async scrape for all origin/destination pairs."""
    if not origins or not destinations:
        raise HTTPException(status_code=400, detail="origin and destination lists required")
    background_tasks.add_task(run_scraper, origins, destinations)
    return {"status": "queued", "pairs": len(origins) * len(destinations)}


async def run_scraper(origins: List[str], destinations: List[str]):
    """Loop through all requested pairs and three departure dates."""
    today = datetime.now().date()
    schedule = {
        "tomorrow": today + timedelta(days=1),
        "one_month": today + timedelta(days=30),
        "three_months": today + timedelta(days=90),
    }

    for origin in origins:
        for dest in destinations:
            if origin == dest:
                continue
            for label, dep_date in schedule.items():
                await ensure_proxy_for_origin(origin)
                flights = await query_momondo_placeholder(origin, dest, dep_date)
                for mf in flights:
                    flight = Flight(
                        origin_airport=mf.origin,
                        destination_airport=mf.destination,
                        date=dep_date,
                        departure_time=mf.dep_time,
                        arrival_time=mf.arr_time,
                        airline_code=mf.airline,
                        cabin_bags=mf.cabin_bags,
                        checked_bags=mf.checked_bags,
                        stops=mf.stops,
                        price=mf.price,
                        currency=mf.currency,
                        scraped_at=datetime.now(timezone.utc),
                    )
                    await save_flight(flight)


async def save_flight(flight: Flight):
    # Key == flight:<orig>-<dest>:<date>:<epoch>
    ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    key = f"flight:{flight.origin_airport}-{flight.destination_airport}:{flight.date.isoformat()}:{ts}"
    await jsondb.set(key, flight.model_dump())

async def query_momondo_placeholder(origin: str, dest: str, dep_date: date) -> List[MomondoFlight]:
    """Return *mocked* Momondo response for development/testing.

    Replace this with a real scraper or official API integration in production.
    We hard‑code a single direct flight below. Extend as needed.
    """
    sample: Dict = {
        "origin": origin,
        "destination": dest,
        "dep_time": "12:30",
        "arr_time": "18:45",
        "airline": "QF", 
        "stops": 0,
        "price": 299.99,
        "currency": "AUD",
        "cabin_bags": 1,
        "checked_bags": 1,
    }
    return [MomondoFlight(**sample)]


async def ensure_proxy_for_origin(origin_airport: str):
    """Placeholder for geo‑IP logic.

    In production, plug in a proxy‑rotation pool where each proxy roughly
    matches the country/region of `origin_airport`. No‑op for now.
    """
    return  

@app.get("/health")
async def health():
    try:
        pong = await r.ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"redis": bool(pong), "status": "ok"}
