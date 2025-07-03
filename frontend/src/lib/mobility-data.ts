import { Region, FamilySize, CostType, CostMatrix, EvidenceData, CostSummary } from '@/types/mobility';

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

export function generateCostMatrix(): CostMatrix {
  const matrix: CostMatrix = {
    flights: {},
    accommodation: {},
    shipping: {}
  };

  // Generate flight costs
  REGIONS.forEach(originRegion => {
    matrix.flights[originRegion.id] = {};
    REGIONS.forEach(destRegion => {
      matrix.flights[originRegion.id][destRegion.id] = {};
      FAMILY_SIZES.forEach(familySize => {
        const baseCost = FLIGHT_BASE_COSTS[originRegion.id][destRegion.id];
        matrix.flights[originRegion.id][destRegion.id][familySize.id] = Math.round(baseCost * familySize.multiplier);
      });
    });
  });

  // Generate accommodation costs
  REGIONS.forEach(originRegion => {
    matrix.accommodation[originRegion.id] = {};
    REGIONS.forEach(destRegion => {
      matrix.accommodation[originRegion.id][destRegion.id] = {};
      FAMILY_SIZES.forEach(familySize => {
        const baseCost = ACCOMMODATION_BASE_COSTS[originRegion.id][destRegion.id];
        matrix.accommodation[originRegion.id][destRegion.id][familySize.id] = Math.round(baseCost * familySize.multiplier);
      });
    });
  });

  // Generate shipping costs
  REGIONS.forEach(originRegion => {
    matrix.shipping[originRegion.id] = {};
    REGIONS.forEach(destRegion => {
      matrix.shipping[originRegion.id][destRegion.id] = {
        '20ft': SHIPPING_COSTS[originRegion.id][destRegion.id]['20ft'],
        '40ft': SHIPPING_COSTS[originRegion.id][destRegion.id]['40ft']
      };
    });
  });

  return matrix;
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
        if (origin.id !== destination.id) {
          let costs: number[] = [];
          
          if (costType.id === 'shipping') {
            costs = [
              matrix.shipping[origin.id][destination.id]['20ft'],
              matrix.shipping[origin.id][destination.id]['40ft']
            ];
          } else {
            costs = FAMILY_SIZES.map(fs => 
              matrix[costType.id][origin.id][destination.id][fs.id]
            );
          }

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
            outliers: 0, // Could implement outlier detection logic
            lastUpdated: '2025-01-15T12:00:00Z'
          });
        }
      });
    });
  });

  return summaries;
} 