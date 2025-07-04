import asyncio
import json
import aiohttp
from app.utils.model import FreightosQuotesResponse, FreightosRequestPayload

FREIGHTOS_USER_COOKIES = "handlID=92852469965; handl_ref_domain=; handl_landing_page_base=https://www.freightos.com/; traffic_source=Direct; first_traffic_source=Direct; server-version-cookie=y25w24-release.1749630721000|; i18next=en; handl_original_ref=https%3A%2F%2Fship.freightos.com%2F; handl_landing_page=https%3A%2F%2Fwww.freightos.com%2Fwp-content%2Fuploads%2F2018%2F04%2Fcropped-favicon-512x512-Freighots-32x32.png; handl_ref=https%3A%2F%2Fship.freightos.com%2F; handl_url_base=https%3A%2F%2Fwww.freightos.com%2Fwp-content%2Fuploads%2F2018%2F04%2Fcropped-favicon-512x512-Freighots-32x32.png; handl_url=https%3A%2F%2Fwww.freightos.com%2Fwp-content%2Fuploads%2F2018%2F04%2Fcropped-favicon-512x512-Freighots-32x32.png; user_agent=Mozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F137.0.0.0%20Safari%2F537.36; organic_source=https%3A%2F%2Fship.freightos.com%2F; organic_source_str=Other; intercom-id-hwrb8vsu=84d5dfdf-01de-4610-ac59-2cceb47a176d; intercom-device-id-hwrb8vsu=49d67dd8-4587-4c5d-bcb2-17d430cda0b8; HandLtestDomainNameServer=HandLtestDomainValueServer; handl_ip=5.151.198.139; prefs=en|null|GBP|true|GB|0|kg|cm|cbm|cm3_kg|days||W48|YES|false|Freight||cbm|kg|false|false; intercom-session-hwrb8vsu=emlmUmdWR2E5c2xBYjZrRGRxKzZmM1Z3d0UxWE9QeG50ZUR5RE9FVHprWmpBTnI1cUNDSXRLd2ZtaDVPM1VleklsakYxR0FCWmI2R1hYOTZLSGQvTkYzem1DWFY5akpyK3RNUmUveDlmejQ9LS1Zc1JjRHFzdW1ISkdEeVRkaHBRdCtRPT0=--d9843bc58cd8bbe1a1a4ee6c9adf7c4f77cb06a1; session=okafor%40thecozm.com|agpzfnRyYWRlb3Mxch0LEhB1c2VyL0xlZ2FsRW50aXR5GICA6vCFiaoLDA|Okafor+Okafor||1750517761132|1753109761132|yT_32N3EdG4Tvn16XsqHMUfTciA|true|false||false|BuyQuotes+MarketplaceShipper+Buying|BusinessAdmin||||7204968168%3AagpzfnRyYWRlb3Mxch0LEhB1c2VyL0xlZ2FsRW50aXR5GICA6rCyp-kLDA%2CBuyQuotes%2BBuying%2BMarketplaceShipper|V2|v-qdF8g9ijcq1QqmMEa_6-i9Q_k"

def make_freightos_headers():
    return {
        "Cookie": FREIGHTOS_USER_COOKIES,
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://ship.freightos.com",
    }

async def make_freightos_request(
        url: str,
        payload: FreightosRequestPayload
) -> FreightosQuotesResponse:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=url, data=json.dumps(payload.model_dump(exclude_none=True), indent=2), 
                                    headers=make_freightos_headers()) as response:
                return FreightosQuotesResponse(**await response.json())
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            return None
        

# Your JSON payload as a Python dictionary:
req_payload = {
   "messageHeader":{
      "messageID":"d559a7c1-784d-49f7-a58c-818c77afc2bd"
   },
   "businessInfo":{
      "serviceName":"Quoting",
      "serviceMethod":"New",
      "messageDateTime":"2025-06-21T14:56:22.508Z",
      "parties":[
         {
            "partyTypeCode":"BY",
            "contact":{
               "electronicMail":"okafor@thecozm.com"
            },
            "knownShipper":False
         },
         {
            "partyTypeCode":"FR",
            "name":"freightos.com"
         }
      ]
   },
   "shipment":{
      "originLocation":{
         "locationName":"port",
         "locationTypeCode":"seaport",
         "ID":"GBLON",
         "countryID":{
            "value":"GB"
         },
         "locationCode":"GBLON"
      },
      "destinationLocation":{
         "locationName":"port",
         "locationTypeCode":"seaport",
         "ID":"USNYC",
         "countryID":{
            "value":"US"
         },
         "locationCode":"USNYC"
      },
      "additionalInformation":[
         
      ],
      "pickupEvent":{
         "eventDate":{
            "scheduledDateTime":"2025-06-22T00:00:00+00:00",
            "endDateTime":""
         }
      },
      "load":{
         "packages":[
            {
               "quantity":1,
               "packagingType":"container20",
               "overWeightIndicator":False
            }
         ],
         "declaredValue":{
            "value":9000,
            "currencyID":"USD"
         }
      },
      "accessorials":[
         
      ],
      "insuranceValueAmount":{
         "value":9000,
         "currencyID":"USD"
      },
      "pricePreference":{
         "includeOriginPortCharges":True,
         "includeDestinationPortCharges":True,
         "requestCurrency":{
            
         }
      },
      "declaredCustoms":{
         "singleEntryBond":{
            "value":9000,
            "currencyID":"USD"
         },
         "entry":True,
         "commodityTypes":1
      }
   }
}

# Example usage:
if __name__ == "__main__":
    url = "https://ship.freightos.com/api/open-freight/quoting/quotes/search/"
    result = asyncio.run(make_freightos_request(
        url=url,
        payload=FreightosRequestPayload(**req_payload)
    ))
    print(result.paging.next, result.messageHeader.conversationID)
