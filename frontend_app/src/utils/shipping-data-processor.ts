export interface ShippingQuote {
  city_of_origin: string;
  country_of_origin: string;
  city_of_destination: string;
  country_of_destination: string;
  date_of_shipping: string;
  total_shipping_time_days: string;
  price_of_shipping: number;
  currency: string;
  container_type: string; // ST40 = 40ft, ST20 = 20ft
  provider: string;
  datetime_of_scraping: string;
  carrier: string;
  screenshot_url?: string;
  website_link?: string;
  validity_from: string;
  validity_to: string;
  origin_city_region: string;
  destination_city_region: string;
}

export interface ProcessedShippingData {
  averagePriceUSD: number;
  minPrice: number;
  maxPrice: number;
  sampleCount: number;
  evidence: ShippingQuote[];
}

export interface ProcessedShippingMatrix {
  [originRegion: string]: {
    [destRegion: string]: {
      [containerType: string]: ProcessedShippingData;
    };
  };
}

// Currency conversion rates to USD
const CURRENCY_RATES: Record<string, number> = {
  'USD': 1.0,
  'EUR': 1.09,
  'GBP': 1.27,
  'CAD': 0.74,
  'AUD': 0.67
};

// Container type mapping
const CONTAINER_TYPE_MAPPING: Record<string, string> = {
  'ST40': '40ft',
  'ST20': '20ft',
  '40ft': '40ft',
  '20ft': '20ft'
};

// Region mapping to match our frontend regions
const REGION_MAPPING: Record<string, string> = {
  'NORTH_AMERICA': 'north-america',
  'LATAM': 'latam',
  'EMEA': 'emea',
  'ASIA': 'apac',
  'INDIA': 'india',
  'ANZ': 'apac'
};

function convertToUSD(price: number, currency: string): number {
  const rate = CURRENCY_RATES[currency] || 1.0;
  return Math.round(price * rate);
}

function mapContainerType(containerType: string): string {
  return CONTAINER_TYPE_MAPPING[containerType] || containerType;
}

function mapRegion(region: string): string {
  return REGION_MAPPING[region] || region.toLowerCase().replace('_', '-');
}

export async function loadAndProcessShippingData(): Promise<ProcessedShippingMatrix> {
  try {
    const response = await fetch('/shipping_data.json');
    if (!response.ok) {
      throw new Error(`Failed to fetch shipping data: ${response.statusText}`);
    }

    const rawData: ShippingQuote[] = await response.json();
    console.log(`Loaded ${rawData.length} shipping quotes`);

    const processedMatrix: ProcessedShippingMatrix = {};

    // Group quotes by origin region, destination region, and container type
    const groupedData: Record<string, Record<string, Record<string, ShippingQuote[]>>> = {};

    rawData.forEach(quote => {
      const originRegion = mapRegion(quote.origin_city_region);
      const destRegion = mapRegion(quote.destination_city_region);
      const containerType = mapContainerType(quote.container_type);

      // Skip if we don't have valid region mapping
      if (!originRegion || !destRegion) {
        return;
      }

      if (!groupedData[originRegion]) {
        groupedData[originRegion] = {};
      }
      if (!groupedData[originRegion][destRegion]) {
        groupedData[originRegion][destRegion] = {};
      }
      if (!groupedData[originRegion][destRegion][containerType]) {
        groupedData[originRegion][destRegion][containerType] = [];
      }

      groupedData[originRegion][destRegion][containerType].push(quote);
    });

    // Process each group to calculate statistics
    Object.keys(groupedData).forEach(originRegion => {
      if (!processedMatrix[originRegion]) {
        processedMatrix[originRegion] = {};
      }

      Object.keys(groupedData[originRegion]).forEach(destRegion => {
        if (!processedMatrix[originRegion][destRegion]) {
          processedMatrix[originRegion][destRegion] = {};
        }

        Object.keys(groupedData[originRegion][destRegion]).forEach(containerType => {
          const quotes = groupedData[originRegion][destRegion][containerType];
          
          // Convert all prices to USD
          const pricesUSD = quotes.map(quote => 
            convertToUSD(quote.price_of_shipping, quote.currency)
          );

          // Calculate statistics
          const minPrice = Math.min(...pricesUSD);
          const maxPrice = Math.max(...pricesUSD);
          const averagePrice = Math.round(
            pricesUSD.reduce((sum, price) => sum + price, 0) / pricesUSD.length
          );

          // Collect evidence (prioritize screenshots, limit to 5-10 samples)
          const quotesWithScreenshots = quotes.filter(q => q.screenshot_url);
          const quotesWithoutScreenshots = quotes.filter(q => !q.screenshot_url);
          
          const evidenceQuotes = [
            ...quotesWithScreenshots.slice(0, 7),
            ...quotesWithoutScreenshots.slice(0, Math.max(0, 10 - quotesWithScreenshots.length))
          ];

          processedMatrix[originRegion][destRegion][containerType] = {
            averagePriceUSD: averagePrice,
            minPrice,
            maxPrice,
            sampleCount: quotes.length,
            evidence: evidenceQuotes
          };

          console.log(`Processed ${originRegion} → ${destRegion} (${containerType}): ${quotes.length} quotes, avg $${averagePrice}`);
        });
      });
    });

    return processedMatrix;
  } catch (error) {
    console.error('Error processing shipping data:', error);
    throw error;
  }
}

export function getShippingEvidenceForRoute(
  matrix: ProcessedShippingMatrix,
  originRegion: string,
  destRegion: string,
  containerType: string
): ShippingQuote[] {
  return matrix[originRegion]?.[destRegion]?.[containerType]?.evidence || [];
}

export function getShippingStatistics(
  matrix: ProcessedShippingMatrix,
  originRegion: string,
  destRegion: string,
  containerType: string
) {
  const data = matrix[originRegion]?.[destRegion]?.[containerType];
  if (!data) {
    return null;
  }

  return {
    averagePrice: data.averagePriceUSD,
    minPrice: data.minPrice,
    maxPrice: data.maxPrice,
    sampleCount: data.sampleCount,
    evidenceCount: data.evidence.length
  };
} 