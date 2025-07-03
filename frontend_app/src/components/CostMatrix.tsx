import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Grid3X3, 
  MapPin,
  Users,
  ExternalLink,
  Camera,
  Plane,
  Package,
  Home
} from 'lucide-react';
import { DashboardFilters, CostMatrix as CostMatrixType } from '@/types/mobility';
import * as mobilityData from '@/lib/mobility-data';

interface CostMatrixProps {
  costMatrix: CostMatrixType;
  filters: DashboardFilters;
  selectedCostType: 'flights' | 'accommodation' | 'shipping';
}

export const CostMatrix: React.FC<CostMatrixProps> = ({
  costMatrix,
  filters,
  selectedCostType
}) => {
  const [selectedRoute, setSelectedRoute] = useState<{
    origin: string;
    destination: string;
    passengerType: string;
    price: number;
  } | null>(null);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getCostValue = (originId: string, destId: string, categoryKey: string) => {
    return costMatrix[selectedCostType][originId]?.[destId]?.[categoryKey] || 0;
  };

  const getColorIntensity = (value: number, min: number, max: number) => {
    if (max === min) return 'bg-blue-50';
    const intensity = (value - min) / (max - min);
    if (intensity < 0.2) return 'bg-green-50 text-green-800';
    if (intensity < 0.4) return 'bg-green-100 text-green-800';
    if (intensity < 0.6) return 'bg-yellow-50 text-yellow-800';
    if (intensity < 0.8) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const renderMatrix = () => {
    // For flights and accommodation, use family sizes; for shipping, use container types
    const categories = selectedCostType === 'shipping' 
      ? [
          { id: '20ft', label: '20ft Container', adults: 0, children: 0, multiplier: 1.0 },
          { id: '40ft', label: '40ft Container', adults: 0, children: 0, multiplier: 1.0 }
        ]
      : mobilityData.FAMILY_SIZES;

    // Calculate min/max for color coding
    const allValues: number[] = [];
    mobilityData.REGIONS.forEach(origin => {
      mobilityData.REGIONS.forEach(dest => {
        if (origin.id !== dest.id) {
          categories.forEach(cat => {
            const value = getCostValue(origin.id, dest.id, cat.id);
            if (value > 0) allValues.push(value);
          });
        }
      });
    });

    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);

    return (
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-40 bg-gray-50">
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>Origin / Destination</span>
                </div>
              </TableHead>
              {mobilityData.REGIONS.map(region => (
                <React.Fragment key={region.id}>
                  <TableHead 
                    colSpan={categories.length} 
                    className="text-center bg-blue-50 border-l border-blue-200"
                  >
                    <div className="flex items-center justify-center space-x-1">
                      <MapPin className="h-3 w-3" />
                      <span className="font-medium">{region.name}</span>
                    </div>
                  </TableHead>
                </React.Fragment>
              ))}
            </TableRow>
            <TableRow>
              <TableHead className="bg-gray-50"></TableHead>
              {mobilityData.REGIONS.map(region => (
                <React.Fragment key={`${region.id}-sub`}>
                  {categories.map(category => (
                    <TableHead 
                      key={`${region.id}-${category.id}`}
                      className="text-center text-xs bg-blue-25 border-l border-blue-100"
                    >
                      <div className="flex items-center justify-center space-x-1">
                        <Users className="h-3 w-3" />
                        <span>{category.label}</span>
                      </div>
                    </TableHead>
                  ))}
                </React.Fragment>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {mobilityData.REGIONS.map(originRegion => (
              <TableRow key={originRegion.id}>
                <TableCell className="font-medium bg-gray-50 border-r">
                  <div className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4 text-gray-500" />
                    <span>{originRegion.name}</span>
                  </div>
                </TableCell>
                {mobilityData.REGIONS.map(destRegion => (
                  <React.Fragment key={`${originRegion.id}-${destRegion.id}`}>
                    {categories.map(category => {
                      const value = getCostValue(originRegion.id, destRegion.id, category.id);
                      const colorClass = value === 0 
                        ? 'bg-gray-100 text-gray-400' 
                        : getColorIntensity(value, minValue, maxValue);
                      
                      return (
                        <TableCell 
                          key={`${originRegion.id}-${destRegion.id}-${category.id}`}
                          className={`text-center font-medium border-l border-blue-100 ${colorClass} ${
                            value > 0 ? 'cursor-pointer hover:bg-blue-50' : ''
                          }`}
                          onClick={() => {
                            if (value > 0) {
                              setSelectedRoute({
                                origin: originRegion.id,
                                destination: destRegion.id,
                                passengerType: category.id,
                                price: value
                              });
                            }
                          }}
                        >
                          {value === 0 ? (
                            <span className="text-gray-400">—</span>
                          ) : (
                            <span className="text-sm">
                              {formatCurrency(value)}
                            </span>
                          )}
                        </TableCell>
                      );
                    })}
                  </React.Fragment>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <Grid3X3 className="h-5 w-5 text-blue-600" />
              <span>
                {selectedCostType === 'flights' && 'Flight Cost Matrix'}
                {selectedCostType === 'accommodation' && 'Accommodation Cost Matrix'}
                {selectedCostType === 'shipping' && 'Shipping Cost Matrix'}
              </span>
            </CardTitle>
            <CardDescription>
              {selectedCostType === 'flights' && 'Comprehensive flight cost breakdown across all regions and family sizes (USD)'}
              {selectedCostType === 'accommodation' && 'Monthly accommodation costs from Alto Vita and Silverdoor providers (USD)'}
              {selectedCostType === 'shipping' && 'Container shipping costs for household goods across regions (USD)'}
            </CardDescription>
          </div>
          <div className="hidden md:flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              <MapPin className="h-3 w-3 mr-1" />
              {mobilityData.REGIONS.length} Regions
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {renderMatrix()}
        
        {/* Legend */}
        <div className="mt-6 pt-4 border-t">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              <strong>Color Legend:</strong> Cost intensity from lowest (green) to highest (red)
            </div>
            <div className="flex items-center space-x-4 text-xs">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-green-100 rounded"></div>
                <span>Low Cost</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-yellow-100 rounded"></div>
                <span>Medium Cost</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-red-100 rounded"></div>
                <span>High Cost</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>

      {/* Evidence Modal */}
      <Dialog open={!!selectedRoute} onOpenChange={() => setSelectedRoute(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {selectedCostType === 'flights' && <Plane className="h-5 w-5 text-blue-600" />}
              {selectedCostType === 'shipping' && <Package className="h-5 w-5 text-orange-600" />}
              {selectedCostType === 'accommodation' && <Home className="h-5 w-5 text-green-600" />}
              <span>
                {selectedCostType === 'flights' && 'Flight Evidence: '}
                {selectedCostType === 'shipping' && 'Shipping Evidence: '}
                {selectedCostType === 'accommodation' && 'Accommodation Evidence: '}
                {selectedRoute && mobilityData.REGIONS.find(r => r.id === selectedRoute.origin)?.name} → {selectedRoute && mobilityData.REGIONS.find(r => r.id === selectedRoute.destination)?.name}
              </span>
            </DialogTitle>
            <DialogDescription>
              {selectedRoute && (
                <>
                  {selectedCostType === 'flights' && (
                    <>Flight data for {mobilityData.FAMILY_SIZES.find(f => f.id === selectedRoute.passengerType)?.label} passengers</>
                  )}
                  {selectedCostType === 'shipping' && (
                    <>Shipping data for {selectedRoute.passengerType} container</>
                  )}
                  {selectedCostType === 'accommodation' && (
                    <>Accommodation data for {mobilityData.FAMILY_SIZES.find(f => f.id === selectedRoute.passengerType)?.label}</>
                  )}
                  {' - Average Price: '}{formatCurrency(selectedRoute.price)}
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          
          {selectedRoute && (
            <div className="space-y-4">
              {(() => {
                let evidence: any[] = [];
                let stats: any = null;

                if (selectedCostType === 'flights') {
                  evidence = mobilityData.getFlightEvidence(
                    selectedRoute.origin,
                    selectedRoute.destination,
                    selectedRoute.passengerType
                  );
                  stats = mobilityData.getFlightStatistics(
                    selectedRoute.origin,
                    selectedRoute.destination,
                    selectedRoute.passengerType
                  );
                } else if (selectedCostType === 'shipping') {
                  evidence = mobilityData.getShippingEvidence(
                    selectedRoute.origin,
                    selectedRoute.destination,
                    selectedRoute.passengerType
                  );
                  stats = mobilityData.getShippingStatistics(
                    selectedRoute.origin,
                    selectedRoute.destination,
                    selectedRoute.passengerType
                  );
                }

                if (!evidence.length) {
                  return (
                    <div className="text-center py-8 text-gray-500">
                      {selectedCostType === 'flights' && <Plane className="h-12 w-12 mx-auto mb-4 opacity-50" />}
                      {selectedCostType === 'shipping' && <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />}
                      {selectedCostType === 'accommodation' && <Home className="h-12 w-12 mx-auto mb-4 opacity-50" />}
                      <p>No real {selectedCostType} data available for this route.</p>
                      <p className="text-sm mt-2">We only display prices based on actual scraped {selectedCostType} data.</p>
                      <p className="text-sm mt-1">Try different categories or check back later as we collect more data.</p>
                    </div>
                  );
                }

                return (
                  <>
                    {stats && (
                      <div className="grid grid-cols-4 gap-4 p-4 bg-blue-50 rounded-lg">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{formatCurrency(stats.averagePrice)}</div>
                          <div className="text-sm text-gray-600">Average Price</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">{formatCurrency(stats.minPrice)}</div>
                          <div className="text-sm text-gray-600">Min Price</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">{formatCurrency(stats.maxPrice)}</div>
                          <div className="text-sm text-gray-600">Max Price</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">{stats.sampleCount}</div>
                          <div className="text-sm text-gray-600">Total Samples</div>
                        </div>
                      </div>
                    )}

                    <div className="grid gap-4">
                      {evidence.map((item, index) => (
                        <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                {selectedCostType === 'flights' && (
                                  <>
                                    <Badge variant="outline" className="font-mono">{item.airline_code}</Badge>
                                    <span className="text-sm text-gray-600">{item.source}</span>
                                    <span className="text-sm text-gray-500">{item.total_flight_time}</span>
                                  </>
                                )}
                                {selectedCostType === 'shipping' && (
                                  <>
                                    <Badge variant="outline" className="font-mono">{item.container_type}</Badge>
                                    <span className="text-sm text-gray-600">{item.provider}</span>
                                    <span className="text-sm text-gray-500">{item.total_shipping_time_days} days</span>
                                  </>
                                )}
                              </div>
                              <div className="text-lg font-semibold">
                                {selectedCostType === 'flights' && `${item.departure_city} → ${item.destination_city}`}
                                {selectedCostType === 'shipping' && `${item.city_of_origin} → ${item.city_of_destination}`}
                              </div>
                              <div className="text-sm text-gray-600">
                                {selectedCostType === 'flights' && `Flight Date: ${item.flight_date}`}
                                {selectedCostType === 'shipping' && `Shipping Date: ${item.date_of_shipping}`}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-xl font-bold text-green-600">
                                {selectedCostType === 'flights' && formatCurrency(item.priceUSD)}
                                {selectedCostType === 'shipping' && formatCurrency(item.price_of_shipping)}
                              </div>
                              {selectedCostType === 'flights' && item.currency !== 'USD' && (
                                <div className="text-sm text-gray-500">
                                  {item.price} {item.currency}
                                </div>
                              )}
                              {selectedCostType === 'shipping' && item.currency !== 'USD' && (
                                <div className="text-sm text-gray-500">
                                  {item.price_of_shipping} {item.currency}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-4">
                            {item.screenshot_url && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => window.open(item.screenshot_url!, '_blank')}
                                className="flex items-center space-x-1"
                              >
                                <Camera className="h-4 w-4" />
                                <span>Screenshot</span>
                              </Button>
                            )}
                            
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(
                                selectedCostType === 'flights' ? item.booking_url : item.website_link, 
                                '_blank'
                              )}
                              className="flex items-center space-x-1"
                            >
                              <ExternalLink className="h-4 w-4" />
                              <span>{selectedCostType === 'flights' ? 'Book Now' : 'View Quote'}</span>
                            </Button>
                            
                            <span className="text-xs text-gray-400 ml-auto">
                              Scraped: {new Date(
                                selectedCostType === 'flights' ? item.scraping_datetime : item.datetime_of_scraping
                              ).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                );
              })()}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
}; 