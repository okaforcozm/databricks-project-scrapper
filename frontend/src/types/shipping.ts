export interface ShippingRoute {
  _id?: string;
  city_of_origin: string;
  country_of_origin: string;
  city_of_destination: string;
  country_of_destination: string;
  date_of_shipping: string;
  total_shipping_time_days?: string | null;
  price_of_shipping: number;
  currency: string;
  container_type: string;
  provider: string;
  datetime_of_scraping?: string;
  carrier?: string;
  screenshot_url?: string;
  website_link?: string;
  website_url?: string;
  shipment_id?: string;
  rate_id?: string;
  co2_amount?: number | null;
  co2_price?: number | null;
  validity_from?: string;
  validity_to?: string;
  distance?: string;
  point_total?: number | null;
  route_total?: number | null;
}

export interface PaginationState {
  currentPage: number;
  itemsPerPage: number;
  totalItems: number;
  totalPages: number;
}

export interface ShippingFilters {
  origin?: string;
  destination?: string;
  container?: string;
  minPrice?: number;
  maxPrice?: number;
  minDays?: number;
  maxDays?: number;
} 