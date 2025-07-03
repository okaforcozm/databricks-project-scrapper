/**
 * Script to generate static flight data from centralized_flight_data.json
 * This processes the real data once and creates optimized static files
 */

import fs from 'fs';
import path from 'path';
import { processFlightDataToMatrix, convertToLegacyFormat } from '../utils/flight-data-processor';

interface FlightDataSet {
  aggregation_timestamp: string;
  total_quotes: number;
  data_sources: any;
  statistics: any;
  flight_quotes: any[];
}

async function generateStaticFlightData() {
  try {
    console.log('🔄 Loading centralized flight data...');
    
    // Read the centralized flight data
    const dataPath = path.join(process.cwd(), 'public', 'centralized_flight_data.json');
    const rawData = fs.readFileSync(dataPath, 'utf8');
    const flightData: FlightDataSet = JSON.parse(rawData);
    
    console.log(`📊 Processing ${flightData.total_quotes} flight quotes...`);
    
    // Process the data
    const processedMatrix = processFlightDataToMatrix(flightData);
    const legacyMatrix = convertToLegacyFormat(processedMatrix);
    
    // Generate output
    const output = {
      generated_at: new Date().toISOString(),
      source_data: {
        total_quotes: flightData.total_quotes,
        aggregation_timestamp: flightData.aggregation_timestamp
      },
      processed_matrix: processedMatrix,
      legacy_matrix: legacyMatrix,
      statistics: {
        route_combinations: Object.keys(processedMatrix).length,
        total_routes: Object.values(processedMatrix).reduce((sum, origins) => 
          sum + Object.values(origins).reduce((subSum, destinations) => 
            subSum + Object.keys(destinations).length, 0), 0),
        regions_covered: Array.from(new Set([
          ...Object.keys(processedMatrix),
          ...Object.values(processedMatrix).flatMap(origins => Object.keys(origins))
        ])),
        passenger_types_covered: Array.from(new Set(
          Object.values(processedMatrix).flatMap(origins =>
            Object.values(origins).flatMap(destinations =>
              Object.keys(destinations)
            )
          )
        ))
      }
    };
    
    // Save processed data
    const outputPath = path.join(process.cwd(), 'public', 'processed_flight_data.json');
    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    
    console.log('✅ Static flight data generated successfully!');
    console.log(`📁 Output saved to: ${outputPath}`);
    console.log(`📈 Statistics:`);
    console.log(`   - Route combinations: ${output.statistics.route_combinations}`);
    console.log(`   - Total routes: ${output.statistics.total_routes}`);
    console.log(`   - Regions: ${output.statistics.regions_covered.join(', ')}`);
    console.log(`   - Passenger types: ${output.statistics.passenger_types_covered.join(', ')}`);
    
    // Generate a summary report
    console.log('\n📋 Sample Data Preview:');
    Object.entries(processedMatrix).slice(0, 2).forEach(([origin, destinations]) => {
      Object.entries(destinations).slice(0, 2).forEach(([dest, passengerTypes]) => {
        Object.entries(passengerTypes).slice(0, 1).forEach(([passengerType, data]) => {
          console.log(`   ${origin} → ${dest} (${passengerType}): $${data.averagePriceUSD} (${data.sampleCount} samples, ${data.evidence.length} evidence)`);
        });
      });
    });
    
  } catch (error) {
    console.error('❌ Error generating static flight data:', error);
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  generateStaticFlightData();
}

export { generateStaticFlightData }; 