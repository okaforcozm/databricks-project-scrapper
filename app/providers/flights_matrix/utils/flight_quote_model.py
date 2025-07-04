from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class FlightSearchProvider(str, Enum):
    KIWI = "kiwi"
    SKYSCANNER = "skyscanner"
    AMADEUS = "amadeus"
    BOOKING_COM = "booking.com"
    SK = "sk"

class PriceData(BaseModel):
    amount: float
    currency: str

class LayoverData(BaseModel):
    location: str
    airportName: str 
    duration: str

class RouteData(BaseModel):
    airportCode: str
    airportName: str
    city: str
    date_time: str
    layover: Optional[LayoverData] = None


class AirlineData(BaseModel):
    code: str
    name: str
    logo: str
    flightNumber: int


class SegmentData(BaseModel):
    departure: RouteData
    arrival: RouteData
    airline: AirlineData
    duration: str


class FlightData(BaseModel):
    totalDuration: str
    segments: List[SegmentData]

class Quote(BaseModel):
    id: str
    provider: FlightSearchProvider
    price: PriceData
    outbound: FlightData
    inbound: FlightData
    url: str



class FlightClass(str, Enum):
    ECONOMY = "M"
    BUSINESS = "C"
    FIRST = "F"
    PREMIUM_ECONOMY = "W"


class FlightType(str, Enum):
    ONE_WAY = "oneway"
    ROUND_TRIP = "roundtrip"

class UserQuery(BaseModel):
    origin_city: str
    destination_city: str
    airline: str
    departure_time: str
    search_location: str
    num_adults: int
    quoted_price: float
    departure_date: str
    num_children: Optional[int] = 0
    num_infants: Optional[int] = 0
    flight_class: Optional[FlightClass] = FlightClass.ECONOMY.value
    baggage_allowance: Optional[int] = 0
    flight_type: Optional[FlightType] = FlightType.ONE_WAY.value
