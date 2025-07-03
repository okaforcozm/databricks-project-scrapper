import { ShippingRoute } from "@/types/shipping";
import { SHIPPING_ROUTES } from "./shipping-utils-data";

// API functions that could be used in production
export const loadShippingRoutes = async (): Promise<ShippingRoute[]> => {
  try {
    // In production, this would fetch from your API
    // const response = await fetch('/api/shipping-routes');
    // return await response.json();
    
    // For now, return the static data
    return SHIPPING_ROUTES;
  } catch (error) {
    console.error('Failed to load shipping routes:', error);
    return [];
  }
};

export const loadShippingRoute = async (shipmentId: string): Promise<ShippingRoute | null> => {
  try {
    // In production, this would fetch a specific route
    // const response = await fetch(`/api/shipping-routes/${shipmentId}`);
    // return await response.json();
    
    // For now, find in static data
    return SHIPPING_ROUTES.find(route => route.shipment_id === shipmentId) || null;
  } catch (error) {
    console.error(`Failed to load shipping route ${shipmentId}:`, error);
    return null;
  }
};

// Helper functions for data analysis
export const getUniqueOrigins = (): string[] => {
  return [...new Set(SHIPPING_ROUTES.map(route => route.city_of_origin))].sort();
};

export const getUniqueDestinations = (): string[] => {
  return [...new Set(SHIPPING_ROUTES.map(route => route.city_of_destination))].sort();
};

export const getUniqueContainerTypes = (): string[] => {
  return [...new Set(SHIPPING_ROUTES.map(route => route.container_type))].sort();
};

export const getUniqueCarriers = (): string[] => {
  return [...new Set(SHIPPING_ROUTES.map(route => route.carrier))].sort();
};

export const getPriceRange = (): { min: number; max: number } => {
  const prices = SHIPPING_ROUTES.map(route => route.price_of_shipping);
  return {
    min: Math.min(...prices),
    max: Math.max(...prices)
  };
};

export const getTransitTimeRange = (): { min: number; max: number } => {
  const times = SHIPPING_ROUTES
    .map(route => route.total_shipping_time_days)
    .filter(time => time != null)
    .map(time => {
      const match = time.toString().match(/(\d+)/);
      return match ? parseInt(match[1], 10) : 0;
    })
    .filter(num => num > 0);
  
  return {
    min: times.length > 0 ? Math.min(...times) : 0,
    max: times.length > 0 ? Math.max(...times) : 0
  };
}; 