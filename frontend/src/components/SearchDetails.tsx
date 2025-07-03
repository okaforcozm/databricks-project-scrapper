
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { X, Plane, TrendingUp, DollarSign } from 'lucide-react';

interface FlightSearch {
  id: string;
  user_query: any;
  quotes?: any[];
  analytics?: any;
  screenshots?: any[];
  timestamp: string;
}

interface SearchDetailsProps {
  search: FlightSearch;
  onClose: () => void;
}

export const SearchDetails: React.FC<SearchDetailsProps> = ({ search, onClose }) => {
  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Plane className="h-5 w-5" />
            <span>Search Details</span>
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} className="text-white hover:bg-white/20">
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {search.quotes && search.quotes.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <DollarSign className="h-5 w-5 mr-2 text-green-600" />
              Flight Quotes
            </h3>
            <div className="space-y-3">
              {search.quotes.map((quote, idx) => (
                <Card key={quote.id || idx} className="p-4 border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-blue-50 rounded-lg">
                        <Plane className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <div className="font-medium">{quote.carriers?.join(', ') || 'Unknown Airline'}</div>
                        <div className="text-sm text-gray-600">
                          {quote.origin} → {quote.destination}
                        </div>
                        <div className="text-sm text-gray-500">
                          {quote.stops === 0 ? 'Direct' : `${quote.stops} stop${quote.stops > 1 ? 's' : ''}`}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        £{quote.price?.toFixed(2) || 'N/A'}
                      </div>
                      <Badge variant="secondary">Quote {idx + 1}</Badge>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <strong>Departure:</strong> {new Date(quote.departure).toLocaleString()}
                    </div>
                    <div>
                      <strong>Arrival:</strong> {new Date(quote.arrival).toLocaleString()}
                    </div>
                  </div>
                  {quote.deep_link && (
                    <div className="mt-3">
                      <a 
                        href={quote.deep_link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm underline"
                      >
                        View on Kiwi.com
                      </a>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {search.analytics && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
              Analytics
            </h3>
            <Card className="p-4 bg-gray-50">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-auto">
                {JSON.stringify(search.analytics, null, 2)}
              </pre>
            </Card>
          </div>
        )}
      </CardContent>
    </Card>
  );
};