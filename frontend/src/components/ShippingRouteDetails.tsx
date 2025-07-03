import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft,
  MapPin, 
  Package, 
  DollarSign, 
  Clock,
  Calendar,
  ExternalLink,
  Truck,
  Globe,
  Zap,
  Activity,
  Target,
  Info,
  TreePine,
  Building2,
  Ship,
  Camera
} from 'lucide-react';

import { ShippingRoute } from '@/types/shipping';
import { 
  formatCurrency, 
  getPriceColorClass, 
  getTransitTimeColorClass,
  formatDate,
  formatDateTime,
  safeField,
  parseTransitTime
} from '@/lib/shipping-utils';

interface ShippingRouteDetailsProps {
  route: ShippingRoute;
  onBack: () => void;
}

const ShippingRouteDetails: React.FC<ShippingRouteDetailsProps> = ({ route, onBack }) => {

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-slate-200/60 shadow-lg shadow-slate-900/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                onClick={onBack}
                variant="outline"
                className="bg-white/70 backdrop-blur-sm hover:bg-white shadow-sm"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Routes
              </Button>
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg">
                  <Ship className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 bg-clip-text text-transparent">
                    Route Details: {route.city_of_origin} → {route.city_of_destination}
                  </h1>
                  <p className="text-slate-600 font-medium">
                    Shipment ID: {safeField(route.shipment_id, 'N/A')} • Rate ID: {safeField(route.rate_id, 'N/A')}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                onClick={() => window.open(route.website_link, '_blank')}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                View on Searates
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - 2/3 width */}
          <div className="lg:col-span-2 space-y-8">
            {/* Route Overview */}
            <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
              <CardHeader className="bg-gradient-to-r from-blue-50/50 to-indigo-50/50 rounded-t-lg border-b border-slate-200/50">
                <CardTitle className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg shadow-lg">
                    <MapPin className="h-5 w-5 text-white" />
                  </div>
                  <span>Route Overview</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* Origin */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <Building2 className="h-5 w-5 text-green-600" />
                      </div>
                      <span className="text-lg font-semibold text-slate-700">Origin</span>
                    </div>
                    <div className="pl-9">
                      <div className="text-2xl font-bold text-slate-900">{route.city_of_origin}</div>
                      <div className="text-lg text-slate-600">{route.country_of_origin}</div>
                    </div>
                  </div>

                  {/* Destination */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 bg-red-100 rounded-lg">
                        <Target className="h-5 w-5 text-red-600" />
                      </div>
                      <span className="text-lg font-semibold text-slate-700">Destination</span>
                    </div>
                    <div className="pl-9">
                      <div className="text-2xl font-bold text-slate-900">{route.city_of_destination}</div>
                      <div className="text-lg text-slate-600">{route.country_of_destination}</div>
                    </div>
                  </div>
                </div>

                <Separator className="my-8" />

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className={`p-4 rounded-xl border-2 ${getPriceColorClass(route.price_of_shipping)}`}>
                    <div className="flex items-center space-x-3">
                      <DollarSign className="h-8 w-8" />
                      <div>
                        <div className="text-sm font-medium opacity-80">Total Cost</div>
                        <div className="text-2xl font-bold">{formatCurrency(route.price_of_shipping)}</div>
                        <div className="text-xs opacity-60">{route.currency}</div>
                      </div>
                    </div>
                  </div>

                  <div className={`p-4 rounded-xl ${getTransitTimeColorClass(route.total_shipping_time_days)}`}>
                    <div className="flex items-center space-x-3">
                      <Clock className="h-8 w-8" />
                      <div>
                        <div className="text-sm font-medium opacity-80">Transit Time</div>
                        <div className="text-2xl font-bold">{safeField(route.total_shipping_time_days, 'N/A')}</div>
                        <div className="text-xs opacity-60">days</div>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-purple-50 text-purple-600 border-2 border-purple-200">
                    <div className="flex items-center space-x-3">
                      <Globe className="h-8 w-8" />
                      <div>
                        <div className="text-sm font-medium opacity-80">Distance</div>
                        <div className="text-2xl font-bold">{safeField(route.distance, 'N/A')}</div>
                        <div className="text-xs opacity-60">km</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Shipping Details */}
            <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg shadow-lg">
                    <Package className="h-5 w-5 text-white" />
                  </div>
                  <span>Shipping Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <span className="font-medium text-slate-700">Container Type</span>
                      <Badge variant="outline" className="font-mono text-lg px-3 py-1">
                        {route.container_type}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <span className="font-medium text-slate-700">Carrier</span>
                      <span className="font-semibold text-slate-900">{safeField(route.carrier, 'N/A')}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <span className="font-medium text-slate-700">Provider</span>
                      <span className="font-semibold text-slate-900">{route.provider}</span>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <span className="font-medium text-slate-700">Shipping Date</span>
                      <span className="font-semibold text-slate-900">{formatDate(route.date_of_shipping)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <span className="font-medium text-slate-700">Point Total</span>
                      <span className="font-semibold text-slate-900">{route.point_total ? formatCurrency(route.point_total) : 'N/A'}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <span className="font-medium text-slate-700">Route Total</span>
                      <span className="font-semibold text-slate-900">{route.route_total ? formatCurrency(route.route_total) : 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Environmental Impact */}
            <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg shadow-lg">
                    <TreePine className="h-5 w-5 text-white" />
                  </div>
                  <span>Environmental Impact</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
                    <div className="flex items-center space-x-3 mb-4">
                      <Activity className="h-6 w-6 text-green-600" />
                      <span className="font-semibold text-green-800">CO₂ Emissions</span>
                    </div>
                    <div className="text-3xl font-bold text-green-900 mb-2">
                      {(route.co2_amount / 1000).toFixed(1)}t
                    </div>
                    <div className="text-sm text-green-600">
                      Total carbon footprint for this shipment
                    </div>
                  </div>

                  <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                    <div className="flex items-center space-x-3 mb-4">
                      <DollarSign className="h-6 w-6 text-blue-600" />
                      <span className="font-semibold text-blue-800">Carbon Cost</span>
                    </div>
                    <div className="text-3xl font-bold text-blue-900 mb-2">
                      {formatCurrency(route.co2_price)}
                    </div>
                    <div className="text-sm text-blue-600">
                      Environmental impact pricing
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Validity Period */}
            <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg shadow-lg">
                    <Calendar className="h-5 w-5 text-white" />
                  </div>
                  <span>Rate Validity</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <div className="text-sm font-medium text-orange-600 mb-2">Valid From</div>
                    <div className="text-lg font-bold text-orange-900">{formatDate(route.validity_from)}</div>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                    <div className="text-sm font-medium text-red-600 mb-2">Valid Until</div>
                    <div className="text-lg font-bold text-red-900">{formatDate(route.validity_to)}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - 1/3 width */}
          <div className="space-y-8">
            {/* Screenshot */}
            <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg shadow-lg">
                    <Camera className="h-5 w-5 text-white" />
                  </div>
                  <span>Live Screenshot</span>
                </CardTitle>
                <CardDescription>
                  Real-time capture from Searates logistics explorer
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="relative group">
                  <img
                    src={route.screenshot_url}
                    alt={`Screenshot of ${route.city_of_origin} to ${route.city_of_destination} route`}
                    className="w-full h-auto rounded-lg shadow-lg border border-slate-200 group-hover:shadow-xl transition-shadow"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjMuNDQzNyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM2NjY2NjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5TY3JlZW5zaG90IE5vdCBBdmFpbGFibGU8L3RleHQ+PC9zdmc+';
                    }}
                  />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <Button
                      onClick={() => window.open(route.screenshot_url, '_blank')}
                      variant="secondary"
                      className="bg-white/90 hover:bg-white shadow-lg"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View Full Size
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Meta Information */}
            <Card className="bg-white/80 backdrop-blur-sm shadow-xl shadow-slate-900/5">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-slate-500 to-gray-600 rounded-lg shadow-lg">
                    <Info className="h-5 w-5 text-white" />
                  </div>
                  <span>Meta Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <span className="text-sm font-medium text-slate-700">Shipment ID</span>
                  <code className="px-2 py-1 bg-slate-200 rounded text-xs font-mono">
                    {route.shipment_id}
                  </code>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <span className="text-sm font-medium text-slate-700">Rate ID</span>
                  <code className="px-2 py-1 bg-slate-200 rounded text-xs font-mono">
                    {route.rate_id}
                  </code>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <span className="text-sm font-medium text-slate-700">Scraped At</span>
                  <span className="text-xs text-slate-600">
                    {formatDateTime(route.datetime_of_scraping)}
                  </span>
                </div>

                <Separator />

                <div className="flex flex-col space-y-3">
                  <Button
                    onClick={() => window.open(route.website_link, '_blank')}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View on Searates
                  </Button>
                  
                  <Button
                    onClick={() => navigator.clipboard.writeText(route.website_link)}
                    variant="outline"
                    className="w-full"
                  >
                    Copy Link
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShippingRouteDetails; 