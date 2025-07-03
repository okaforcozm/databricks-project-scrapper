import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { 
  Ship, 
  Package, 
  DollarSign, 
  Clock,
  MapPin,
  Eye,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Download,
  Calendar,
  Building2,
  Plane,
  Filter,
  Search,
  X,
  ChevronDown,
  Globe,
  BarChart3,
  TrendingUp,
  Users,
  Settings
} from 'lucide-react';

import { ShippingRoute, PaginationState, ShippingFilters } from '@/types/shipping';
import { 
  formatCurrency, 
  getPriceColorClass, 
  calculateAverageTransitTime,
  safeField 
} from '@/lib/shipping-utils';
import { SHIPPING_ROUTES } from '@/lib/shipping-utils-data';

interface ColumnFilters {
  originCity: string;
  originCountry: string;
  destinationCity: string;
  destinationCountry: string;
  shippingDate: string;
  priceRange: { min: string; max: string };
  containerType: string;
  provider: string;
}

interface ShippingMatrixDashboardProps {
  onViewDetails: (route: ShippingRoute) => void;
}

const ShippingMatrixDashboard: React.FC<ShippingMatrixDashboardProps> = ({ onViewDetails }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [columnFilters, setColumnFilters] = useState<ColumnFilters>({
    originCity: '',
    originCountry: '',
    destinationCity: '',
    destinationCountry: '',
    shippingDate: '',
    priceRange: { min: '', max: '' },
    containerType: '',
    provider: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const itemsPerPage = 10;

  // Get unique values for dropdowns
  const uniqueValues = useMemo(() => ({
    originCities: [...new Set(SHIPPING_ROUTES.map(route => route.city_of_origin))].sort(),
    originCountries: [...new Set(SHIPPING_ROUTES.map(route => route.country_of_origin))].sort(),
    destinationCities: [...new Set(SHIPPING_ROUTES.map(route => route.city_of_destination))].sort(),
    destinationCountries: [...new Set(SHIPPING_ROUTES.map(route => route.country_of_destination))].sort(),
    containerTypes: [...new Set(SHIPPING_ROUTES.map(route => route.container_type))].sort(),
    providers: [...new Set(SHIPPING_ROUTES.map(route => route.provider))].sort(),
  }), []);

  // Enhanced filter data based on search and column filters
  const filteredData = useMemo(() => {
    let filtered = SHIPPING_ROUTES;

    // Global search
    if (searchTerm) {
      filtered = filtered.filter(route => 
        route.city_of_origin.toLowerCase().includes(searchTerm.toLowerCase()) ||
        route.city_of_destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
        route.country_of_origin.toLowerCase().includes(searchTerm.toLowerCase()) ||
        route.country_of_destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
        safeField(route.carrier, '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        route.provider.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Column filters
    if (columnFilters.originCity) {
      filtered = filtered.filter(route => route.city_of_origin === columnFilters.originCity);
    }
    if (columnFilters.originCountry) {
      filtered = filtered.filter(route => route.country_of_origin === columnFilters.originCountry);
    }
    if (columnFilters.destinationCity) {
      filtered = filtered.filter(route => route.city_of_destination === columnFilters.destinationCity);
    }
    if (columnFilters.destinationCountry) {
      filtered = filtered.filter(route => route.country_of_destination === columnFilters.destinationCountry);
    }
    if (columnFilters.shippingDate) {
      filtered = filtered.filter(route => route.date_of_shipping === columnFilters.shippingDate);
    }
    if (columnFilters.containerType) {
      filtered = filtered.filter(route => route.container_type === columnFilters.containerType);
    }
    if (columnFilters.provider) {
      filtered = filtered.filter(route => route.provider === columnFilters.provider);
    }
    if (columnFilters.priceRange.min) {
      filtered = filtered.filter(route => route.price_of_shipping >= parseFloat(columnFilters.priceRange.min));
    }
    if (columnFilters.priceRange.max) {
      filtered = filtered.filter(route => route.price_of_shipping <= parseFloat(columnFilters.priceRange.max));
    }

    return filtered;
  }, [searchTerm, columnFilters]);

  // Paginate data
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredData.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredData, currentPage]);

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  // Helper functions
  const clearAllFilters = () => {
    setColumnFilters({
      originCity: '',
      originCountry: '',
      destinationCity: '',
      destinationCountry: '',
      shippingDate: '',
      priceRange: { min: '', max: '' },
      containerType: '',
      provider: ''
    });
    setSearchTerm('');
    setCurrentPage(1);
  };

  const updateColumnFilter = (key: keyof ColumnFilters, value: any) => {
    setColumnFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page when filtering
  };

  // Smart pagination logic
  const getPaginationRange = () => {
    const delta = 2; // Number of pages to show around current page
    const range = [];
    const rangeWithDots = [];

    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }

    rangeWithDots.push(...range);

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages);
    }

    return rangeWithDots.filter((item, index, array) => array.indexOf(item) === index);
  };

  // Calculate statistics
  const statistics = useMemo(() => {
    const routes = filteredData;
    const totalRoutes = routes.length;
    const averagePrice = routes.length > 0 ? routes.reduce((sum, route) => sum + route.price_of_shipping, 0) / routes.length : 0;
    const averageDays = calculateAverageTransitTime(routes);
    const uniqueOrigins = new Set(routes.map(route => route.city_of_origin)).size;
    const uniqueDestinations = new Set(routes.map(route => route.city_of_destination)).size;
    
    return {
      totalRoutes,
      averagePrice,
      averageDays,
      uniqueOrigins,
      uniqueDestinations
    };
  }, [filteredData]);

  const formatLastUpdated = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Enhanced Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-2xl">
              <BarChart3 className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 to-blue-900 bg-clip-text text-transparent">
                Shipping Matrix Dashboard
              </h1>
              <p className="text-slate-600 text-lg mt-2">
                Advanced analytics and route optimization insights
              </p>
              <div className="flex items-center space-x-4 mt-3">
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Live Data
                </Badge>
                <span className="text-xs text-slate-500">
                  Last updated: {formatLastUpdated(new Date())}
                </span>
              </div>
            </div>
          </div>

          {/* Search and Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search routes, cities, carriers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-10 pl-10 pr-4"
                />
                {searchTerm && (
                  <Button
                    onClick={() => setSearchTerm('')}
                    variant="ghost"
                    size="sm"
                    className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
              
              <Button
                onClick={() => setShowFilters(!showFilters)}
                variant={showFilters ? "default" : "outline"}
                className="flex items-center space-x-2"
              >
                <Filter className="h-4 w-4" />
                <span>Filters</span>
                {Object.values(columnFilters).some(value => 
                  typeof value === 'string' ? value : value.min || value.max
                ) && (
                  <Badge variant="secondary" className="ml-1">
                    Active
                  </Badge>
                )}
              </Button>
              
              {(searchTerm || Object.values(columnFilters).some(value => 
                typeof value === 'string' ? value : value.min || value.max
              )) && (
                <Button
                  onClick={clearAllFilters}
                  variant="ghost"
                  className="flex items-center space-x-2 text-red-600 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                  <span>Clear All</span>
                </Button>
              )}
            </div>
            
            <Button className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg">
              <Download className="h-4 w-4 mr-2" />
              Export Data
            </Button>
          </div>

          {/* Column Filters */}
          {showFilters && (
            <Card className="mt-4 bg-white/70 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center space-x-2">
                  <Filter className="h-4 w-4" />
                  <span>Advanced Filters</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <MapPin className="h-3 w-3" />
                    <span>Origin City</span>
                  </label>
                  <Select value={columnFilters.originCity} onValueChange={(value) => updateColumnFilter('originCity', value)}>
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="All cities" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All cities</SelectItem>
                      {uniqueValues.originCities.map(city => (
                        <SelectItem key={city} value={city}>{city}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <Globe className="h-3 w-3" />
                    <span>Origin Country</span>
                  </label>
                  <Select value={columnFilters.originCountry} onValueChange={(value) => updateColumnFilter('originCountry', value)}>
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="All countries" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All countries</SelectItem>
                      {uniqueValues.originCountries.map(country => (
                        <SelectItem key={country} value={country}>{country}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <Plane className="h-3 w-3" />
                    <span>Destination City</span>
                  </label>
                  <Select value={columnFilters.destinationCity} onValueChange={(value) => updateColumnFilter('destinationCity', value)}>
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="All cities" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All cities</SelectItem>
                      {uniqueValues.destinationCities.map(city => (
                        <SelectItem key={city} value={city}>{city}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <Globe className="h-3 w-3" />
                    <span>Destination Country</span>
                  </label>
                  <Select value={columnFilters.destinationCountry} onValueChange={(value) => updateColumnFilter('destinationCountry', value)}>
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="All countries" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All countries</SelectItem>
                      {uniqueValues.destinationCountries.map(country => (
                        <SelectItem key={country} value={country}>{country}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <Package className="h-3 w-3" />
                    <span>Container Type</span>
                  </label>
                  <Select value={columnFilters.containerType} onValueChange={(value) => updateColumnFilter('containerType', value)}>
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="All containers" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All containers</SelectItem>
                      {uniqueValues.containerTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <Building2 className="h-3 w-3" />
                    <span>Provider</span>
                  </label>
                  <Select value={columnFilters.provider} onValueChange={(value) => updateColumnFilter('provider', value)}>
                    <SelectTrigger className="h-8">
                      <SelectValue placeholder="All providers" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All providers</SelectItem>
                      {uniqueValues.providers.map(provider => (
                        <SelectItem key={provider} value={provider}>{provider}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <DollarSign className="h-3 w-3" />
                    <span>Min Price</span>
                  </label>
                  <Input
                    type="number"
                    placeholder="Min price"
                    value={columnFilters.priceRange.min}
                    onChange={(e) => updateColumnFilter('priceRange', { ...columnFilters.priceRange, min: e.target.value })}
                    className="h-8"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-gray-700 flex items-center space-x-1">
                    <DollarSign className="h-3 w-3" />
                    <span>Max Price</span>
                  </label>
                  <Input
                    type="number"
                    placeholder="Max price"
                    value={columnFilters.priceRange.max}
                    onChange={(e) => updateColumnFilter('priceRange', { ...columnFilters.priceRange, max: e.target.value })}
                    className="h-8"
                  />
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Enhanced Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200/50 shadow-xl shadow-blue-900/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-600">Total Routes</p>
                  <p className="text-3xl font-bold text-blue-900">{statistics.totalRoutes}</p>
                  <p className="text-xs text-blue-600 mt-1">Active shipments</p>
                </div>
                <div className="p-3 bg-blue-500 rounded-full shadow-lg">
                  <Ship className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200/50 shadow-xl shadow-green-900/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Avg. Price</p>
                  <p className="text-3xl font-bold text-green-900">{formatCurrency(statistics.averagePrice, 'USD')}</p>
                  <p className="text-xs text-green-600 mt-1">Per shipment</p>
                </div>
                <div className="p-3 bg-green-500 rounded-full shadow-lg">
                  <DollarSign className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200/50 shadow-xl shadow-yellow-900/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-yellow-600">Avg. Transit</p>
                  <p className="text-3xl font-bold text-yellow-900">{Math.round(statistics.averageDays)} days</p>
                  <p className="text-xs text-yellow-600 mt-1">Delivery time</p>
                </div>
                <div className="p-3 bg-yellow-500 rounded-full shadow-lg">
                  <Clock className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200/50 shadow-xl shadow-purple-900/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-600">Global Coverage</p>
                  <p className="text-3xl font-bold text-purple-900">{statistics.uniqueOrigins + statistics.uniqueDestinations}</p>
                  <p className="text-xs text-purple-600 mt-1">Cities served</p>
                </div>
                <div className="p-3 bg-purple-500 rounded-full shadow-lg">
                  <Globe className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Table */}
        <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-3">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <span>Shipping Routes Analysis</span>
              </CardTitle>
              <Badge variant="outline" className="px-3 py-1 bg-blue-50 text-blue-700 border-blue-200">
                {paginatedData.length} of {statistics.totalRoutes} routes
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-200">
                  <tr>
                    {/* Origin City Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-blue-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <MapPin className="h-4 w-4 text-blue-600" />
                            <span>Origin City</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.originCity && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <MapPin className="h-4 w-4 text-blue-600" />
                                <span>Filter by Origin City</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.originCity === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('originCity', '')}
                                >
                                  <span className="font-medium">All Cities</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {uniqueValues.originCities.map(city => {
                                  const count = SHIPPING_ROUTES.filter(r => r.city_of_origin === city).length;
                                  return (
                                    <Button
                                      key={city}
                                      variant={columnFilters.originCity === city ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('originCity', city)}
                                    >
                                      <span>{city}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Origin Country Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-green-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <Globe className="h-4 w-4 text-green-600" />
                            <span>Origin Country</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.originCountry && (
                              <div className="w-2 h-2 bg-green-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-green-50 to-emerald-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <Globe className="h-4 w-4 text-green-600" />
                                <span>Filter by Origin Country</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.originCountry === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('originCountry', '')}
                                >
                                  <span className="font-medium">All Countries</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {uniqueValues.originCountries.map(country => {
                                  const count = SHIPPING_ROUTES.filter(r => r.country_of_origin === country).length;
                                  return (
                                    <Button
                                      key={country}
                                      variant={columnFilters.originCountry === country ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('originCountry', country)}
                                    >
                                      <span>{country}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Destination City Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-purple-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <Plane className="h-4 w-4 text-purple-600" />
                            <span>Destination City</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.destinationCity && (
                              <div className="w-2 h-2 bg-purple-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-violet-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <Plane className="h-4 w-4 text-purple-600" />
                                <span>Filter by Destination City</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.destinationCity === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('destinationCity', '')}
                                >
                                  <span className="font-medium">All Cities</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {uniqueValues.destinationCities.map(city => {
                                  const count = SHIPPING_ROUTES.filter(r => r.city_of_destination === city).length;
                                  return (
                                    <Button
                                      key={city}
                                      variant={columnFilters.destinationCity === city ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('destinationCity', city)}
                                    >
                                      <span>{city}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Destination Country Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-green-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <Globe className="h-4 w-4 text-green-600" />
                            <span>Destination Country</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.destinationCountry && (
                              <div className="w-2 h-2 bg-green-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-green-50 to-emerald-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <Globe className="h-4 w-4 text-green-600" />
                                <span>Filter by Destination Country</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.destinationCountry === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('destinationCountry', '')}
                                >
                                  <span className="font-medium">All Countries</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {uniqueValues.destinationCountries.map(country => {
                                  const count = SHIPPING_ROUTES.filter(r => r.country_of_destination === country).length;
                                  return (
                                    <Button
                                      key={country}
                                      variant={columnFilters.destinationCountry === country ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('destinationCountry', country)}
                                    >
                                      <span>{country}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Shipping Date Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-orange-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <Calendar className="h-4 w-4 text-orange-600" />
                            <span>Shipping Date</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.shippingDate && (
                              <div className="w-2 h-2 bg-orange-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-orange-50 to-amber-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <Calendar className="h-4 w-4 text-orange-600" />
                                <span>Filter by Shipping Date</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.shippingDate === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('shippingDate', '')}
                                >
                                  <span className="font-medium">All Dates</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {[...new Set(SHIPPING_ROUTES.map(route => route.date_of_shipping))].sort().map(date => {
                                  const count = SHIPPING_ROUTES.filter(r => r.date_of_shipping === date).length;
                                  return (
                                    <Button
                                      key={date}
                                      variant={columnFilters.shippingDate === date ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('shippingDate', date)}
                                    >
                                      <span>{date}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Price Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-emerald-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <DollarSign className="h-4 w-4 text-emerald-600" />
                            <span>Price</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {(columnFilters.priceRange.min || columnFilters.priceRange.max) && (
                              <div className="w-2 h-2 bg-emerald-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-green-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <DollarSign className="h-4 w-4 text-emerald-600" />
                                <span>Filter by Price Range</span>
                              </h3>
                            </div>
                            <div className="p-4 space-y-4">
                              <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-2">
                                  <label className="text-xs font-medium text-gray-700">Min Price</label>
                                  <Input
                                    type="number"
                                    placeholder="Min"
                                    value={columnFilters.priceRange.min}
                                    onChange={(e) => updateColumnFilter('priceRange', { ...columnFilters.priceRange, min: e.target.value })}
                                    className="h-9 rounded-lg border-gray-200"
                                  />
                                </div>
                                <div className="space-y-2">
                                  <label className="text-xs font-medium text-gray-700">Max Price</label>
                                  <Input
                                    type="number"
                                    placeholder="Max"
                                    value={columnFilters.priceRange.max}
                                    onChange={(e) => updateColumnFilter('priceRange', { ...columnFilters.priceRange, max: e.target.value })}
                                    className="h-9 rounded-lg border-gray-200"
                                  />
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="flex-1 rounded-lg"
                                  onClick={() => updateColumnFilter('priceRange', { min: '', max: '' })}
                                >
                                  Clear
                                </Button>
                                <div className="text-xs text-gray-500">
                                  {filteredData.length} results
                                </div>
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Container Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-amber-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <Package className="h-4 w-4 text-amber-600" />
                            <span>Container</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.containerType && (
                              <div className="w-2 h-2 bg-amber-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-amber-50 to-yellow-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <Package className="h-4 w-4 text-amber-600" />
                                <span>Filter by Container Type</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.containerType === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('containerType', '')}
                                >
                                  <span className="font-medium">All Containers</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {uniqueValues.containerTypes.map(type => {
                                  const count = SHIPPING_ROUTES.filter(r => r.container_type === type).length;
                                  return (
                                    <Button
                                      key={type}
                                      variant={columnFilters.containerType === type ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('containerType', type)}
                                    >
                                      <span>{type}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Provider Filter */}
                    <th className="text-left p-4 font-semibold text-gray-800">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="flex items-center space-x-2 hover:bg-slate-100 rounded-lg px-3 py-2 transition-all duration-200"
                          >
                            <Building2 className="h-4 w-4 text-slate-600" />
                            <span>Provider</span>
                            <ChevronDown className="h-3 w-3 text-gray-500" />
                            {columnFilters.provider && (
                              <div className="w-2 h-2 bg-slate-500 rounded-full ml-1"></div>
                            )}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80 p-0" align="start">
                          <div className="bg-white rounded-lg shadow-xl border border-gray-200">
                            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-slate-50 to-gray-50">
                              <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                                <Building2 className="h-4 w-4 text-slate-600" />
                                <span>Filter by Provider</span>
                              </h3>
                            </div>
                            <div className="max-h-64 overflow-y-auto p-2">
                              <div className="space-y-1">
                                <Button
                                  variant={columnFilters.provider === '' ? "default" : "ghost"}
                                  size="sm"
                                  className="w-full justify-start rounded-md px-3 py-2"
                                  onClick={() => updateColumnFilter('provider', '')}
                                >
                                  <span className="font-medium">All Providers</span>
                                  <span className="ml-auto text-xs text-gray-500">
                                    ({SHIPPING_ROUTES.length})
                                  </span>
                                </Button>
                                {uniqueValues.providers.map(provider => {
                                  const count = SHIPPING_ROUTES.filter(r => r.provider === provider).length;
                                  return (
                                    <Button
                                      key={provider}
                                      variant={columnFilters.provider === provider ? "default" : "ghost"}
                                      size="sm"
                                      className="w-full justify-start rounded-md px-3 py-2"
                                      onClick={() => updateColumnFilter('provider', provider)}
                                    >
                                      <span>{provider}</span>
                                      <span className="ml-auto text-xs text-gray-500">({count})</span>
                                    </Button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </th>

                    {/* Actions Column (no filter) */}
                    <th className="text-center p-4 font-semibold text-gray-800">
                      <div className="flex items-center justify-center space-x-2 px-3 py-2">
                        <Eye className="h-4 w-4 text-blue-600" />
                        <span>Actions</span>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((route, index) => (
                    <tr 
                      key={`${route.shipment_id}-${index}`}
                      className="border-b border-gray-100 hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-indigo-50/50 transition-colors duration-200"
                    >
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span className="font-semibold text-gray-900">{route.city_of_origin}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                            {route.country_of_origin}
                          </Badge>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                          <span className="font-semibold text-gray-900">{route.city_of_destination}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                            {route.country_of_destination}
                          </Badge>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <Calendar className="h-4 w-4 text-orange-500" />
                          <span className="text-gray-700 font-medium">{route.date_of_shipping}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-bold border shadow-sm ${getPriceColorClass(route.price_of_shipping)}`}>
                          {formatCurrency(route.price_of_shipping, route.currency)}
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge variant="outline" className="font-mono bg-amber-50 text-amber-800 border-amber-200 px-3 py-1">
                          <Package className="h-3 w-3 mr-1" />
                          {route.container_type}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <Building2 className="h-4 w-4 text-slate-500" />
                          <span className="text-gray-700 font-medium">{route.provider}</span>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <Button
                          onClick={() => onViewDetails(route)}
                          size="sm"
                          className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transition-all duration-200"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Enhanced Pagination */}
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50 border-t border-blue-200">
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-700 font-medium">
                  Showing <span className="font-bold text-blue-600">{((currentPage - 1) * itemsPerPage) + 1}</span> to{' '}
                  <span className="font-bold text-blue-600">{Math.min(currentPage * itemsPerPage, filteredData.length)}</span> of{' '}
                  <span className="font-bold text-blue-600">{filteredData.length}</span> results
                </div>
                
                {filteredData.length > 0 && (
                  <div className="text-xs text-gray-500">
                    Page {currentPage} of {totalPages}
                  </div>
                )}
              </div>
              
              {totalPages > 1 && (
                <div className="flex items-center space-x-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(1)}
                    disabled={currentPage === 1}
                    className="text-xs px-2"
                  >
                    First
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="flex items-center space-x-1"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    <span>Prev</span>
                  </Button>
                  
                  <div className="flex items-center space-x-1 mx-2">
                    {getPaginationRange().map((pageNum, index) => {
                      if (pageNum === '...') {
                        return (
                          <span key={`dots-${index}`} className="px-2 py-1 text-gray-400">
                            ...
                          </span>
                        );
                      }
                      
                      const isCurrentPage = pageNum === currentPage;
                      return (
                        <Button
                          key={pageNum}
                          variant={isCurrentPage ? "default" : "outline"}
                          size="sm"
                          onClick={() => setCurrentPage(Number(pageNum))}
                          className={`min-w-[36px] h-8 ${
                            isCurrentPage 
                              ? "bg-blue-600 text-white border-blue-600 shadow-md" 
                              : "hover:bg-blue-50 hover:border-blue-300"
                          }`}
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="flex items-center space-x-1"
                  >
                    <span>Next</span>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(totalPages)}
                    disabled={currentPage === totalPages}
                    className="text-xs px-2"
                  >
                    Last
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ShippingMatrixDashboard; 