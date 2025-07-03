import React, { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { 
  Plane, 
  Home, 
  Package, 
  TrendingUp, 
  DollarSign, 
  Users,
  MapPin,
  Calendar,
  Info,
  ExternalLink,
  ChevronRight,
  BarChart3,
  Grid3X3,
  FileText
} from 'lucide-react';

import { CostVisualization } from './CostVisualization';
import { CostMatrix } from './CostMatrix';
import { EvidencePanel } from './EvidencePanel';
import * as mobilityData from '@/lib/mobility-data';
import { DashboardFilters } from '@/types/mobility';

const MobilityDashboard: React.FC = () => {
  const [filters, setFilters] = useState<DashboardFilters>({
    costType: 'flights',
    originRegion: 'emea',
    destinationRegion: 'north-america',
    familySize: 'single',
    containerType: '20ft'
  });

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const costMatrix = useMemo(() => mobilityData.generateCostMatrix(), []);
  const costSummaries = useMemo(() => mobilityData.generateCostSummaries(), []);

  // Update the timestamp every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 5 * 60 * 1000); // 5 minutes in milliseconds

    return () => clearInterval(interval);
  }, []);

  const currentCostType = mobilityData.COST_TYPES.find(ct => ct.id === filters.costType);
  const originRegion = mobilityData.REGIONS.find(r => r.id === filters.originRegion);
  const destinationRegion = mobilityData.REGIONS.find(r => r.id === filters.destinationRegion);

  const summary = costSummaries.find(s => 
    s.costType === filters.costType && 
    s.origin === filters.originRegion && 
    s.destination === filters.destinationRegion
  );

  const getCostIcon = (costType: string) => {
    switch (costType) {
      case 'flights': return Plane;
      case 'accommodation': return Home;
      case 'shipping': return Package;
      default: return DollarSign;
    }
  };

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
                <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl hidden shadow-lg">
                  <TrendingUp className="h-8 w-8 text-white" />
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
              <Button
                onClick={() => window.location.href = '/shipping'}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-lg px-4 py-2"
              >
                <Package className="h-4 w-4 mr-2" />
                Shipping Matrix
              </Button>
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
              {/* Enhanced Cost Type Selector */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700 flex items-center space-x-2">
                  <div className="h-2 w-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"></div>
                  <span>Cost Type</span>
                </label>
                <Select value={filters.costType} onValueChange={(value) => updateFilters('costType', value)}>
                  <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {mobilityData.COST_TYPES.map(costType => {
                      const Icon = getCostIcon(costType.id);
                      return (
                        <SelectItem key={costType.id} value={costType.id}>
                          <div className="flex items-center space-x-2">
                            <Icon className="h-4 w-4" />
                            <span>{costType.label}</span>
                          </div>
                        </SelectItem>
                      );
                    })}
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

              {/* Enhanced Family Size or Container Type */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700 flex items-center space-x-2">
                  <div className="h-2 w-2 bg-gradient-to-r from-orange-500 to-amber-500 rounded-full"></div>
                  <span>{filters.costType === 'shipping' ? 'Container Type' : 'Family Size'}</span>
                </label>
                {filters.costType === 'shipping' ? (
                  <Select value={filters.containerType || '20ft'} onValueChange={(value) => updateFilters('containerType', value)}>
                    <SelectTrigger className="w-full h-12 border-slate-200 shadow-sm bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all duration-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="20ft">20ft Container</SelectItem>
                      <SelectItem value="40ft">40ft Container</SelectItem>
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
                    {React.createElement(getCostIcon(filters.costType), { 
                      className: "h-7 w-7 text-white" 
                    })}
                  </div>
                  <div className="absolute -top-1 -right-1 h-3 w-3 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full border-2 border-white animate-pulse"></div>
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                    {originRegion?.name} → {destinationRegion?.name}
                  </CardTitle>
                  <CardDescription className="text-lg text-slate-600 font-medium">
                    {currentCostType?.description}
                  </CardDescription>
                </div>
              </div>
              <div className="p-2 bg-gradient-to-r from-slate-100 to-gray-100 rounded-full">
                <ChevronRight className="h-6 w-6 text-slate-500" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-8">
            {summary && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-50 to-green-50 p-6 rounded-2xl border border-emerald-100 shadow-sm hover:shadow-lg transition-all duration-300">
                  <div className="absolute top-2 right-2 h-2 w-2 bg-emerald-400 rounded-full"></div>
                  <div className="text-3xl font-bold text-emerald-600 mb-2">
                    {formatCurrency(summary.minCost)}
                  </div>
                  <div className="text-sm font-semibold text-emerald-700 uppercase tracking-wide">Minimum Cost</div>
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 to-green-400"></div>
                </div>
                <div className="group relative overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-100 shadow-sm hover:shadow-lg transition-all duration-300">
                  <div className="absolute top-2 right-2 h-2 w-2 bg-blue-400 rounded-full"></div>
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {formatCurrency(summary.avgCost)}
                  </div>
                  <div className="text-sm font-semibold text-blue-700 uppercase tracking-wide">Average Cost</div>
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-400 to-indigo-400"></div>
                </div>
                <div className="group relative overflow-hidden bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-2xl border border-orange-100 shadow-sm hover:shadow-lg transition-all duration-300">
                  <div className="absolute top-2 right-2 h-2 w-2 bg-orange-400 rounded-full"></div>
                  <div className="text-3xl font-bold text-orange-600 mb-2">
                    {formatCurrency(summary.maxCost)}
                  </div>
                  <div className="text-sm font-semibold text-orange-700 uppercase tracking-wide">Maximum Cost</div>
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-400 to-amber-400"></div>
                </div>
                <div className="group relative overflow-hidden bg-gradient-to-br from-purple-50 to-violet-50 p-6 rounded-2xl border border-purple-100 shadow-sm hover:shadow-lg transition-all duration-300">
                  <div className="absolute top-2 right-2 h-2 w-2 bg-purple-400 rounded-full"></div>
                  <div className="text-3xl font-bold text-purple-600 mb-2">
                    {summary.totalRoutes}
                  </div>
                  <div className="text-sm font-semibold text-purple-700 uppercase tracking-wide">Data Points</div>
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-400 to-violet-400"></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Enhanced Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-8">
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border-0 shadow-lg shadow-slate-900/5 p-2">
            <TabsList className="grid w-full grid-cols-4 bg-transparent gap-1">
              <TabsTrigger 
                value="overview" 
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-200 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg hover:bg-slate-50"
              >
                <TrendingUp className="h-4 w-4" />
                <span>Overview</span>
              </TabsTrigger>
              <TabsTrigger 
                value="visualization" 
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-200 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg hover:bg-slate-50"
              >
                <BarChart3 className="h-4 w-4" />
                <span>Analytics</span>
              </TabsTrigger>
              <TabsTrigger 
                value="matrix" 
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-200 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg hover:bg-slate-50"
              >
                <Grid3X3 className="h-4 w-4" />
                <span>Matrix</span>
              </TabsTrigger>
              <TabsTrigger 
                value="evidence" 
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-200 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg hover:bg-slate-50"
              >
                <FileText className="h-4 w-4" />
                <span>Sources</span>
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CostVisualization 
                costMatrix={costMatrix}
                filters={filters}
                type="chart"
              />
              <CostVisualization 
                costMatrix={costMatrix}
                filters={filters}
                type="comparison"
              />
            </div>
          </TabsContent>

          <TabsContent value="visualization" className="space-y-6">
            <CostVisualization 
              costMatrix={costMatrix}
              filters={filters}
              type="detailed"
            />
          </TabsContent>

          <TabsContent value="matrix" className="space-y-6">
            <CostMatrix 
              costMatrix={costMatrix}
              filters={filters}
            />
          </TabsContent>

          <TabsContent value="evidence" className="space-y-6">
            <EvidencePanel 
              evidence={mobilityData.SAMPLE_EVIDENCE}
              filters={filters}
            />
          </TabsContent>
        </Tabs>

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