import { ShippingRoute } from '@/types/shipping';

/**
 * Parse transit time from string format like "20 days" or "30" to number
 */
export const parseTransitTime = (timeStr: string | null | undefined): number => {
  if (!timeStr) return 0;
  
  // Extract number from string like "20 days" or "30"
  const match = timeStr.toString().match(/(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
};

/**
 * Get transit time range from shipping routes
 */
export const getTransitTimeRange = (routes: ShippingRoute[]): { min: number; max: number } => {
  const times = routes
    .map(route => parseTransitTime(route.total_shipping_time_days))
    .filter(time => time > 0);
  
  return {
    min: times.length > 0 ? Math.min(...times) : 0,
    max: times.length > 0 ? Math.max(...times) : 0
  };
};

/**
 * Get currency symbol
 */
export const getCurrencySymbol = (currency: string): string => {
  const currencyMap: { [key: string]: string } = {
    'USD': '$',
    'GBP': '£',
    'EUR': '€',
  };
  
  return currencyMap[currency?.toUpperCase()] || currency || '$';
};

/**
 * Format currency with price and symbol
 */
export const formatCurrency = (price: number | null | undefined, currency?: string): string => {
  if (price === null || price === undefined || isNaN(price)) {
    return 'N/A';
  }
  
  const symbol = getCurrencySymbol(currency || 'USD');
  return `${symbol}${price.toLocaleString()}`;
};

/**
 * Get price color class based on price value
 */
export const getPriceColorClass = (price: number): string => {
  if (price < 2000) return "text-green-600 bg-green-50 border-green-200";
  if (price < 3500) return "text-yellow-600 bg-yellow-50 border-yellow-200";
  return "text-red-600 bg-red-50 border-red-200";
};

/**
 * Get transit time color class based on days
 */
export const getTransitTimeColorClass = (timeStr: string | null | undefined): string => {
  const days = parseTransitTime(timeStr);
  if (days <= 7) return "text-green-600 bg-green-50";
  if (days <= 14) return "text-yellow-600 bg-yellow-50";
  return "text-red-600 bg-red-50";
};

/**
 * Calculate average transit time from routes
 */
export const calculateAverageTransitTime = (routes: ShippingRoute[]): number => {
  const times = routes
    .map(route => parseTransitTime(route.total_shipping_time_days))
    .filter(time => time > 0);
  
  return times.length > 0 ? Math.round(times.reduce((sum, time) => sum + time, 0) / times.length) : 0;
};

/**
 * Safe field access for optional fields
 */
export const safeField = <T>(value: T | null | undefined, fallback: T): T => {
  return value ?? fallback;
};

/**
 * Format date
 */
export const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
};

/**
 * Format date time
 */
export const formatDateTime = (dateString: string | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  } catch {
    return dateString;
  }
}; 