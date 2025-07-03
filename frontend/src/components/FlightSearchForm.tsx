import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Search, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

const CITIES = [
  "London",
  "Milan",
  "Lisbon",
  "Paris",
  "New York",
  "Tokyo",
  "Los Angeles",
  "Chicago",
  "San Francisco",
  "Dubai",
  "Singapore",
  "Madrid",
  "Rome",
  "Barcelona",
  "Berlin",
  "Amsterdam",
  "Moscow",
  "Hong Kong",
  "Bangkok",
  "Sydney",
  "Toronto",
  "Vancouver",
  "Mexico City",
  "São Paulo",
  "Delhi",
  "Mumbai",
  "Istanbul",
  "Seoul",
  "Zurich",
  "Vienna"
]

const FLIGHT_CLASSES = [
  { value: 'M', label: 'Economy' },
  { value: 'W', label: 'Premium Economy' },
  { value: 'C', label: 'Business' },
  { value: 'F', label: 'First' }
];

const BAGGAGE_OPTIONS = [
  '20kg included',
  '23kg included', 
  '25kg included',
  '30kg included',
  'Hand luggage only',
  'Extra baggage fees apply'
];

interface FlightSearchFormProps {
  onSearch: (data: any) => void;
}

export const FlightSearchForm: React.FC<FlightSearchFormProps> = ({ onSearch }) => {
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    flight_class: '',
    num_adults: 1,
    num_children: 0,
    num_infants: 0,
    departure_date: undefined as Date | undefined,
    client_quoted_price: 0,
    baggage_allowance: ''
  });
  const [isSearching, setIsSearching] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.origin || !formData.destination || !formData.departure_date || !formData.client_quoted_price) {
      return;
    }

    setIsSearching(true);
    try {
      await onSearch({
        ...formData,
        departure_date: formData.departure_date ? format(formData.departure_date, 'yyyy-MM-dd') : ''
      });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Card className="bg-white shadow-lg border-0">
      <CardHeader className="bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-t-lg">
        <CardTitle className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5" />
          <span>Flight Price Comparison</span>
        </CardTitle>
        <p className="text-red-100 text-sm mt-1">
          Enter your client's quoted price to check for discrepancies with external sources
        </p>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="origin">From City</Label>
                <Select value={formData.origin} onValueChange={(value) => setFormData({...formData, origin: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select origin city" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    {CITIES.map((city) => (
                      <SelectItem key={city} value={city}>{city}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="destination">To City</Label>
                <Select value={formData.destination} onValueChange={(value) => setFormData({...formData, destination: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select destination city" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    {CITIES.map((city) => (
                      <SelectItem key={city} value={city}>{city}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="flight_class">Flight Class</Label>
                <Select value={formData.flight_class} onValueChange={(value) => setFormData({...formData, flight_class: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select class" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    {FLIGHT_CLASSES.map((cls) => (
                      <SelectItem key={cls.value} value={cls.value}>{cls.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="adults">Adults</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      type="number"
                      min="1"
                      value={formData.num_adults}
                      onChange={(e) => setFormData({...formData, num_adults: parseInt(e.target.value) || 1})}
                      className="text-center"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="children">Children</Label>
                  <Input
                    type="number"
                    min="0"
                    value={formData.num_children}
                    onChange={(e) => setFormData({...formData, num_children: parseInt(e.target.value) || 0})}
                    className="text-center"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="infants">Infants</Label>
                  <Input
                    type="number"
                    min="0"
                    value={formData.num_infants}
                    onChange={(e) => setFormData({...formData, num_infants: parseInt(e.target.value) || 0})}
                    className="text-center"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Departure Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !formData.departure_date && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {formData.departure_date ? format(formData.departure_date, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-white" align="start">
                    <Calendar
                      mode="single"
                      selected={formData.departure_date}
                      onSelect={(date) => setFormData({...formData, departure_date: date})}
                      disabled={(date) => date < new Date()}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label htmlFor="baggage_allowance">Baggage Allowance</Label>
                <Select value={formData.baggage_allowance} onValueChange={(value) => setFormData({...formData, baggage_allowance: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select baggage allowance" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    {BAGGAGE_OPTIONS.map((option) => (
                      <SelectItem key={option} value={option}>{option}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="client_quoted_price" className="text-red-600 font-medium">
                  Client's Quoted Price (£)
                </Label>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.client_quoted_price || ''}
                  onChange={(e) => setFormData({...formData, client_quoted_price: parseFloat(e.target.value) || 0})}
                  className="text-right text-lg font-semibold border-red-200 focus:border-red-500"
                  placeholder="0.00"
                />
                <p className="text-xs text-gray-500">
                  Enter the price quoted to your client for comparison
                </p>
              </div>

              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-medium text-red-800 mb-2">What we'll check:</h4>
                <ul className="text-xs text-red-700 space-y-1">
                  <li>• Skyscanner prices</li>
                  <li>• Direct airline websites</li>
                  <li>• Other travel platforms</li>
                  <li>• Real-time pricing data</li>
                </ul>
              </div>
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-medium py-3"
            disabled={isSearching || !formData.origin || !formData.destination || !formData.departure_date || !formData.client_quoted_price}
          >
            {isSearching ? 'Checking for Discrepancies...' : 'Check Price Discrepancies'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};