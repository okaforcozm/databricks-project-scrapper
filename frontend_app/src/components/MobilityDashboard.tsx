import React, { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Home,
  Users,
  MapPin,
  Calendar,
  Info,
  ExternalLink,
  ChevronRight,
  Award,
  Plane,
  Package
} from 'lucide-react';

import { CostMatrix } from './CostMatrix';
import * as mobilityData from '@/lib/mobility-data';
import { DashboardFilters } from '@/types/mobility';

const MobilityDashboard: React.FC = () => {
  const [filters, setFilters] = useState<DashboardFilters>({
    originRegion: 'emea',
    destinationRegion: 'north-america',
    seniority: 'entry-level',
    familySize: 'single',
    containerType: '20ft'
  });

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isLoadingFlightData, setIsLoadingFlightData] = useState(true);
  const [isLoadingShippingData, setIsLoadingShippingData] = useState(true);
  const [flightDataLoaded, setFlightDataLoaded] = useState(false);
  const [shippingDataLoaded, setShippingDataLoaded] = useState(false);
  const [selectedCostType, setSelectedCostType] = useState<'flights' | 'accommodation' | 'shipping'>('flights');

  const costMatrix = useMemo(() => mobilityData.generateCostMatrix(), [flightDataLoaded, shippingDataLoaded]);
  const costSummaries = useMemo(() => mobilityData.generateCostSummaries(), [flightDataLoaded]);

  // Initialize real flight and shipping data on component mount
  useEffect(() => {
    const initFlightData = async () => {
      try {
        await mobilityData.initializeRealFlightData();
        console.log('Flight data loaded successfully');
        setFlightDataLoaded(true); // Trigger cost matrix regeneration
      } catch (error) {
        console.error('Failed to load flight data:', error);
      } finally {
        setIsLoadingFlightData(false);
      }
    };

    const initShippingData = async () => {
      try {
        await mobilityData.initializeRealShippingData();
        console.log('Shipping data loaded successfully');
        setShippingDataLoaded(true); // Trigger cost matrix regeneration
      } catch (error) {
        console.error('Failed to load shipping data:', error);
      } finally {
        setIsLoadingShippingData(false);
      }
    };
    
    initFlightData();
    initShippingData();
  }, []);

  // Update the timestamp every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 5 * 60 * 1000); // 5 minutes in milliseconds

    return () => clearInterval(interval);
  }, []);

  const originRegion = mobilityData.REGIONS.find(r => r.id === filters.originRegion);
  const destinationRegion = mobilityData.REGIONS.find(r => r.id === filters.destinationRegion);

  const summary = costSummaries.find(s => 
    s.origin === filters.originRegion && 
    s.destination === filters.destinationRegion
  );



  const updateFilters = (key: keyof DashboardFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatLastUpdated = (date: Date) => {
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  // Get specific route costs for the selected filters
  const getRouteSpecificCosts = () => {
    const flightCost = costMatrix.flights[filters.originRegion]?.[filters.destinationRegion]?.[filters.familySize || 'single'] || 0;
    const accommodationCost = costMatrix.accommodation[filters.originRegion]?.[filters.destinationRegion]?.[filters.familySize || 'single'] || 0;
    const shippingCost = costMatrix.shipping[filters.originRegion]?.[filters.destinationRegion]?.[filters.containerType || '20ft'] || 0;
    
    return {
      flights: flightCost,
      accommodation: accommodationCost,
      shipping: shippingCost
    };
  };

  const routeCosts = getRouteSpecificCosts();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      {/* Header with enhanced styling */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-slate-200/60 shadow-lg shadow-slate-900/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <img 
                    src="/databricks_logo.png" 
                    alt="Databricks" 
                    className="h-14 w-14 object-contain drop-shadow-sm"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      target.nextElementSibling?.classList.remove('hidden');
                    }}
                  />
                  <div className="absolute -top-1 -right-1 h-4 w-4 bg-gradient-to-r from-green-400 to-green-500 rounded-full border-2 border-white shadow-sm animate-pulse"></div>
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 bg-clip-text text-transparent">
                      Databricks Intelligence Mobility
                    </h1>
                    <div className="px-2 py-1 bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 text-xs font-semibold rounded-full border border-emerald-200">
                      LIVE
                    </div>
                  </div>
                  <p className="text-slate-600 text-lg font-medium mt-1">
                    Advanced analytics for international mobility cost intelligence
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 shadow-sm">
                <div className="relative">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <div className="absolute -top-0.5 -right-0.5 h-2 w-2 bg-green-400 rounded-full border border-white"></div>
                </div>
                <span className="text-sm font-medium text-slate-700">
                  Updated {formatLastUpdated(lastUpdated)}
                </span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-slate-50 to-gray-50 rounded-xl border border-slate-200 shadow-sm">
                <MapPin className="h-4 w-4 text-slate-600" />
                <span className="text-sm font-medium text-slate-700">
                  {mobilityData.REGIONS.length} Global Regions
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Enhanced Filters Section */}
        <Card className="mb-8 bg-white/70 backdrop-blur-sm border-0 shadow-xl shadow-slate-900/5">
          <CardHeader className="bg-gradient-to-r from-blue-50/50 to-indigo-50/50 rounded-t-lg border-b border-slate-200/50">
            <CardTitle className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg shadow-lg">
                <Users className="h-5 w-5 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold text-slate-900">Analysis Parameters</span>
                <p className="text-sm text-slate-600 font-normal mt-1">
                  Configure your mobility cost analysis with precision filtering
                </p>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {/* Enhanced Seniority Selector */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700 flex items-center space-x-2">
                  <div className="h-2 w-2 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full"></div>
                  <span>Seniority</span>
                </label>
                <Select value={filters.seniority || 'entry-level'} onValueChange={(value) => updateFilters('seniority', value)}>
                  <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {mobilityData.SENIORITY_LEVELS.map(seniority => (
                      <SelectItem key={seniority.id} value={seniority.id}>
                        <div className="flex items-center space-x-2">
                          <Award className="h-4 w-4" />
                          <div className="flex flex-col">
                            <span className="font-medium">{seniority.label}</span>
                            <span className="text-xs text-slate-500">{seniority.description}</span>
                          </div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Enhanced Origin Region */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700 flex items-center space-x-2">
                  <div className="h-2 w-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"></div>
                  <span>Origin Region</span>
                </label>
                <Select value={filters.originRegion} onValueChange={(value) => updateFilters('originRegion', value)}>
                  <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {mobilityData.REGIONS.map(region => (
                      <SelectItem key={region.id} value={region.id}>
                        <div className="flex items-center space-x-2">
                          <MapPin className="h-4 w-4" />
                          <span>{region.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Enhanced Destination Region */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700 flex items-center space-x-2">
                  <div className="h-2 w-2 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full"></div>
                  <span>Destination Region</span>
                </label>
                <Select value={filters.destinationRegion} onValueChange={(value) => updateFilters('destinationRegion', value)}>
                  <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {mobilityData.REGIONS.map(region => (
                      <SelectItem key={region.id} value={region.id}>
                        <div className="flex items-center space-x-2">
                          <MapPin className="h-4 w-4" />
                          <span>{region.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Dynamic Filter: Family Size or Container Type */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700 flex items-center space-x-2">
                  <div className="h-2 w-2 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"></div>
                  <span>{selectedCostType === 'shipping' ? 'Container Type' : 'Family Size'}</span>
                </label>
                {selectedCostType === 'shipping' ? (
                  <Select value={filters.containerType || '20ft'} onValueChange={(value) => updateFilters('containerType', value)}>
                    <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {mobilityData.CONTAINER_TYPES.map(container => (
                        <SelectItem key={container.id} value={container.id}>
                          <div className="flex items-center space-x-2">
                            <Package className="h-4 w-4" />
                            <span>{container.label}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Select value={filters.familySize || 'single'} onValueChange={(value) => updateFilters('familySize', value)}>
                    <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {mobilityData.FAMILY_SIZES.map(size => (
                        <SelectItem key={size.id} value={size.id}>
                          <div className="flex items-center space-x-2">
                            <Users className="h-4 w-4" />
                            <span>{size.label}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Route Summary Card */}
        <Card className="mb-8 bg-white/70 backdrop-blur-sm border-0 shadow-xl shadow-slate-900/5 overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-slate-50/50 to-gray-50/50 border-b border-slate-200/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-lg">
                    <MapPin className="h-7 w-7 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 h-3 w-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full border-2 border-white animate-pulse"></div>
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                    {originRegion?.name} → {destinationRegion?.name}
                  </CardTitle>
                  <CardDescription className="text-lg text-slate-600 font-medium">
                    {selectedCostType === 'shipping' 
                      ? `${mobilityData.CONTAINER_TYPES.find(ct => ct.id === filters.containerType)?.label || '20ft Container'} • Shipping analysis`
                      : `${mobilityData.FAMILY_SIZES.find(fs => fs.id === filters.familySize)?.label || 'Single'} • Mobility cost analysis`
                    }
                  </CardDescription>
                </div>
              </div>
              <div className="p-2 bg-gradient-to-r from-slate-100 to-gray-100 rounded-full">
                <ChevronRight className="h-6 w-6 text-slate-500" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Flights Cost */}
              <div 
                onClick={() => {
                  setSelectedCostType('flights');
                  // Ensure family size is set when switching to flights
                  if (!filters.familySize) {
                    updateFilters('familySize', 'single');
                  }
                }}
                className={`group relative overflow-hidden p-6 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer ${
                  selectedCostType === 'flights' 
                    ? 'bg-gradient-to-br from-sky-100 to-blue-100 border-2 border-sky-500 shadow-lg scale-105' 
                    : 'bg-gradient-to-br from-sky-50 to-blue-50 border border-sky-100 hover:scale-102'
                }`}
              >
                <div className="absolute top-3 right-3">
                  <div className={`p-2 rounded-lg ${
                    selectedCostType === 'flights' 
                      ? 'bg-gradient-to-r from-sky-200 to-blue-200' 
                      : 'bg-gradient-to-r from-sky-100 to-blue-100'
                  }`}>
                    <Plane className="h-5 w-5 text-sky-600" />
                  </div>
                </div>
                {selectedCostType === 'flights' && (
                  <div className="absolute top-3 left-3">
                    <div className="h-3 w-3 bg-sky-500 rounded-full animate-pulse"></div>
                  </div>
                )}
                <div className="text-3xl font-bold text-sky-600 mb-2">
                  {routeCosts.flights > 0 ? formatCurrency(routeCosts.flights) : 'No Data'}
                </div>
                <div className="text-sm font-semibold text-sky-700 uppercase tracking-wide">Flights</div>
                <div className="text-xs text-sky-600/70 mt-1">Round-trip costs</div>
                <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-sky-400 to-blue-400 ${
                  selectedCostType === 'flights' ? 'h-2' : ''
                }`}></div>
              </div>

              {/* Accommodation Cost */}
              <div 
                onClick={() => {
                  setSelectedCostType('accommodation');
                  // Ensure family size is set when switching to accommodation
                  if (!filters.familySize) {
                    updateFilters('familySize', 'single');
                  }
                }}
                className={`group relative overflow-hidden p-6 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer ${
                  selectedCostType === 'accommodation' 
                    ? 'bg-gradient-to-br from-emerald-100 to-green-100 border-2 border-emerald-500 shadow-lg scale-105' 
                    : 'bg-gradient-to-br from-emerald-50 to-green-50 border border-emerald-100 hover:scale-102'
                }`}
              >
                <div className="absolute top-3 right-3">
                  <div className={`p-2 rounded-lg ${
                    selectedCostType === 'accommodation' 
                      ? 'bg-gradient-to-r from-emerald-200 to-green-200' 
                      : 'bg-gradient-to-r from-emerald-100 to-green-100'
                  }`}>
                    <Home className="h-5 w-5 text-emerald-600" />
                  </div>
                </div>
                {selectedCostType === 'accommodation' && (
                  <div className="absolute top-3 left-3">
                    <div className="h-3 w-3 bg-emerald-500 rounded-full animate-pulse"></div>
                  </div>
                )}
                <div className="text-3xl font-bold text-emerald-600 mb-2">
                  {routeCosts.accommodation > 0 ? formatCurrency(routeCosts.accommodation) : 'No Data'}
                </div>
                <div className="text-sm font-semibold text-emerald-700 uppercase tracking-wide">Accommodation</div>
                <div className="text-xs text-emerald-600/70 mt-1">Monthly housing</div>
                <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 to-green-400 ${
                  selectedCostType === 'accommodation' ? 'h-2' : ''
                }`}></div>
              </div>

              {/* Shipping Cost */}
              <div 
                onClick={() => {
                  setSelectedCostType('shipping');
                  // Set default container type when switching to shipping
                  if (!filters.containerType) {
                    updateFilters('containerType', '20ft');
                  }
                }}
                className={`group relative overflow-hidden p-6 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer ${
                  selectedCostType === 'shipping' 
                    ? 'bg-gradient-to-br from-orange-100 to-amber-100 border-2 border-orange-500 shadow-lg scale-105' 
                    : 'bg-gradient-to-br from-orange-50 to-amber-50 border border-orange-100 hover:scale-102'
                }`}
              >
                <div className="absolute top-3 right-3">
                  <div className={`p-2 rounded-lg ${
                    selectedCostType === 'shipping' 
                      ? 'bg-gradient-to-r from-orange-200 to-amber-200' 
                      : 'bg-gradient-to-r from-orange-100 to-amber-100'
                  }`}>
                    <Package className="h-5 w-5 text-orange-600" />
                  </div>
                </div>
                {selectedCostType === 'shipping' && (
                  <div className="absolute top-3 left-3">
                    <div className="h-3 w-3 bg-orange-500 rounded-full animate-pulse"></div>
                  </div>
                )}
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {routeCosts.shipping > 0 ? formatCurrency(routeCosts.shipping) : 'No Data'}
                </div>
                <div className="text-sm font-semibold text-orange-700 uppercase tracking-wide">Shipping</div>
                <div className="text-xs text-orange-600/70 mt-1">Container shipping</div>
                <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-400 to-amber-400 ${
                  selectedCostType === 'shipping' ? 'h-2' : ''
                }`}></div>
              </div>
            </div>

            {/* Total Cost Summary */}
            <div className="mt-6 p-4 bg-gradient-to-r from-slate-50 to-gray-50 rounded-xl border border-slate-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-slate-100 to-gray-100 rounded-lg">
                    <Calendar className="h-5 w-5 text-slate-600" />
                  </div>
                  <div>
                    <div className="text-lg font-bold text-slate-900">
                      Total Estimated Cost
                    </div>
                    <div className="text-sm text-slate-600">
                      Combined mobility package
                    </div>
                  </div>
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {formatCurrency(routeCosts.flights + routeCosts.accommodation + routeCosts.shipping)}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Main Content */}
        <div className="space-y-6">
          <CostMatrix 
            costMatrix={costMatrix}
            filters={filters}
            selectedCostType={selectedCostType}
          />
        </div>

        {/* Enhanced Footer */}
        <div className="mt-16 pt-12 border-t border-slate-200/60">
          <div className="bg-gradient-to-r from-slate-50 to-gray-50 rounded-2xl p-8 shadow-lg shadow-slate-900/5">
            <div className="text-center space-y-6">
              <div className="flex items-center justify-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-lg">
                  <Info className="h-5 w-5 text-blue-600" />
                </div>
                <span className="text-slate-600 font-medium">
                  Data represents potential peak costs for strategic planning purposes
                </span>
              </div>
              <div className="flex items-center justify-center space-x-8">
                <a 
                  href="https://altovita.com" 
                  target="_blank" 
                  rel="noopener" 
                  className="group flex items-center space-x-2 px-4 py-3 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105"
                >
                  <div className="p-1 bg-green-100 rounded">
                    <Home className="h-4 w-4 text-green-600" />
                  </div>
                  <span className="font-medium text-slate-700 group-hover:text-green-600">Alto Vita</span>
                  <ExternalLink className="h-3 w-3 text-slate-400 group-hover:text-green-600" />
                </a>
                <div className="h-8 w-px bg-slate-300"></div>
                <a 
                  href="https://silverdoor.com" 
                  target="_blank" 
                  rel="noopener" 
                  className="group flex items-center space-x-2 px-4 py-3 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105"
                >
                  <div className="p-1 bg-purple-100 rounded">
                    <Home className="h-4 w-4 text-purple-600" />
                  </div>
                  <span className="font-medium text-slate-700 group-hover:text-purple-600">Silverdoor</span>
                  <ExternalLink className="h-3 w-3 text-slate-400 group-hover:text-purple-600" />
                </a>
              </div>
              <div className="pt-4 border-t border-slate-200">
                <p className="text-xs text-slate-500">
                  © 2025 Databricks Intelligence Mobility. Powered by advanced analytics and real-time data processing.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobilityDashboard; 