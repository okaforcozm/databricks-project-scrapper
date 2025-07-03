import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  BarChart3, 
  TrendingUp, 
  DollarSign,
  Users,
  Package
} from 'lucide-react';
import { DashboardFilters, CostMatrix } from '@/types/mobility';
import * as mobilityData from '@/lib/mobility-data';

interface CostVisualizationProps {
  costMatrix: CostMatrix;
  filters: DashboardFilters;
  type: 'chart' | 'comparison' | 'detailed';
}

export const CostVisualization: React.FC<CostVisualizationProps> = ({
  costMatrix,
  filters,
  type
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getVisualizationData = () => {
    const { costType, originRegion, destinationRegion, familySize, containerType } = filters;
    
    if (costType === 'shipping') {
      const shippingData = costMatrix.shipping[originRegion]?.[destinationRegion];
      if (!shippingData) return [];
      
      return [
        { label: '20ft Container', value: shippingData['20ft'], color: 'bg-blue-500' },
        { label: '40ft Container', value: shippingData['40ft'], color: 'bg-blue-700' }
      ];
    } else {
      const data = costMatrix[costType][originRegion]?.[destinationRegion];
      if (!data) return [];
      
      return mobilityData.FAMILY_SIZES.map(size => ({
        label: size.label,
        value: data[size.id],
        color: size.id === familySize ? 'bg-blue-600' : 'bg-blue-400'
      }));
    }
  };

  const getComparisonData = () => {
    const { costType, familySize } = filters;
    const data: { origin: string; destination: string; cost: number }[] = [];
    
    mobilityData.REGIONS.forEach(origin => {
      mobilityData.REGIONS.forEach(destination => {
        if (origin.id !== destination.id) {
          let cost = 0;
          if (costType === 'shipping') {
            cost = costMatrix.shipping[origin.id]?.[destination.id]?.['20ft'] || 0;
          } else {
            cost = costMatrix[costType][origin.id]?.[destination.id]?.[familySize || 'single'] || 0;
          }
          data.push({
            origin: origin.name,
            destination: destination.name,
            cost
          });
        }
      });
    });
    
    return data.sort((a, b) => b.cost - a.cost).slice(0, 10);
  };

  const visualizationData = getVisualizationData();
  const comparisonData = getComparisonData();
  const maxValue = Math.max(...visualizationData.map(d => d.value));

  if (type === 'chart') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <span>Cost Breakdown</span>
          </CardTitle>
          <CardDescription>
            {filters.costType === 'shipping' ? 'Container sizes' : 'Family sizes'} for selected route
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {visualizationData.map((item, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-24 text-sm font-medium text-gray-700">
                  {item.label}
                </div>
                <div className="flex-1 relative">
                  <div 
                    className={`h-8 ${item.color} rounded-md flex items-center justify-end px-3 text-white font-medium shadow-sm`}
                    style={{ width: `${(item.value / maxValue) * 100}%`, minWidth: '120px' }}
                  >
                    {formatCurrency(item.value)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (type === 'comparison') {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <span>Top Routes by Cost</span>
          </CardTitle>
          <CardDescription>
            Highest cost routes across all regions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {comparisonData.slice(0, 8).map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs font-bold text-blue-600">
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {item.origin} → {item.destination}
                    </div>
                  </div>
                </div>
                <div className="font-bold text-blue-600">
                  {formatCurrency(item.cost)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Detailed view
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <DollarSign className="h-5 w-5 text-blue-600" />
          <span>Detailed Cost Analysis</span>
        </CardTitle>
        <CardDescription>
          Comprehensive cost breakdown with regional insights
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart Section */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Current Route Breakdown</h4>
            <div className="space-y-3">
              {visualizationData.map((item, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <div className="w-20 text-sm font-medium text-gray-700">
                    {item.label}
                  </div>
                  <div className="flex-1 relative">
                    <div 
                      className={`h-6 ${item.color} rounded-md flex items-center justify-end px-2 text-white text-sm font-medium`}
                      style={{ width: `${(item.value / maxValue) * 100}%`, minWidth: '100px' }}
                    >
                      {formatCurrency(item.value)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Comparison Section */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Route Comparison</h4>
            <div className="space-y-2">
              {comparisonData.slice(0, 6).map((item, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="text-sm">
                    <span className="font-medium">{item.origin}</span>
                    <span className="text-gray-500 mx-1">→</span>
                    <span className="font-medium">{item.destination}</span>
                  </div>
                  <div className="text-sm font-bold text-blue-600">
                    {formatCurrency(item.cost)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 