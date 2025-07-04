from datetime import datetime, timezone
import json
from typing import List, Union
from pydantic import ValidationError


from app.providers.flights_matrix.utils.flight_quote_model import AirlineData, FlightData, LayoverData, PriceData, Quote, RouteData, SegmentData, FlightSearchProvider, UserQuery



def make_airline_name_lookup(json_file):
    cache = {}

    def get_airline_name(airline_id):
        if not cache:
            # Cache miss: load and index the JSON file
            print("Cache miss: loading data from file...")
            with open(json_file, "r", encoding="utf-8") as f:
                airlines_list = json.load(f)
            # Build the cache as {id: name}
            for item in airlines_list:
                cache[item["id"]] = item["name"]
        if airline_id in cache:
            print(f"Cache hit for {airline_id}")
            return cache[airline_id]
        print(f"Cache miss: {airline_id} not found in data")
        return None

    return get_airline_name


get_airline_name = make_airline_name_lookup("/Users/chimzuruokeokafor/cozn/databricks-mobility-agent/app/providers/airlines.json")

airlines_data = {
    "SK": {
        "name": "Scandinavian Airlines",
        "logo": "https://r-xx.bstatic.com/data/airlines_logo/SK.png"
    },
    "LH": {
        "name": "Lufthansa",
        "logo": "https://r-xx.bstatic.com/data/airlines_logo/LH.png"
    },
    "KL": {
        "name": "KLM",
        "logo": "https://r-xx.bstatic.com/data/airlines_logo/KL.png"
    },
    "BA": {
        "name": "British Airways",
        "logo": "https://r-xx.bstatic.com/data/airlines_logo/BA.png"
    },
    "D8": { 
        "name": "Norwegian Air International",
        "logo": "https://r-xx.bstatic.com/data/airlines_logo/D8.png"
    }
}



def _parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def _format_duration(start_iso: str, end_iso: str) -> str:
    delta_sec = int((_parse_iso(end_iso) - _parse_iso(start_iso)).total_seconds())
    if delta_sec <= 0:
        return "0h 0m"
    hrs, mins = divmod(delta_sec // 60, 60)
    return f"{hrs}h {mins}m"


def serialize_quotes(payload: dict) -> List[Quote]:
    quotes: List[Quote] = []
    currency = payload["currency"]

    for flight in payload["data"]:
        price_data = PriceData(amount=flight["price"], currency=currency)

        # Separate outbound (return==0) and inbound (return==1), sorted by utc_departure
        out_raw = sorted(
            [r for r in flight["route"] if r["return"] == 0],
            key=lambda r: r["utc_departure"],
        )
        in_raw = sorted(
            [r for r in flight["route"] if r["return"] == 1],
            key=lambda r: r["utc_departure"],
        )

        def _mk_segment(r: dict) -> SegmentData:
            dep = RouteData(
                airportCode=r["flyFrom"],
                airportName=r["flyFrom"],
                city=r["cityFrom"],
                date_time=r["local_departure"],
            )
            arr = RouteData(
                airportCode=r["flyTo"],
                airportName=r["flyTo"],
                city=r["cityTo"],
                date_time=r["local_arrival"],
            )
            airline = AirlineData(
                code=r["airline"],
                # name=get_airline_name(r["airline"]),
                name=r["airline"],
                flightNumber=r["flight_no"],
                logo=f"https://r-xx.bstatic.com/data/airlines_logo/{r['airline']}.png"
            )
            duration = _format_duration(r["local_departure"], r["local_arrival"])
            return SegmentData(departure=dep, arrival=arr, airline=airline, duration=duration)

        def _attach_layovers(segments: List[SegmentData]) -> List[SegmentData]:
            # Only if there's more than one segment, we compute layovers
            for i in range(1, len(segments)):
                prev = segments[i - 1]
                curr = segments[i]
                # Calculate layover duration between prev arrival and curr departure
                layover_duration = _format_duration(
                    prev.arrival.date_time, curr.departure.date_time
                )
                if layover_duration != "0h 0m":
                    # Populate layover on the current segment's departure
                    prev.arrival.layover = LayoverData(
                        location=prev.arrival.airportCode,
                        airportName=prev.arrival.airportName,
                        duration=layover_duration,
                    )
            return segments

        outbound_segments = _attach_layovers([_mk_segment(r) for r in out_raw])
        inbound_segments = _attach_layovers([_mk_segment(r) for r in in_raw])

        outbound_flight = FlightData(
            totalDuration=format_seconds_to_duration(flight["duration"]["departure"]),
            segments=outbound_segments,
        )
        inbound_flight = FlightData(
            totalDuration=format_seconds_to_duration(flight["duration"]["return"]),
            segments=inbound_segments,
        )

        try:
            quotes.append(
                Quote(
                    id=flight["id"],
                    provider=FlightSearchProvider.KIWI,
                    price=price_data,
                    outbound=outbound_flight,
                    inbound=inbound_flight,
                    url=flight["deep_link"]
                )
            )
        except ValidationError as ve:
            print(f"[WARN] Quote validation failed for {flight['id']}")
            print(ve.json())

    return quotes



def format_seconds_to_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"{hours} hours {minutes} minutes"




def serialize_booking_quotes(payload: dict) -> List[Quote]:
    quotes = []
    for offer in payload.get("flightOffers", []):
        total = offer["priceBreakdown"]["total"]
        price = PriceData(amount=total["units"] + total["nanos"]/1e9, currency=total["currencyCode"])

        segments = []
        for seg in offer["segments"]:
            for leg in seg["legs"]:
                dep = RouteData(
                    airportCode=leg["departureAirport"]["code"],
                    airportName=leg["departureAirport"]["name"],
                    city=leg["departureAirport"]["cityName"],
                    date_time=leg["departureTime"]
                )
                arr = RouteData(
                    airportCode=leg["arrivalAirport"]["code"],
                    airportName=leg["arrivalAirport"]["name"],
                    city=leg["arrivalAirport"]["cityName"],
                    date_time=leg["arrivalTime"]
                )
                airline = AirlineData(
                    code=leg["flightInfo"]["marketingCarrier"],
                    name=next((c["name"] for c in leg["carriersData"] if c["code"] == leg["flightInfo"]["marketingCarrier"]), ""),
                    flightNumber=leg["flightInfo"]["flightNumber"]
                )
                duration = f"{int(leg['totalTime'] // 3600)}h {int((leg['totalTime'] % 3600) // 60)}m"
                segments.append(SegmentData(departure=dep, arrival=arr, airline=airline, duration=duration))
        
        outbound = FlightData(totalDuration="", segments=segments)
        inbound = FlightData(totalDuration="", segments=[])

        quotes.append(Quote(
            id=offer["token"],
            provider=FlightSearchProvider.BOOKING_COM,
            price=price,
            outbound=outbound,
            inbound=inbound
        ))
    return quotes


def filter_quotes_by_departure(quotes: List[Quote], user_query: UserQuery) -> List[Quote]:
    user_departure_date = datetime.strptime(user_query.departure_date, "%d/%m/%Y").date()
    user_departure_time = datetime.strptime(user_query.departure_time, "%H:%M").time()

    filtered_quotes = []
    for quote in quotes:
        # Get the first segment of the outbound journey (usually the main flight)
        if not quote.outbound.segments:
            continue
        segment = quote.outbound.segments[0]
       
        dt_str = segment.departure.date_time
       
        dt_str_clean = dt_str.replace('Z', '').split('.')[0]
        try:
            departure_dt = datetime.fromisoformat(dt_str_clean)
        except ValueError:
            continue 

        if (departure_dt.date() == user_departure_date and
            departure_dt.time().strftime("%H:%M") == user_departure_time.strftime("%H:%M")):
            filtered_quotes.append(quote)

    return filtered_quotes
