""" Flight Search Tool Request.

This module contains the FlightSearchToolRequest class.
"""


from __future__ import annotations
import os
from typing import List
import httpx
from app.providers.flight_quote_model import Quote, UserQuery
# from app.core.config import config
from app.providers.kiwi_utils import serialize_quotes, filter_quotes_by_departure


KIWI_API_KEY = os.getenv("KIWI_API_KEY")


class KiwiProviderSearchToolRequest:
    """
    Kiwi Provider Search Tool Request.

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
            "fly_from": self.user_query.origin_city,
            "fly_to": self.user_query.destination_city,
            "date_from": self.user_query.departure_date,
            "date_to": self.user_query.departure_date,
            # "flight_type": self.user_query.flight_type,
            "adults": self.user_query.num_adults,
            "select_airlines": self.user_query.airline,
            "dtime_from": self.user_query.departure_time,
            "dtime_to": "23:59",
            "children": self.user_query.num_children,
            "infants": self.user_query.num_infants,
            "enable_vi": True,
            "limit": 20,
        }

        # config.logger.info(f"API request params: {params}")
        
        headers = {"apikey": KIWI_API_KEY}

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                # config.logger.info("Making API request to Kiwi...")
                r = await client.get("https://api.tequila.kiwi.com/v2/search", params=params, headers=headers)
                r.raise_for_status()
        
                quotes_data = serialize_quotes(r.json())

                # filtered_quotes = filter_quotes_by_departure(quotes_data, self.user_query)
                # print(filtered_quotes)
                return quotes_data

        except httpx.HTTPError as e:
            # config.logger.error(f"HTTP error during flight search: {str(e)}")
            raise
        except Exception as e:
            # config.logger.error(f"Unexpected error during flight search: {str(e)}")
            raise