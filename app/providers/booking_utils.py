from datetime import datetime
from typing import List, Tuple

from app.providers.flight_quote_model import AirlineData, FlightData, LayoverData, PriceData, Quote, RouteData, SegmentData, FlightSearchProvider

def _parse_iso(ts: str) -> datetime:
    """Parse ISO-8601 string ignoring timezone info (Booking.com gives local)."""
    return datetime.fromisoformat(ts.split("+")[0])

def _fmt(sec: int) -> str:
    h, m = divmod(sec // 60, 60)
    return f"{h}h {m}m"

def _gap(start_iso: str, end_iso: str) -> int:
    """Return lay-over in **seconds** between two ISO stamps (≥0)."""
    return max(0, int((_parse_iso(end_iso) - _parse_iso(start_iso)).total_seconds()))


def serialize_booking_quotes(payload: dict, title: str) -> List[Quote]:
    quotes: List[Quote] = []
    
    # Check if flightOffers exists and is not empty
    flight_offers = payload.get("flightOffers", [])
    if not flight_offers:
        print("Warning: No flight offers found in response")
        return quotes
        
    # Get token from first offer if available
    token = flight_offers[0].get("token", "d6a1f_H4sIAAAAAAAA_y2Qb2-CMBDGP417R6Hlj2NJs2yCm1vBTEHUNw3WCoizG61T-fSrQnq557nf5ZpeS6V-5JNp7g5VUSppnGpQCCWKXHHAxLe5a3TaCFFXx8LMq8Yk05hM5-jxI41NaBr6sKfVM78oQzYMP1QbDnJs-L7fWckw7F2DPeDGWfy2nE7uiAmFHeCN0eJ9PF6SVQcb_G57k8fkXm1xNDqfp-2LjAKpNR1G-2gY16vroi7fZoewTVqp0sNERsk6nl_Pl7iGhAQhSlJ5Z8lIs9QPNYOJ9aXZyrndRYJxQoLZjASsJeH61rdJEBMygtm8GNiBjvsTONMrAOAM_W4Rkct-JcEUhlZntwrPl6n_0XcUth3L7noXDG0P-Q-SHzhTlTh-8ivOXocQGvobT0fkGgnNXpGFDOT39QCNoOOVv2ep3cB-0VFQC1hay15zuv4E4UK7DXXWWhh1b3xLXcSdm-PUtpjWHXV1rigE3eSeTjItLXX-OPT2_6CHc74DAgAA")
    
    for offer in flight_offers:
        total = offer["priceBreakdown"]["total"]
        price = PriceData(
            amount   = total["units"] + total["nanos"] / 1e9,
            currency = total["currencyCode"]
        )

        seg_groups = offer.get("segments", [])
        outbound_raw = [seg_groups[0]] if seg_groups else []
        inbound_raw  = seg_groups[1:] if len(seg_groups) > 1 else []

        def build_legs(raw_segments: List[dict]) -> Tuple[List[SegmentData], int]:
            legs: List[SegmentData] = []
            flight_sec_total = 0
            layover_sec_total = 0

            for seg in raw_segments:
                for leg in seg["legs"]:
                    flight_sec = int(leg.get("totalTime", 0))
                    flight_sec_total += flight_sec

                    dep_air = leg["departureAirport"]
                    arr_air = leg["arrivalAirport"]

                    carrier = leg.get("carriersData", [{}])[0]
                    airline = AirlineData(
                        code         = carrier.get("code", "XX"),
                        name         = carrier.get("name", "UNKNOWN"),
                        flightNumber = int(leg.get("flightInfo", {})
                                              .get("flightNumber", 0)),
                        logo         = f"https://r-xx.bstatic.com/data/airlines_logo/{carrier.get('code', 'XX')}.png"
                    )

                    legs.append(
                        SegmentData(
                            departure = RouteData(
                                airportCode = dep_air.get("code", "UNK"),
                                airportName = dep_air.get("name", "UNKNOWN"),
                                city        = dep_air.get("cityName", dep_air.get("city", "")),
                                date_time   = leg.get("departureTime",
                                                      "1970-01-01T00:00:00")
                            ),
                            arrival   = RouteData(
                                airportCode = arr_air.get("code", "UNK"),
                                airportName = arr_air.get("name", "UNKNOWN"),
                                city        = arr_air.get("cityName", arr_air.get("city", "")),
                                date_time   = leg.get("arrivalTime",
                                                      "1970-01-01T00:00:00")
                            ),
                            airline   = airline,
                            duration  = _fmt(flight_sec)
                        )
                    )

            for i in range(1, len(legs)):
                prev = legs[i - 1]
                curr = legs[i]

                lay_sec = _gap(prev.arrival.date_time, curr.departure.date_time)

                prev.arrival.layover = LayoverData(
                    location    = prev.arrival.airportCode,
                    airportName = prev.arrival.airportName,
                    duration    = _fmt(lay_sec)
                )
                curr.departure.layover = None

            total_sec = flight_sec_total + layover_sec_total
            return legs, total_sec

        outbound_legs, outbound_total = build_legs(outbound_raw)
        inbound_legs,  inbound_total  = build_legs(inbound_raw) if inbound_raw else ([], 0)

        outbound_fd = FlightData(
            totalDuration = _fmt(outbound_total),
            segments      = outbound_legs
        )
        inbound_fd = FlightData(
            totalDuration = _fmt(inbound_total),
            segments      = inbound_legs
        ) if inbound_legs else FlightData(totalDuration="0h 0m", segments=[])

        quotes.append(
            Quote(
                id       = offer.get("token", "UNKNOWN"),
                provider = FlightSearchProvider.BOOKING_COM,
                price    = price,
                outbound = outbound_fd,
                inbound  = inbound_fd,
                url      = f"https://flights.booking.com/flights/{title}/{token}"
            )
        )

    return quotes
