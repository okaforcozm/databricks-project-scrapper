interface FlightSearchRequest {
  session_id?: string;
  origin_city: string;
  destination_city: string;
  num_adults: number;
  num_children: number;
  num_infants: number;
  flight_class: string;
  departure_date: string;
  quoted_price: number;
  baggage_allowance?: number;
  flight_type?: string;
}

interface Quote {
  id: string;
  source: string;
  price: number;
  url: string;
  airline: string;
  departure: string;
  arrival: string;
  stops: number;
  baggage: string;
}

interface FlightComparison {
  id: string;
  user_query: {
    origin: string;
    destination: string;
    num_adults: number;
    num_children: number;
    num_infants: number;
    flight_class: string;
    departure_date: string;
    client_quoted_price: number;
    baggage_allowance: string;
  };
  external_quotes: Quote[];
  discrepancies: Quote[];
  analytics: {
    total_external_sources: number;
    discrepancies_found: number;
    avg_savings: number;
    max_savings: number;
    performance_by_source: Record<string, { competitive: number; total: number }>;
  };
  screenshots: Array<{
    screenshot_url: string;
    quote_id: string;
    source: string;
  }>;
  timestamp: string;
}

interface FlightSearchResponse {
  session_id: string;
  status: string;
  data?: FlightComparison;
  error?: string;
}

interface GlobalAnalytics {
  total_comparisons: number;
  total_discrepancies: number;
  avg_savings_percentage: number;
  time_saved_hours: number;
  performance_by_airline: Array<{
    name: string;
    competitive_rate: number;
    avg_discrepancy: number;
  }>;
  performance_by_route: Array<{
    route: string;
    discrepancy_rate: number;
    avg_savings: number;
  }>;
}

const API_BASE_URL = 'http://3.218.218.18/backend/api/v1';

export const searchFlights = async (searchData: FlightSearchRequest): Promise<FlightComparison> => {
  // Transform frontend data to backend format
  const backendData = {
    session_id: searchData.session_id,
    origin_city: searchData.origin_city,
    destination_city: searchData.destination_city,
    num_adults: searchData.num_adults,
    num_children: searchData.num_children,
    num_infants: searchData.num_infants,
    flight_class: searchData.flight_class,
    departure_date: searchData.departure_date,
    quoted_price: searchData.quoted_price,
    baggage_allowance: searchData.baggage_allowance || 23,
    flight_type: searchData.flight_type || 'oneway'
  };

  const response = await fetch(`${API_BASE_URL}/search/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendData),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }

  const result: FlightSearchResponse = await response.json();
  
  if (result.status === 'failed') {
    throw new Error(result.error || 'Flight search failed');
  }
  
  if (!result.data) {
    throw new Error('No data returned from search');
  }

  return result.data;
};

export const getGlobalAnalytics = async (): Promise<GlobalAnalytics> => {
  const response = await fetch(`${API_BASE_URL}/analytics/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const result = await response.json();
  
  if (result.status === 'error') {
    throw new Error(result.error || 'Failed to fetch analytics');
  }

  return result.data;
};

export const getRecentComparisons = async (limit: number = 50): Promise<FlightComparison[]> => {
  const response = await fetch(`${API_BASE_URL}/analytics/recent/?limit=${limit}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const result = await response.json();
  
  if (result.status === 'error') {
    throw new Error(result.error || 'Failed to fetch recent comparisons');
  }

  return result.data;
};

export const getSearchStatus = async (sessionId: string): Promise<FlightSearchResponse> => {
  const response = await fetch(`${API_BASE_URL}/search/${sessionId}/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Deprecated - keeping for backward compatibility
export const getFlightMatrixPdfFile = async (): Promise<{ url: string }> => {
  // This endpoint no longer exists, return a mock response
  return Promise.resolve({ url: '#' });
};