
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X, Camera, Image } from 'lucide-react';

interface FlightSearch {
  id: string;
  user_query: any;
  quotes?: any[];
  external_quotes?: any[];
  analytics?: any;
  screenshots?: any[];
  timestamp: string;
}

interface ScreenshotGalleryProps {
  search: FlightSearch;
  onClose: () => void;
}

export const ScreenshotGallery: React.FC<ScreenshotGalleryProps> = ({ search, onClose }) => {
  const screenshots = search.screenshots || [];
  const quotes = search.external_quotes || search.quotes || [];

  // Helper function to find the quote associated with a screenshot
  const getQuoteForScreenshot = (quoteId: string) => {
    return quotes.find(quote => quote.id === quoteId);
  };

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Camera className="h-5 w-5" />
            <span>Evidence: Screenshots ({screenshots.length})</span>
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} className="text-white hover:bg-white/20">
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {screenshots.length === 0 ? (
          <div className="text-center py-8">
            <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No screenshots available</h3>
            <p className="text-gray-500">No screenshots were captured for this search.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {screenshots.map((screenshot, idx) => {
              const associatedQuote = getQuoteForScreenshot(screenshot.quote_id);
              const hasError = !screenshot.screenshot_url || (screenshot.error && screenshot.error !== null);
              
              return (
                <Card key={idx} className="overflow-hidden border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="aspect-video bg-gray-100 flex items-center justify-center relative">
                    {hasError ? (
                      <div className="flex flex-col items-center justify-center h-full text-red-400">
                        <div className="w-12 h-12 mb-2">
                          <svg fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                          </svg>
                        </div>
                        <span className="text-sm text-center px-2">Screenshot failed</span>
                      </div>
                    ) : (
                      <img
                        src={screenshot.screenshot_url}
                        alt={`Flight screenshot for quote ${screenshot.quote_id}`}
                        className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform"
                        onClick={() => window.open(screenshot.screenshot_url, '_blank')}
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                          target.parentElement!.innerHTML = `
                            <div class="flex flex-col items-center justify-center h-full text-gray-400">
                              <div class="w-12 h-12 mb-2">
                                <svg fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17l2.5-3.15L14 17H9z"/>
                                </svg>
                              </div>
                              <span class="text-sm">Image not available</span>
                            </div>
                          `;
                        }}
                      />
                    )}
                  </div>
                  <div className="p-3">
                    {associatedQuote ? (
                      <>
                        <p className="text-sm font-medium text-gray-900">
                          {associatedQuote.airline} • ${associatedQuote.price}
                        </p>
                        <p className="text-xs text-gray-600">
                          {associatedQuote.source} • {new Date(associatedQuote.departure).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          {associatedQuote.stops === 0 ? 'Direct flight' : `${associatedQuote.stops} stop${associatedQuote.stops > 1 ? 's' : ''}`}
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="text-sm font-medium text-gray-900">Flight Evidence {idx + 1}</p>
                        <p className="text-xs text-gray-500">Quote ID: {screenshot.quote_id}</p>
                      </>
                    )}
                    {hasError && (
                      <p className="text-xs text-red-500 mt-1">Error: {screenshot.error}</p>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
