import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  ExternalLink, 
  Camera,
  CheckCircle,
  Clock,
  Globe,
  Link,
  Image as ImageIcon
} from 'lucide-react';
import { DashboardFilters, EvidenceData } from '@/types/mobility';

interface EvidencePanelProps {
  evidence: EvidenceData[];
  filters: DashboardFilters;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidence,
  filters
}) => {
  const [activeEvidence, setActiveEvidence] = useState<string | null>(null);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredEvidence = evidence.filter(item => 
    item.costType === filters.costType
  );

  const getEvidenceIcon = (costType: string) => {
    switch (costType) {
      case 'flights': return '✈️';
      case 'accommodation': return '🏠';
      case 'shipping': return '📦';
      default: return '📄';
    }
  };

  const getSourceBadgeColor = (source: string) => {
    switch (source.toLowerCase()) {
      case 'expedia': return 'bg-blue-100 text-blue-800';
      case 'alto vita': return 'bg-green-100 text-green-800';
      case 'silverdoor': return 'bg-purple-100 text-purple-800';
      case 'freightos': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderEvidenceCard = (item: EvidenceData) => (
    <Card 
      key={item.id} 
      className={`cursor-pointer transition-all hover:shadow-md ${
        activeEvidence === item.id ? 'ring-2 ring-blue-500' : ''
      }`}
      onClick={() => setActiveEvidence(activeEvidence === item.id ? null : item.id)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">
              {getEvidenceIcon(item.costType)}
            </div>
            <div>
              <CardTitle className="text-lg">{item.source}</CardTitle>
              <CardDescription className="flex items-center space-x-2">
                <Clock className="h-4 w-4" />
                <span>{formatDate(item.timestamp)}</span>
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {item.verified && (
              <CheckCircle className="h-5 w-5 text-green-500" />
            )}
            <Badge className={getSourceBadgeColor(item.source)}>
              {item.source}
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      {activeEvidence === item.id && (
        <CardContent className="pt-0">
          <div className="space-y-4">
            {/* Extracted Data */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Extracted Data</h4>
              <div className="bg-gray-50 p-3 rounded-lg">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(item.extractedData, null, 2)}
                </pre>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-3">
              {item.url && (
                <Button variant="outline" size="sm" asChild>
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View Source
                  </a>
                </Button>
              )}
              
              {item.screenshot && (
                <Button variant="outline" size="sm">
                  <ImageIcon className="h-4 w-4 mr-2" />
                  View Screenshot
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );

  const renderDataSources = () => {
    const sources = {
      flights: [
        { name: 'Expedia', url: 'https://expedia.com', description: 'Global flight booking platform' },
        { name: 'Kayak', url: 'https://kayak.com', description: 'Flight comparison engine' },
        { name: 'Google Flights', url: 'https://flights.google.com', description: 'Google travel search' }
      ],
      accommodation: [
        { name: 'Alto Vita', url: 'https://altovita.com', description: 'Corporate housing platform' },
        { name: 'Silverdoor', url: 'https://silverdoor.com', description: 'Serviced apartment provider' },
        { name: 'BridgeStreet', url: 'https://bridgestreet.com', description: 'Extended stay accommodations' }
      ],
      shipping: [
        { name: 'Freightos', url: 'https://freightos.com', description: 'Global freight marketplace' },
        { name: 'SeaRates', url: 'https://searates.com', description: 'International shipping calculator' },
        { name: 'iContainers', url: 'https://icontainers.com', description: 'Container shipping quotes' }
      ]
    };

    const currentSources = sources[filters.costType] || [];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {currentSources.map((source, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{source.name}</CardTitle>
                  <CardDescription>{source.description}</CardDescription>
                </div>
                <Globe className="h-5 w-5 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <Button variant="outline" size="sm" asChild className="w-full">
                <a href={source.url} target="_blank" rel="noopener noreferrer">
                  <Link className="h-4 w-4 mr-2" />
                  Visit Source
                </a>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>Evidence & Data Sources</span>
          </CardTitle>
          <CardDescription>
            Data verification and source tracking for {filters.costType} cost information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="evidence" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="evidence">
                <Camera className="h-4 w-4 mr-2" />
                Evidence ({filteredEvidence.length})
              </TabsTrigger>
              <TabsTrigger value="sources">
                <Globe className="h-4 w-4 mr-2" />
                Data Sources
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="evidence" className="space-y-4 mt-6">
              {filteredEvidence.length > 0 ? (
                <div className="space-y-4">
                  {filteredEvidence.map(renderEvidenceCard)}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No Evidence Available
                  </h3>
                  <p className="text-gray-500">
                    No evidence data found for {filters.costType} in the current selection.
                  </p>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="sources" className="mt-6">
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {filters.costType === 'flights' ? 'Flight Booking Platforms' :
                     filters.costType === 'accommodation' ? 'Accommodation Providers' :
                     'Shipping & Freight Services'}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Primary data sources for {filters.costType} cost information
                  </p>
                </div>
                {renderDataSources()}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Data Collection Notes */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Data Collection Notes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>All cost data is converted to USD using 30-day average exchange rates</span>
            </div>
            <div className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>Peak costs represent potential highest expenses during peak travel seasons</span>
            </div>
            <div className="flex items-start space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
              <span>Data is updated regularly from verified sources and partner APIs</span>
            </div>
            <div className="flex items-start space-x-2">
              <Clock className="h-4 w-4 text-blue-500 mt-0.5" />
              <span>Evidence collection includes screenshots and API responses for audit trails</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 