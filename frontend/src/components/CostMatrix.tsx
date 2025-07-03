import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { 
  Grid3X3, 
  MapPin,
  Users,
  Package
} from 'lucide-react';
import { DashboardFilters, CostMatrix as CostMatrixType } from '@/types/mobility';
import * as mobilityData from '@/lib/mobility-data';

interface CostMatrixProps {
  costMatrix: CostMatrixType;
  filters: DashboardFilters;
}

export const CostMatrix: React.FC<CostMatrixProps> = ({
  costMatrix,
  filters
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getCostValue = (originId: string, destId: string, categoryKey: string) => {
    const { costType } = filters;
    
    if (costType === 'shipping') {
      return costMatrix.shipping[originId]?.[destId]?.[categoryKey as '20ft' | '40ft'] || 0;
    } else {
      return costMatrix[costType][originId]?.[destId]?.[categoryKey] || 0;
    }
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
    const { costType } = filters;
    const categories = costType === 'shipping' 
      ? [{ id: '20ft', label: '20ft' }, { id: '40ft', label: '40ft' }]
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
                        {costType === 'shipping' ? (
                          <Package className="h-3 w-3" />
                        ) : (
                          <Users className="h-3 w-3" />
                        )}
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
                      const colorClass = originRegion.id === destRegion.id 
                        ? 'bg-gray-100 text-gray-400' 
                        : getColorIntensity(value, minValue, maxValue);
                      
                      return (
                        <TableCell 
                          key={`${originRegion.id}-${destRegion.id}-${category.id}`}
                          className={`text-center font-medium border-l border-blue-100 ${colorClass}`}
                        >
                          {originRegion.id === destRegion.id ? (
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
                {filters.costType === 'flights' ? 'Flight' : 
                 filters.costType === 'accommodation' ? 'Accommodation' : 'Shipping'} 
                Cost Matrix
              </span>
            </CardTitle>
            <CardDescription>
              Comprehensive cost breakdown across all regions and{' '}
              {filters.costType === 'shipping' ? 'container types' : 'family sizes'} (USD)
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
    </Card>
  );
}; 