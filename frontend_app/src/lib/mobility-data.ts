import { Region, FamilySize, Seniority, CostType, CostMatrix, EvidenceData, CostSummary } from '@/types/mobility';
import { loadAndProcessFlightData, ProcessedFlightMatrix, getEvidenceForRoute } from '@/utils/flight-data-processor';
import { loadAndProcessShippingData, ProcessedShippingMatrix, getShippingEvidenceForRoute } from '@/utils/shipping-data-processor';

export const SENIORITY_LEVELS: Seniority[] = [
  {
    id: 'entry-level',
    label: 'Entry Level',
    description: 'L2, L3',
    multiplier: 1.0
  },
  {
    id: 'mid-career',
    label: 'Mid Career',
    description: 'L4 - L6',
    multiplier: 1.3
  },
  {
    id: 'director',
    label: 'Director',
    description: 'L7+M5/6',
    multiplier: 1.8
  },
  {
    id: 'vip',
    label: 'VIP',
    description: 'L8+ or M7+',
    multiplier: 2.5
  }
];

export const REGIONS: Region[] = [
  {
    id: 'north-america',
    name: 'North America',
    code: 'NA',
    countries: ['United States', 'Canada', 'Mexico']
  },
  {
    id: 'emea',
    name: 'EMEA',
    code: 'EMEA',
    countries: ['United Kingdom', 'Germany', 'France', 'Netherlands', 'Spain', 'Italy', 'Switzerland', 'Sweden', 'Norway', 'Denmark']
  },
  {
    id: 'apac',
    name: 'APAC',
    code: 'APAC',
    countries: ['Australia', 'New Zealand', 'Singapore', 'Japan', 'South Korea', 'Hong Kong']
  },
  {
    id: 'latam',
    name: 'LATAM',
    code: 'LATAM',
    countries: ['Brazil', 'Mexico', 'Costa Rica', 'Argentina', 'Chile', 'Colombia']
  },
  {
    id: 'india',
    name: 'India',
    code: 'IN',
    countries: ['India']
  }
];

export const FAMILY_SIZES: FamilySize[] = [
  {
    id: 'single',
    label: 'Single',
    adults: 1,
    children: 0,
    multiplier: 1.0
  },
  {
    id: 'couple',
    label: 'Couple',
    adults: 2,
    children: 0,
    multiplier: 1.8
  },
  {
    id: 'couple-plus-1',
    label: 'Couple +1',
    adults: 2,
    children: 1,
    multiplier: 2.4
  },
  {
    id: 'couple-plus-2',
    label: 'Couple +2',
    adults: 2,
    children: 2,
    multiplier: 2.9
  }
];

export const CONTAINER_TYPES = [
  {
    id: '20ft',
    label: '20ft Container',
    description: 'Standard 20-foot container'
  },
  {
    id: '40ft',
    label: '40ft Container', 
    description: 'Standard 40-foot container'
  }
];

export const COST_TYPES: CostType[] = [
  {
    id: 'flights',
    label: 'Flights',
    icon: 'Plane',
    description: 'Point-to-point flight costs for all family sizes across regions'
  },
  {
    id: 'accommodation',
    label: 'Accommodation',
    icon: 'Home',
    description: 'Temporary housing costs from Alto Vita and Silverdoor providers'
  },
  {
    id: 'shipping',
    label: 'Shipping',
    icon: 'Package',
    description: 'Container shipping costs (20ft vs 40ft) for household goods'
  }
];

// Base costs for flight routes (single person, economy)
const FLIGHT_BASE_COSTS: Record<string, Record<string, number>> = {
  'north-america': {
    'north-america': 650,
    'emea': 2200,
    'apac': 3000,
    'latam': 1200,
    'india': 3500
  },
  'emea': {
    'north-america': 2200,
    'emea': 600,
    'apac': 2500,
    'latam': 2800,
    'india': 1800
  },
  'apac': {
    'north-america': 3000,
    'emea': 2500,
    'apac': 800,
    'latam': 3500,
    'india': 2000
  },
  'latam': {
    'north-america': 1200,
    'emea': 2800,
    'apac': 3500,
    'latam': 900,
    'india': 4000
  },
  'india': {
    'north-america': 3500,
    'emea': 1800,
    'apac': 2000,
    'latam': 4000,
    'india': 400
  }
};

// Base costs for accommodation (single person per month)
const ACCOMMODATION_BASE_COSTS: Record<string, Record<string, number>> = {
  'north-america': {
    'north-america': 2000,
    'emea': 3500,
    'apac': 2500,
    'latam': 2800,
    'india': 2800
  },
  'emea': {
    'north-america': 3500,
    'emea': 1800,
    'apac': 3000,
    'latam': 3200,
    'india': 1200
  },
  'apac': {
    'north-america': 2500,
    'emea': 3000,
    'apac': 1000,
    'latam': 2400,
    'india': 800
  },
  'latam': {
    'north-america': 2800,
    'emea': 3200,
    'apac': 2400,
    'latam': 1500,
    'india': 2000
  },
  'india': {
    'north-america': 2800,
    'emea': 1200,
    'apac': 800,
    'latam': 2000,
    'india': 600
  }
};

// Shipping costs for containers
const SHIPPING_COSTS: Record<string, Record<string, { '20ft': number; '40ft': number }>> = {
  'north-america': {
    'north-america': { '20ft': 2500, '40ft': 3500 },
    'emea': { '20ft': 3000, '40ft': 4500 },
    'apac': { '20ft': 4500, '40ft': 6500 },
    'latam': { '20ft': 2800, '40ft': 4000 },
    'india': { '20ft': 4200, '40ft': 6000 }
  },
  'emea': {
    'north-america': { '20ft': 3000, '40ft': 4500 },
    'emea': { '20ft': 2000, '40ft': 2800 },
    'apac': { '20ft': 4000, '40ft': 5800 },
    'latam': { '20ft': 3500, '40ft': 5000 },
    'india': { '20ft': 3700, '40ft': 5300 }
  },
  'apac': {
    'north-america': { '20ft': 4500, '40ft': 6500 },
    'emea': { '20ft': 4000, '40ft': 5800 },
    'apac': { '20ft': 2200, '40ft': 3200 },
    'latam': { '20ft': 4800, '40ft': 6800 },
    'india': { '20ft': 3200, '40ft': 4500 }
  },
  'latam': {
    'north-america': { '20ft': 2800, '40ft': 4000 },
    'emea': { '20ft': 3500, '40ft': 5000 },
    'apac': { '20ft': 4800, '40ft': 6800 },
    'latam': { '20ft': 2000, '40ft': 2800 },
    'india': { '20ft': 4500, '40ft': 6200 }
  },
  'india': {
    'north-america': { '20ft': 4200, '40ft': 6000 },
    'emea': { '20ft': 3700, '40ft': 5300 },
    'apac': { '20ft': 3200, '40ft': 4500 },
    'latam': { '20ft': 4500, '40ft': 6200 },
    'india': { '20ft': 1500, '40ft': 2200 }
  }
};

// Store the processed data globally
let processedFlightMatrix: ProcessedFlightMatrix | null = null;
let processedShippingMatrix: ProcessedShippingMatrix | null = null;
let isLoadingFlightData = false;
let isLoadingShippingData = false;

/**
 * Load and cache the real flight data
 */
export async function initializeRealFlightData(): Promise<void> {
  if (processedFlightMatrix || isLoadingFlightData) {
    return; // Already loaded or loading
  }
  
  isLoadingFlightData = true;
  
  try {
    const { processedMatrix } = await loadAndProcessFlightData();
    processedFlightMatrix = processedMatrix;
    console.log('Real flight data initialized successfully');
  } catch (error) {
    console.error('Failed to load real flight data, falling back to static data:', error);
    processedFlightMatrix = null;
  } finally {
    isLoadingFlightData = false;
  }
}

/**
 * Load and cache the real shipping data
 */
export async function initializeRealShippingData(): Promise<void> {
  if (processedShippingMatrix || isLoadingShippingData) {
    return; // Already loaded or loading
  }
  
  isLoadingShippingData = true;
  
  try {
    processedShippingMatrix = await loadAndProcessShippingData();
    console.log('Real shipping data initialized successfully');
  } catch (error) {
    console.error('Failed to load real shipping data, falling back to static data:', error);
    processedShippingMatrix = null;
  } finally {
    isLoadingShippingData = false;
  }
}

// Enhanced generateCostMatrix to use real data when available
export function generateCostMatrix(): CostMatrix {
  const matrix: CostMatrix = {
    flights: {},
    accommodation: {},
    shipping: {}
  };

  // Use real flight data if available
  if (processedFlightMatrix) {
    // Convert real data to legacy format for flights
    REGIONS.forEach(originRegion => {
      if (!matrix.flights[originRegion.id]) {
        matrix.flights[originRegion.id] = {};
      }

              REGIONS.forEach(destRegion => {
          if (!matrix.flights[originRegion.id][destRegion.id]) {
            matrix.flights[originRegion.id][destRegion.id] = {};
          }

                  FAMILY_SIZES.forEach(familySize => {
            const realData = processedFlightMatrix?.[originRegion.id]?.[destRegion.id]?.[familySize.id];
            
            if (realData) {
              // Only use real average price - no fabricated data
              matrix.flights[originRegion.id][destRegion.id][familySize.id] = realData.averagePriceUSD;
            } else {
              // No real data available - leave blank (0 value)
              matrix.flights[originRegion.id][destRegion.id][familySize.id] = 0;
            }
          });
      });
    });
     } else {
     // No processed flight data available - initialize with empty values
     REGIONS.forEach(originRegion => {
       if (!matrix.flights[originRegion.id]) {
         matrix.flights[originRegion.id] = {};
       }

       REGIONS.forEach(destRegion => {
         if (!matrix.flights[originRegion.id][destRegion.id]) {
           matrix.flights[originRegion.id][destRegion.id] = {};
         }

         FAMILY_SIZES.forEach(familySize => {
           // No real data - leave blank (0 value)
           matrix.flights[originRegion.id][destRegion.id][familySize.id] = 0;
         });
       });
     });
   }

    // Generate accommodation matrix (no real data available yet - leave blank)
  REGIONS.forEach(originRegion => {
    if (!matrix.accommodation[originRegion.id]) {
      matrix.accommodation[originRegion.id] = {};
    }

    REGIONS.forEach(destRegion => {
      if (!matrix.accommodation[originRegion.id][destRegion.id]) {
        matrix.accommodation[originRegion.id][destRegion.id] = {};
      }

      FAMILY_SIZES.forEach(familySize => {
        // Placeholder accommodation data for demo purposes
        const accommodationData = ACCOMMODATION_BASE_COSTS[originRegion.id]?.[destRegion.id];
        if (accommodationData) {
          matrix.accommodation[originRegion.id][destRegion.id][familySize.id] = Math.round(accommodationData * familySize.multiplier);
        } else {
          matrix.accommodation[originRegion.id][destRegion.id][familySize.id] = 0;
        }
      });
    });
  });

  // Use real shipping data if available
  if (processedShippingMatrix) {
    // Convert real data to legacy format for shipping
    REGIONS.forEach(originRegion => {
      if (!matrix.shipping[originRegion.id]) {
        matrix.shipping[originRegion.id] = {};
      }

      REGIONS.forEach(destRegion => {
        if (!matrix.shipping[originRegion.id][destRegion.id]) {
          matrix.shipping[originRegion.id][destRegion.id] = {};
        }

        // Get real shipping data for 20ft and 40ft containers
        const data20ft = processedShippingMatrix?.[originRegion.id]?.[destRegion.id]?.['20ft'];
        const data40ft = processedShippingMatrix?.[originRegion.id]?.[destRegion.id]?.['40ft'];

        matrix.shipping[originRegion.id][destRegion.id]['20ft'] = data20ft?.averagePriceUSD || 0;
        matrix.shipping[originRegion.id][destRegion.id]['40ft'] = data40ft?.averagePriceUSD || 0;
      });
    });
  } else {
    // No processed shipping data available - initialize with empty values
    REGIONS.forEach(originRegion => {
      if (!matrix.shipping[originRegion.id]) {
        matrix.shipping[originRegion.id] = {};
      }

      REGIONS.forEach(destRegion => {
        if (!matrix.shipping[originRegion.id][destRegion.id]) {
          matrix.shipping[originRegion.id][destRegion.id] = {};
        }

        // No real data - leave blank (0 values)
        matrix.shipping[originRegion.id][destRegion.id]['20ft'] = 0;
        matrix.shipping[originRegion.id][destRegion.id]['40ft'] = 0;
      });
    });
  }

  return matrix;
}

/**
 * Get real flight evidence for a specific route and passenger type
 */
export function getFlightEvidence(originRegion: string, destRegion: string, passengerType: string) {
  if (!processedFlightMatrix) {
    return [];
  }
  
  return getEvidenceForRoute(processedFlightMatrix, originRegion, destRegion, passengerType);
}

/**
 * Check if real flight data is available
 */
export function hasRealFlightData(): boolean {
  return processedFlightMatrix !== null;
}

/**
 * Get flight data statistics for a route
 */
export function getFlightStatistics(originRegion: string, destRegion: string, passengerType: string) {
  if (!processedFlightMatrix) {
    return null;
  }
  
  const data = processedFlightMatrix[originRegion]?.[destRegion]?.[passengerType];
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

/**
 * Get real shipping evidence for a specific route and container type
 */
export function getShippingEvidence(originRegion: string, destRegion: string, containerType: string) {
  if (!processedShippingMatrix) {
    return [];
  }
  
  return getShippingEvidenceForRoute(processedShippingMatrix, originRegion, destRegion, containerType);
}

/**
 * Check if real shipping data is available
 */
export function hasRealShippingData(): boolean {
  return processedShippingMatrix !== null;
}

/**
 * Get shipping data statistics for a route
 */
export function getShippingStatistics(originRegion: string, destRegion: string, containerType: string) {
  if (!processedShippingMatrix) {
    return null;
  }
  
  const data = processedShippingMatrix[originRegion]?.[destRegion]?.[containerType];
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

export const SAMPLE_EVIDENCE: EvidenceData[] = [
  {
    id: '1',
    costType: 'flights',
    source: 'Expedia',
    url: 'https://expedia.com',
    screenshot: '/evidence/expedia-flight-screenshot.png',
    extractedData: {
      route: 'EMEA to North America',
      price: 2200,
      class: 'Economy',
      airline: 'British Airways'
    },
    timestamp: '2025-01-15T10:30:00Z',
    verified: true
  },
  {
    id: '2',
    costType: 'accommodation',
    source: 'Alto Vita',
    url: 'https://altovita.com',
    screenshot: '/evidence/altovita-accommodation-screenshot.png',
    extractedData: {
      location: 'London, UK',
      monthlyRate: 3500,
      type: 'Corporate Housing',
      bedrooms: 1
    },
    timestamp: '2025-01-15T14:20:00Z',
    verified: true
  },
  {
    id: '3',
    costType: 'shipping',
    source: 'Freightos',
    url: 'https://freightos.com',
    extractedData: {
      route: 'EMEA to North America',
      containerSize: '20ft',
      price: 3000,
      transitTime: '10-14 days'
    },
    timestamp: '2025-01-15T16:45:00Z',
    verified: true
  }
];

export function generateCostSummaries(): CostSummary[] {
  const summaries: CostSummary[] = [];
  const matrix = generateCostMatrix();

  COST_TYPES.forEach(costType => {
    REGIONS.forEach(origin => {
      REGIONS.forEach(destination => {
        let costs: number[] = [];
        
        if (costType.id === 'shipping') {
          const cost20ft = matrix.shipping[origin.id][destination.id]['20ft'];
          const cost40ft = matrix.shipping[origin.id][destination.id]['40ft'];
          if (cost20ft > 0) costs.push(cost20ft);
          if (cost40ft > 0) costs.push(cost40ft);
        } else {
          FAMILY_SIZES.forEach(fs => {
            const cost = matrix[costType.id][origin.id][destination.id][fs.id];
            if (cost > 0) costs.push(cost);
          });
        }

        // Only create summary if we have real data (costs > 0)
        if (costs.length > 0) {
          const avgCost = costs.reduce((a, b) => a + b, 0) / costs.length;
          const minCost = Math.min(...costs);
          const maxCost = Math.max(...costs);

          summaries.push({
            costType: costType.id,
            origin: origin.id,
            destination: destination.id,
            totalRoutes: costs.length,
            avgCost: Math.round(avgCost),
            minCost,
            maxCost,
            outliers: costs.filter(cost => cost > avgCost * 1.5).length,
            lastUpdated: new Date().toISOString()
          });
        }
      });
    });
  });

  return summaries;
} 