import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Camera, AlertTriangle, CheckCircle, TrendingDown } from 'lucide-react';

interface FlightComparison {
  id: string;
  user_query: {
    origin: string;
    destination: string;
    num_adults: number;
    num_children: number;
    num_infants: number;
    flight_class: string;
    departure_date: string;
    client_quoted_price: number;
    baggage_allowance: string;
  };
  external_quotes?: any[];
  discrepancies?: any[];
  analytics?: any;
  screenshots?: any[];
  timestamp: string;
}

interface RecentSearchesProps {
  searches: FlightComparison[];
  onViewDetails: (search: FlightComparison) => void;
  onViewScreenshots: (search: FlightComparison) => void;
}

export const RecentSearches: React.FC<RecentSearchesProps> = ({ 
  searches, 
  onViewDetails, 
  onViewScreenshots 
}) => {
  if (!searches || searches.length === 0) {
    return (
      <Card className="border-0 shadow-lg">
        <CardContent className="p-8 text-center">
          <div className="text-gray-500 mb-4">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium mb-2">No comparisons yet</h3>
            <p className="text-sm">Start by entering a flight search above to check for price discrepancies.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="bg-gradient-to-r from-gray-700 to-gray-800 text-white rounded-t-lg">
        <CardTitle className="flex items-center space-x-2">
          <TrendingDown className="h-5 w-5" />
          <span>Recent Price Comparisons ({searches.length})</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {searches.map((search) => {
            const hasDiscrepancies = search.discrepancies && search.discrepancies.length > 0;
            const totalSources = search.external_quotes?.length || 0;
            const discrepancyCount = search.discrepancies?.length || 0;
            const maxSavings = hasDiscrepancies 
              ? Math.max(...search.discrepancies!.map(d => search.user_query.client_quoted_price - d.price))
              : 0;

            return (
              <Card key={search.id} className={`p-4 ${hasDiscrepancies ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'} hover:shadow-md transition-shadow`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className={`p-2 rounded-lg ${hasDiscrepancies ? 'bg-red-100' : 'bg-green-100'}`}>
                        {hasDiscrepancies ? (
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">
                          {search.user_query.origin} → {search.user_query.destination}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {new Date(search.user_query.departure_date).toLocaleDateString()} • 
                          {search.user_query.num_adults + search.user_query.num_children + search.user_query.num_infants} passenger{(search.user_query.num_adults + search.user_query.num_children + search.user_query.num_infants) > 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                      <div>
                        <span className="text-gray-500">Client Quote:</span>
                        <div className="font-semibold">£{search.user_query.client_quoted_price.toFixed(2)}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Sources Checked:</span>
                        <div className="font-semibold">{totalSources}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Class:</span>
                        <div className="font-semibold">{search.user_query.flight_class}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Baggage:</span>
                        <div className="font-semibold text-xs">{search.user_query.baggage_allowance || 'N/A'}</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {hasDiscrepancies ? (
                        <Badge variant="destructive">
                          {discrepancyCount} Lower Price{discrepancyCount > 1 ? 's' : ''} Found
                        </Badge>
                      ) : (
                        <Badge variant="default" className="bg-green-600">
                          Competitive Pricing
                        </Badge>
                      )}
                      
                      {hasDiscrepancies && (
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          Max Savings: £{maxSavings.toFixed(2)}
                        </Badge>
                      )}
                      
                      <Badge variant="outline">
                        {new Date(search.timestamp).toLocaleDateString()}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onViewDetails(search)}
                    className="flex items-center space-x-1"
                  >
                    <Eye className="h-3 w-3" />
                    <span>View Details</span>
                  </Button>
                  
                  {search.screenshots && search.screenshots.length > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewScreenshots(search)}
                      className="flex items-center space-x-1"
                    >
                      <Camera className="h-3 w-3" />
                      <span>Screenshots ({search.screenshots.length})</span>
                    </Button>
                  )}
                </div>

                {hasDiscrepancies && (
                  <div className="mt-3 p-3 bg-red-100 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-2 text-red-700 text-sm">
                      <AlertTriangle className="h-4 w-4" />
                      <span className="font-medium">
                        Action needed: {discrepancyCount} external source{discrepancyCount > 1 ? 's' : ''} found lower prices
                      </span>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
