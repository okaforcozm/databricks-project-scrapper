import React, { useState } from 'react';
import SimpleShippingTable from '@/components/SimpleShippingTable';
import ShippingRouteDetails from '@/components/ShippingRouteDetails';
import { ShippingRoute } from '@/types/shipping';

const ShippingMatrix = () => {
  const [selectedRoute, setSelectedRoute] = useState<ShippingRoute | null>(null);

  const handleViewDetails = (route: ShippingRoute) => {
    setSelectedRoute(route);
  };

  const handleBackToTable = () => {
    setSelectedRoute(null);
  };

  if (selectedRoute) {
    return (
      <ShippingRouteDetails 
        route={selectedRoute} 
        onBack={handleBackToTable} 
      />
    );
  }

  return (
    <SimpleShippingTable onViewDetails={handleViewDetails} />
  );
};

export default ShippingMatrix; 