import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, TrendingDown, ExternalLink, CheckCircle } from 'lucide-react';

interface Quote {
  id: string;
  source: string;
  price: number;
  url: string;
  airline: string;
  departure: string;
  arrival: string;
  stops: number;
  baggage: string;
}

interface FlightResultsProps {
  quotes: Quote[];
  isLoading: boolean;
  clientQuotedPrice?: number;
}

export const FlightResults: React.FC<FlightResultsProps> = ({ quotes, isLoading, clientQuotedPrice }) => {
  if (isLoading) {
    return (
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-t-lg">
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 animate-pulse" />
            <span>Checking for price discrepancies...</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Comparing prices across multiple sources...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!quotes || quotes.length === 0) {
    return null;
  }

  const discrepancies = quotes.filter(quote => clientQuotedPrice && quote.price < clientQuotedPrice);
  const hasDiscrepancies = discrepancies.length > 0;

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className={`text-white rounded-t-lg ${hasDiscrepancies ? 'bg-gradient-to-r from-red-600 to-red-700' : 'bg-gradient-to-r from-green-600 to-emerald-600'}`}>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {hasDiscrepancies ? (
              <>
                <AlertTriangle className="h-5 w-5" />
                <span>Price Discrepancies Found ({discrepancies.length} lower prices)</span>
              </>
            ) : (
              <>
                <CheckCircle className="h-5 w-5" />
                <span>No Discrepancies Found - Competitive Pricing</span>
              </>
            )}
          </div>
          <div className="text-right">
            <div className="text-xs opacity-75">Client Quote</div>
            <div className="text-lg font-bold">£{clientQuotedPrice?.toFixed(2) || '0.00'}</div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {quotes.map((quote, idx) => {
            const isDiscrepancy = clientQuotedPrice && quote.price < clientQuotedPrice;
            const savings = clientQuotedPrice ? clientQuotedPrice - quote.price : 0;
            const savingsPercentage = clientQuotedPrice ? ((savings / clientQuotedPrice) * 100) : 0;

            return (
              <Card key={quote.id} className={`p-4 transition-shadow ${isDiscrepancy ? 'border-red-300 bg-red-50 hover:shadow-md' : 'border-gray-200 hover:shadow-sm'}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${isDiscrepancy ? 'bg-red-100' : 'bg-blue-50'}`}>
                      {isDiscrepancy ? (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                      ) : (
                        <CheckCircle className="h-4 w-4 text-blue-600" />
                      )}
                    </div>
                    <div>
                      <div className="font-medium text-lg">{quote.airline}</div>
                      <div className="text-sm text-gray-600">
                        via {quote.source}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${isDiscrepancy ? 'text-red-600' : 'text-gray-900'}`}>
                      £{quote.price.toFixed(2)}
                    </div>
                    {isDiscrepancy && (
                      <Badge variant="destructive" className="mt-1">
                        -{savingsPercentage.toFixed(1)}% (Save £{savings.toFixed(2)})
                      </Badge>
                    )}
                    <Badge variant={quote.stops === 0 ? "default" : "secondary"} className="mt-1 ml-2">
                      {quote.stops === 0 ? 'Direct' : `${quote.stops} stop${quote.stops > 1 ? 's' : ''}`}
                    </Badge>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                  <div>
                    <strong>Departure:</strong> {new Date(quote.departure).toLocaleString()}
                  </div>
                  <div>
                    <strong>Arrival:</strong> {new Date(quote.arrival).toLocaleString()}
                  </div>
                  <div>
                    <strong>Baggage:</strong> {quote.baggage}
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    {isDiscrepancy ? (
                      <span className="text-red-600 font-medium">⚠️ Lower price found</span>
                    ) : (
                      <span className="text-green-600">✅ Competitive price</span>
                    )}
                  </div>
                  <a 
                    href={quote.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className={`inline-flex items-center space-x-2 text-sm underline ${isDiscrepancy ? 'text-red-600 hover:text-red-800' : 'text-blue-600 hover:text-blue-800'}`}
                  >
                    <span>View on {quote.source}</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </Card>
            );
          })}
        </div>

        {hasDiscrepancies && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-800">Action Required</h4>
                <p className="text-red-700 text-sm mt-1">
                  {discrepancies.length} external source{discrepancies.length > 1 ? 's' : ''} found lower prices. 
                  Consider adjusting your pricing strategy or investigating the difference in service offerings.
                </p>
                <div className="mt-2 text-xs text-red-600">
                  Maximum potential savings: £{Math.max(...discrepancies.map(d => clientQuotedPrice! - d.price)).toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 