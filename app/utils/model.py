from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict

# -----------------------------  Searates Request Payload  -----------------------------

class SearatesRequestPayload(BaseModel):
    pointIdFrom: str
    pointIdTo: str
    date: str
    container: str


class Location(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    code: Optional[str] = None
    inaccessible: Optional[bool] = None
    pointType: Optional[str] = None
    dry: Optional[bool] = None

class Load(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: Optional[Union[str, int]] = None
    unit: Optional[str] = None
    amount: Optional[str] = None
    shortCode: Optional[str] = None
    type: Optional[str] = None

class PointTariff(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    name: Optional[str] = None
    abbr: Optional[str] = None
    price: Optional[Union[int, float]] = None
    currency: Optional[str] = None
    profileId: Optional[Union[str, int]] = None

class RouteTariff(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    name: Optional[str] = None
    abbr: Optional[str] = None
    price: Optional[Union[int, float]] = None
    currency: Optional[str] = None

class LumpsumTariff(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    price: Optional[Union[int, float]] = None
    currency: Optional[str] = None

class Co2(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    amount: Optional[Union[int, float]] = None
    price: Optional[Union[int, float]] = None
    placeAmount: Optional[Union[int, float]] = None
    placePrice: Optional[Union[int, float]] = None
    lumpsumAmount: Optional[Union[int, float]] = None
    lumpsumPrice: Optional[Union[int, float]] = None

class TransitTime(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    rate: Optional[Union[int, float]] = None
    port: Optional[Union[int, float]] = None
    route: Optional[Union[int, float]] = None

class Point(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: Optional[str] = None
    rateId: Optional[str] = None
    location: Optional[Location] = None
    shippingType: Optional[str] = None
    provider: Optional[str] = None
    providerLogo: Optional[str] = None
    loads: Optional[List[Load]] = []
    pointTariff: Optional[List[PointTariff]] = []
    routeTariff: Optional[List[RouteTariff]] = []
    lumpsumTariff: Optional[LumpsumTariff] = None
    co2: Optional[Co2] = None
    transitTime: Optional[TransitTime] = None
    profileId: Optional[str] = None
    distance: Optional[str] = None
    totalPrice: Optional[Union[int, float]] = None
    totalCurrency: Optional[str] = None
    pointTotal: Optional[Union[int, float]] = None
    routeTotal: Optional[Union[int, float]] = None
    terms: Optional[str] = None

class TotalCo2(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    amount: Optional[Union[int, float]] = None
    price: Optional[Union[int, float]] = None

class General(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    shipmentId: Optional[str] = None
    validityFrom: Optional[str] = None
    validityTo: Optional[str] = None
    individual: Optional[bool] = None
    totalPrice: Optional[Union[int, float]] = None
    totalCurrency: Optional[str] = None
    totalTransitTime: Optional[Union[int, float]] = None
    totalCo2: Optional[TotalCo2] = None
    dfaRate: Optional[bool] = None
    alternative: Optional[bool] = None
    expired: Optional[bool] = None
    spaceGuarantee: Optional[bool] = None
    spot: Optional[bool] = None
    indicative: Optional[bool] = None
    standard: Optional[bool] = None
    rateOwner: Optional[bool] = None
    queryShippingType: Optional[str] = None
    promotionObligations: Optional[bool] = None
    shipmentCreatedAt: Optional[str] = None

class Request(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    request_key: Optional[str] = None

class Rate(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    points: Optional[List[Point]] = []
    general: Optional[General] = None
    request: Optional[Request] = None

class SearatesResponsePayload(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    data: Optional[dict] = {}

class DataModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    rates: Optional[List[Rate]] = []

class SearatesResponsePayload(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    data: Optional[DataModel] = None


# -----------------------------  Freightos Request Payload  -----------------------------  

class MessageHeader(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    messageID: Optional[str] = None
    conversationID: Optional[str] = None

class Contact(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    electronicMail: Optional[str] = None

class Party(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    partyTypeCode: Optional[str] = None
    contact: Optional[Contact] = None
    name: Optional[str] = None
    knownShipper: Optional[bool] = None

class BusinessInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    serviceName: Optional[str] = None
    serviceMethod: Optional[str] = None
    messageDateTime: Optional[str] = None
    parties: Optional[List[Party]] = []
    message: Optional[str] = None  # For error messages

class CountryID(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    value: Optional[str] = None

class Location(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    locationName: Optional[str] = None
    locationTypeCode: Optional[str] = None
    ID: Optional[str] = None
    countryID: Optional[CountryID] = None
    locationCode: Optional[str] = None

class PickupEvent(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    eventDate: Optional[dict] = {}

class Package(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    quantity: Optional[int] = None
    packagingType: Optional[str] = None
    overWeightIndicator: Optional[bool] = None

class DeclaredValue(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    value: Optional[float] = None
    currencyID: Optional[str] = None

class Load(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    packages: Optional[List[Package]] = []
    declaredValue: Optional[DeclaredValue] = None

class PricePreference(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    requestCurrency: Optional[dict] = {}
    includeOriginPortCharges: Optional[bool] = None
    includeDestinationPortCharges: Optional[bool] = None

class SingleEntryBond(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    value: Optional[float] = None
    currencyID: Optional[str] = None

class DeclaredCustoms(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    singleEntryBond: Optional[SingleEntryBond] = None
    entry: Optional[bool] = None
    commodityTypes: Optional[int] = None

class Shipment(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    originLocation: Optional[Location] = None
    destinationLocation: Optional[Location] = None
    additionalInformation: Optional[List] = []
    pickupEvent: Optional[PickupEvent] = None
    load: Optional[Load] = None
    accessorials: Optional[List] = []
    insuranceValueAmount: Optional[DeclaredValue] = None
    pricePreference: Optional[PricePreference] = None
    declaredCustoms: Optional[DeclaredCustoms] = None

class FreightosRequestPayload(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    messageHeader: Optional[MessageHeader] = None
    businessInfo: Optional[BusinessInfo] = None
    shipment: Optional[Shipment] = None


# -----------------------------  Freightos Response Payload  -----------------------------  

class Paging(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    nextCursor: Optional[int] = None
    next: Optional[str] = None
    hasMore: Optional[bool] = None
    count: Optional[int] = None

class URIObject(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    uri: Optional[str] = None

class URIReferences(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    results: Optional[URIObject] = None
    services: Optional[URIObject] = None

class FreightosQuotesResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    messageHeader: Optional[MessageHeader] = None
    businessInfo: Optional[BusinessInfo] = None
    quotes: Optional[List[Any]] = []
    paging: Optional[Paging] = None
    URIReferences: Optional[Union[URIReferences, dict, Any]] = None