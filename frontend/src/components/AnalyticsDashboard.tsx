import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BarChart3, TrendingDown, Clock, Users } from 'lucide-react';

interface AnalyticsDashboardProps {
  analytics: {
    total_comparisons: number;
    total_discrepancies: number;
    avg_savings_percentage: number;
    time_saved_hours: number;
    performance_by_airline: Array<{
      name: string;
      competitive_rate: number;
      avg_discrepancy: number;
    }>;
    performance_by_route: Array<{
      route: string;
      discrepancy_rate: number;
      avg_savings: number;
    }>;
  };
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ analytics }) => {
  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Total Comparisons</p>
                <p className="text-3xl font-bold text-blue-900">{analytics.total_comparisons}</p>
              </div>
              <BarChart3 className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-50 to-red-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Discrepancies Found</p>
                <p className="text-3xl font-bold text-red-900">{analytics.total_discrepancies}</p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Avg Savings</p>
                <p className="text-3xl font-bold text-green-900">{analytics.avg_savings_percentage}%</p>
              </div>
              <TrendingDown className="h-8 w-8 text-green-600 transform rotate-180" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-600">Time Saved</p>
                <p className="text-3xl font-bold text-purple-900">{analytics.time_saved_hours}h</p>
              </div>
              <Clock className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance by Airline */}
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Performance by Airline</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            {analytics.performance_by_airline.map((airline, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{airline.name}</span>
                    <div className="flex items-center space-x-4">
                      <Badge variant={airline.competitive_rate > 70 ? "default" : airline.competitive_rate > 50 ? "secondary" : "destructive"}>
                        {airline.competitive_rate}% Competitive
                      </Badge>
                      <span className="text-sm text-gray-600">
                        Avg Discrepancy: {airline.avg_discrepancy}%
                      </span>
                    </div>
                  </div>
                  <Progress value={airline.competitive_rate} className="h-2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance by Route */}
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-t-lg">
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Performance by Route</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-4">
            {analytics.performance_by_route.map((route, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{route.route}</span>
                    <div className="flex items-center space-x-4">
                      <Badge variant={route.discrepancy_rate > 60 ? "destructive" : route.discrepancy_rate > 40 ? "secondary" : "default"}>
                        {route.discrepancy_rate}% Discrepancy Rate
                      </Badge>
                      <span className="text-sm text-green-600 font-medium">
                        Avg Savings: £{route.avg_savings.toFixed(2)}
                      </span>
                    </div>
                  </div>
                  <Progress value={route.discrepancy_rate} className="h-2" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card className="border-0 shadow-lg bg-gradient-to-r from-yellow-50 to-orange-50">
        <CardHeader>
          <CardTitle className="text-orange-800">Key Insights</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white rounded-lg border">
              <h4 className="font-semibold text-gray-900 mb-2">Most Problematic Route</h4>
              <p className="text-sm text-gray-600">
                {analytics.performance_by_route.reduce((max, route) => 
                  route.discrepancy_rate > max.discrepancy_rate ? route : max
                ).route} has the highest discrepancy rate at{' '}
                {Math.max(...analytics.performance_by_route.map(r => r.discrepancy_rate))}%
              </p>
            </div>
            <div className="p-4 bg-white rounded-lg border">
              <h4 className="font-semibold text-gray-900 mb-2">Best Performing Airline</h4>
              <p className="text-sm text-gray-600">
                {analytics.performance_by_airline.reduce((max, airline) => 
                  airline.competitive_rate > max.competitive_rate ? airline : max
                ).name} maintains the highest competitive rate at{' '}
                {Math.max(...analytics.performance_by_airline.map(a => a.competitive_rate))}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 