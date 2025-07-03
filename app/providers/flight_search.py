import asyncio
import json
import random
from datetime import datetime
from typing import List, Dict, Optional
from app.providers.booking_provider import BookingsProviderSearchToolRequest
from app.providers.flight_quote_model import Quote, UserQuery, FlightSearchProvider
from app.providers.kiwi_provider import KiwiProviderSearchToolRequest
from app.tasks import _go



async def process_screenshots(all_quotes: List[Quote]) -> Dict[str, str]:
    """
    Process screenshots for selected quotes from each provider.
    Takes up to 2 quotes per provider for screenshots.
    Returns a dictionary mapping quote IDs to screenshot URLs.
    """
    screenshot_urls = {}
    
    # Group quotes by provider
    quotes_by_provider: Dict[FlightSearchProvider, List[Quote]] = {}
    for quote in all_quotes:
        if quote.provider not in quotes_by_provider:
            quotes_by_provider[quote.provider] = []
        quotes_by_provider[quote.provider].append(quote)
    
    # Take screenshots for selected quotes
    for provider, quotes in quotes_by_provider.items():
        # Select up to 2 quotes randomly
        num_to_select = min(2, len(quotes))
        if num_to_select > 0:
            selected_quotes = random.sample(quotes, num_to_select)
            
            for quote in selected_quotes:
                try:
                    # Set accept_cookies based on provider
                    accept_cookies = False if quote.provider == FlightSearchProvider.BOOKING_COM else True
                    
                    # Use the async _go function directly
                    screenshot_result = await _go(quote.url, accept_cookies=accept_cookies)
                    print(f"Screenshot result for {quote.provider.value}")
                    
                    # Extract screenshot URL from the result
                    if 'screenshot_url' in screenshot_result:
                        screenshot_urls[quote.id] = screenshot_result['screenshot_url']
                        print(f"Screenshot saved for quote")
                    else:
                        print(f"No screenshot URL returned for quote {quote.id}")
                        
                except Exception as e:
                    print(f"Failed to take screenshot for quote {quote.id}: {e}")
    
    return screenshot_urls


def format_quote_data(quote: Quote, screenshot_urls: Dict[str, str] = None, region_info: Dict[str, str] = None, user_query: UserQuery = None) -> Dict:
    """
    Format quote data according to the specified structure.
    """
    # Get the first outbound segment for departure info
    departure_segment = quote.outbound.segments[0] if quote.outbound.segments else None
    # Get the last outbound segment for arrival info
    arrival_segment = quote.outbound.segments[-1] if quote.outbound.segments else None
    
    if not departure_segment or not arrival_segment:
        return {}
    
    # Parse departure datetime
    dep_dt = datetime.fromisoformat(departure_segment.departure.date_time.replace('Z', '').split('.')[0])
    arr_dt = datetime.fromisoformat(arrival_segment.arrival.date_time.replace('Z', '').split('.')[0])
    
    # Calculate number of stops (segments - 1)
    num_stops = len(quote.outbound.segments) - 1
    
    # Calculate total flight time from duration
    total_duration = quote.outbound.totalDuration
    
    return {
        "departure_airport": departure_segment.departure.airportCode,
        "destination_airport": arrival_segment.arrival.airportCode,
        "departure_city": departure_segment.departure.city,
        "destination_city": arrival_segment.arrival.city,
        "origin_city_region": region_info.get("origin_city_region", "UNKNOWN") if region_info else "UNKNOWN",
        "destination_city_region": region_info.get("destination_city_region", "UNKNOWN") if region_info else "UNKNOWN",
        "flight_date": dep_dt.strftime("%Y-%m-%d"),
        "departure_time": dep_dt.strftime("%H:%M"),
        "arrival_time": arr_dt.strftime("%H:%M"),
        "total_flight_time": total_duration,
        "airline_code": departure_segment.airline.code,
        "cabin_bags": 0,  # Default value, can be updated based on actual data
        "checked_bags": 0,  # Default value, can be updated based on actual data
        "num_stops": num_stops,
        "price": quote.price.amount,
        "currency": quote.price.currency,
        "num_adults": user_query.num_adults,
        "num_children": user_query.num_children,
        "num_infants": user_query.num_infants,
        "passenger_type": f"{user_query.num_adults}A_{user_query.num_children}C_{user_query.num_infants}I",
        "scraping_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": quote.provider.value,
        "screenshot_url": screenshot_urls.get(quote.id) if screenshot_urls else None,
        "booking_url": quote.url
    }


async def flight_search(
    user_query: UserQuery, 
    region_info: Dict[str, str] = None
) -> List[Quote]:
    
    kiwi = KiwiProviderSearchToolRequest(user_query)
    booking = BookingsProviderSearchToolRequest(user_query)

    try:
        results: List[List[Quote]] = await asyncio.wait_for(
            asyncio.gather(kiwi.run(), booking.run()),
            timeout=30.0
        )

        all_quotes = [quote for provider_quotes in results for quote in provider_quotes]
        
        # Take screenshots of selected quotes
        screenshot_urls = await process_screenshots(all_quotes)
        
        # Format the quote data according to specifications
        formatted_quotes = []
        for quote in all_quotes:
            formatted_data = format_quote_data(quote, screenshot_urls, region_info, user_query)
            if formatted_data:  # Only include if formatting was successful
                formatted_quotes.append(formatted_data)
       
        return formatted_quotes
    
    except Exception as err:
        raise err


# if __name__ == "__main__":
#     results = asyncio.run(flight_search(UserQuery(
#         origin_city="LON",
#         destination_city="PAR",
#         departure_date="01/07/2025",
#         departure_time="10:00",
#         airline="",
#         search_location="",
#         quoted_price=0.0,
#         num_adults=1,
#         num_children=0,
#         num_infants=0,
#     )))
#     print(json.dumps(results, indent=2))