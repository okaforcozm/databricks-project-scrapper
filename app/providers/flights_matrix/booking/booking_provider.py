""" Flight Search Tool Request.

This module contains the FlightSearchToolRequest class.
"""


from __future__ import annotations
import asyncio
from datetime import datetime
import json
from typing import List
import httpx
from app.providers.flights_matrix.utils.flight_quote_model import Quote, UserQuery
from app.providers.flights_matrix.booking.booking_utils import serialize_booking_quotes
from app.providers.flights_matrix.utils.flight_quote_model import FlightClass
from app.providers.flights_matrix.kiwi.kiwi_utils import filter_quotes_by_departure


def convert_date_to_booking_format(date_str):
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    return dt.strftime("%Y-%m-%d")


class BookingsProviderSearchToolRequest:
    """
    Bookings Provider Search Tool Request.

    Args:
        user_query (UserQuery): The user query.

    Returns:
        List[Quote]: A list of Quote objects.   

    Raises:
        httpx.HTTPError: If the HTTP request fails.
        Exception: If the flight search fails.
    """
    
    def __init__(self, user_query: UserQuery):
        self.user_query: UserQuery = user_query
    

    async def run(self) -> List[Quote]:
        """
        Return a list of ``Quote`` objects. All prices are in GBP.

        Returns:
            List[Quote]: A list of Quote objects.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
            Exception: If the flight search fails.
        """
        # config.logger.info(f"Starting flight search: {self.user_query.origin_city} -> {self.user_query.destination_city} for {self.user_query.num_adults} adults") 

        params = {
            "from": f"{self.user_query.origin_city}.AIRPORT",
            "to": f"{self.user_query.destination_city}.AIRPORT",
            "depart": convert_date_to_booking_format(self.user_query.departure_date),
            # "currency": "GBP",
            "sort": "CHEAPEST",
            "adults": self.user_query.num_adults,
            "children": self.user_query.num_children,
            "infants": self.user_query.num_infants,
            "cabinClass": "ECONOMY" if self.user_query.flight_class == FlightClass.ECONOMY.value else "PREMIUM_ECONOMY" if self.user_query.flight_class == FlightClass.PREMIUM_ECONOMY.value else "BUSINESS" if self.user_query.flight_class == FlightClass.BUSINESS.value else "FIRST",
            "type": "ONEWAY",
            "limit": 20,
            "enableVI": 1,
            "depTimeInt": f"{self.user_query.departure_time}-23:59",
            "airlines": self.user_query.airline,
        }



        try:
            async with httpx.AsyncClient(timeout=20) as client:
                # config.logger.info("Making API request to Booking.com...")
                r = await client.get("https://flights.booking.com/api/flights/", params=params)
                r.raise_for_status()
        
                quotes_data = serialize_booking_quotes(
                    payload=r.json(),
                    title=f"{self.user_query.origin_city}.AIRPORT-{self.user_query.destination_city}.AIRPORT"
                )

                # filtered_quotes = filter_quotes_by_departure(quotes_data, self.user_query)
                
                return quotes_data

        except httpx.HTTPError as e:
            # config.logger.error(f"HTTP error during flight search: {str(e)}")
            raise
        except Exception as e:
            # config.logger.error(f"Unexpected error during flight search: {str(e)}")
            raise