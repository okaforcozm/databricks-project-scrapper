interface FlightQuote {
  departure_airport: string;
  destination_airport: string;
  departure_city: string;
  destination_city: string;
  origin_city_region: string;
  destination_city_region: string;
  flight_date: string;
  departure_time: string;
  arrival_time: string;
  total_flight_time: string;
  airline_code: string;
  cabin_bags: number;
  checked_bags: number;
  num_stops: number;
  price: number;
  currency: string;
  num_adults: number;
  num_children: number;
  num_infants: number;
  passenger_type: string;
  scraping_datetime: string;
  source: string;
  screenshot_url: string | null;
  booking_url: string;
}

interface FlightDataSet {
  aggregation_timestamp: string;
  total_quotes: number;
  data_sources: any;
  statistics: any;
  flight_quotes: FlightQuote[];
}

interface EvidenceItem {
  departure_city: string;
  destination_city: string;
  airline_code: string;
  price: number;
  currency: string;
  priceUSD: number;
  flight_date: string;
  total_flight_time: string;
  source: string;
  screenshot_url: string | null;
  booking_url: string;
  scraping_datetime: string;
}

interface RegionMatrixData {
  averagePriceUSD: number;
  sampleCount: number;
  evidence: EvidenceItem[];
  minPrice: number;
  maxPrice: number;
}

export interface ProcessedFlightMatrix {
  [originRegion: string]: {
    [destinationRegion: string]: {
      [passengerType: string]: RegionMatrixData;
    };
  };
}

// Currency conversion rates (as of recent rates - in production, you'd want to fetch these dynamically)
const CURRENCY_RATES = {
  EUR: 1.09,  // 1 EUR = 1.09 USD
  GBP: 1.27,  // 1 GBP = 1.27 USD
  USD: 1.0    // Base currency
};

// Supported regions mapping
const REGION_MAPPING = {
  'NORTH_AMERICA': 'north-america',
  'LATAM': 'latam', 
  'EMEA': 'emea',
  'ASIA': 'apac',  // Mapping ASIA to APAC for consistency
  'INDIA': 'india',
  'ANZ': 'apac'    // Mapping ANZ to APAC for consistency
};

// Passenger type mapping
const PASSENGER_TYPE_MAPPING = {
  'Single': 'single',
  'Couple': 'couple',
  'Couple+1': 'couple-plus-1', 
  'Couple+2': 'couple-plus-2'
};

/**
 * Convert price to USD based on currency
 */
function convertToUSD(price: number, currency: string): number {
  const rate = CURRENCY_RATES[currency as keyof typeof CURRENCY_RATES];
  if (!rate) {
    console.warn(`Unknown currency: ${currency}, defaulting to USD rate`);
    return price; // Assume USD if unknown
  }
  return Math.round(price * rate * 100) / 100; // Round to 2 decimal places
}

/**
 * Shuffle array and take first n elements
 */
function sampleArray<T>(array: T[], count: number): T[] {
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, Math.min(count, array.length));
}

/**
 * Process flight data and generate cost matrix
 */
export function processFlightDataToMatrix(flightData: FlightDataSet): ProcessedFlightMatrix {
  const matrix: ProcessedFlightMatrix = {};
  
  // Group quotes by origin region, destination region, and passenger type
  const groupedData: { [key: string]: FlightQuote[] } = {};
  
  flightData.flight_quotes.forEach(quote => {
    // Only process supported regions
    const originRegion = REGION_MAPPING[quote.origin_city_region as keyof typeof REGION_MAPPING];
    const destRegion = REGION_MAPPING[quote.destination_city_region as keyof typeof REGION_MAPPING];
    const passengerType = PASSENGER_TYPE_MAPPING[quote.passenger_type as keyof typeof PASSENGER_TYPE_MAPPING];
    
    if (!originRegion || !destRegion || !passengerType) {
      return; // Skip unsupported regions/passenger types
    }
    
    // Allow same region routes (domestic flights within regions)
    // Note: Same region routes are now processed
    
    const key = `${originRegion}|${destRegion}|${passengerType}`;
    
    if (!groupedData[key]) {
      groupedData[key] = [];
    }
    
    groupedData[key].push(quote);
  });
  
  // Process each group to calculate averages and collect evidence
  Object.entries(groupedData).forEach(([key, quotes]) => {
    const [originRegion, destRegion, passengerType] = key.split('|');
    
    // Convert all prices to USD
    const pricesUSD = quotes.map(quote => convertToUSD(quote.price, quote.currency));
    
    // Calculate statistics
    const averagePriceUSD = Math.round(pricesUSD.reduce((sum, price) => sum + price, 0) / pricesUSD.length);
    const minPrice = Math.min(...pricesUSD);
    const maxPrice = Math.max(...pricesUSD);
    
    // Select 5-10 random samples for evidence (prioritize those with screenshots)
    const quotesWithScreenshots = quotes.filter(q => q.screenshot_url);
    const quotesWithoutScreenshots = quotes.filter(q => !q.screenshot_url);
    
    // Prefer quotes with screenshots, but fallback to others if needed
    const selectedQuotes = [
      ...sampleArray(quotesWithScreenshots, 7), // Try to get 7 with screenshots
      ...sampleArray(quotesWithoutScreenshots, 3) // Fill remaining with others
    ].slice(0, 10); // Max 10 total
    
    const evidence: EvidenceItem[] = selectedQuotes.map(quote => ({
      departure_city: quote.departure_city,
      destination_city: quote.destination_city,
      airline_code: quote.airline_code,
      price: quote.price,
      currency: quote.currency,
      priceUSD: convertToUSD(quote.price, quote.currency),
      flight_date: quote.flight_date,
      total_flight_time: quote.total_flight_time,
      source: quote.source,
      screenshot_url: quote.screenshot_url,
      booking_url: quote.booking_url,
      scraping_datetime: quote.scraping_datetime
    }));
    
    // Initialize nested structure if needed
    if (!matrix[originRegion]) {
      matrix[originRegion] = {};
    }
    if (!matrix[originRegion][destRegion]) {
      matrix[originRegion][destRegion] = {};
    }
    
    matrix[originRegion][destRegion][passengerType] = {
      averagePriceUSD,
      sampleCount: quotes.length,
      evidence,
      minPrice,
      maxPrice
    };
  });
  
  return matrix;
}

/**
 * Convert processed matrix to the format expected by CostMatrix component
 */
export function convertToLegacyFormat(processedMatrix: ProcessedFlightMatrix) {
  const legacyMatrix: any = {};
  
  Object.entries(processedMatrix).forEach(([originRegion, destinations]) => {
    if (!legacyMatrix[originRegion]) {
      legacyMatrix[originRegion] = {};
    }
    
    Object.entries(destinations).forEach(([destRegion, passengerTypes]) => {
      if (!legacyMatrix[originRegion][destRegion]) {
        legacyMatrix[originRegion][destRegion] = {};
      }
      
      Object.entries(passengerTypes).forEach(([passengerType, data]) => {
        legacyMatrix[originRegion][destRegion][passengerType] = data.averagePriceUSD;
      });
    });
  });
  
  return legacyMatrix;
}

/**
 * Load and process flight data from JSON file
 */
export async function loadAndProcessFlightData(): Promise<{
  processedMatrix: ProcessedFlightMatrix;
  legacyMatrix: any;
}> {
  try {
    // In a real application, you'd fetch this from an API or read from a file
    // For now, we'll need to import or fetch the JSON data
    const response = await fetch('/centralized_flight_data.json');
    const flightData: FlightDataSet = await response.json();
    
    const processedMatrix = processFlightDataToMatrix(flightData);
    const legacyMatrix = convertToLegacyFormat(processedMatrix);
    
    console.log('Flight data processed successfully:');
    console.log(`- Total route combinations: ${Object.keys(processedMatrix).length}`);
    console.log(`- Total data points: ${JSON.stringify(processedMatrix).length} characters`);
    
    return {
      processedMatrix,
      legacyMatrix
    };
  } catch (error) {
    console.error('Error loading flight data:', error);
    throw error;
  }
}

/**
 * Get evidence data for a specific route and passenger type
 */
export function getEvidenceForRoute(
  processedMatrix: ProcessedFlightMatrix,
  originRegion: string,
  destRegion: string,
  passengerType: string
): EvidenceItem[] {
  return processedMatrix[originRegion]?.[destRegion]?.[passengerType]?.evidence || [];
} 