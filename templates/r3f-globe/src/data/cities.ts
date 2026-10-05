export type City = {
  id: string;
  name: string;
  state: string;
  lat: number;
  lon: number;
  tz: string;
  pop: string;
  line: string;
};

// Original copy. Population values are rounded city-proper estimates.
export const cities: City[] = [
  { id: 'nyc', name: 'New York', state: 'NY', lat: 40.71, lon: -74.01, tz: 'ET', pop: '8.3M', line: 'The city that never dims. Eight million lights, one skyline.' },
  { id: 'lax', name: 'Los Angeles', state: 'CA', lat: 34.05, lon: -118.24, tz: 'PT', pop: '3.9M', line: 'A basin of light between the mountains and the Pacific.' },
  { id: 'chi', name: 'Chicago', state: 'IL', lat: 41.88, lon: -87.63, tz: 'CT', pop: '2.7M', line: 'A grid of steel and lake wind, glowing in straight lines.' },
  { id: 'sfo', name: 'San Francisco', state: 'CA', lat: 37.77, lon: -122.42, tz: 'PT', pop: '0.8M', line: 'Fog on the bay, a bright peninsula at the edge of the map.' },
  { id: 'mia', name: 'Miami', state: 'FL', lat: 25.76, lon: -80.19, tz: 'ET', pop: '0.45M', line: 'A neon coastline where the continent runs out of land.' },
  { id: 'sea', name: 'Seattle', state: 'WA', lat: 47.61, lon: -122.33, tz: 'PT', pop: '0.75M', line: 'Rain-lit streets between the sound and the cascades.' },
  { id: 'hou', name: 'Houston', state: 'TX', lat: 29.76, lon: -95.37, tz: 'CT', pop: '2.3M', line: 'A vast bright sprawl across the Gulf plain.' },
  { id: 'dca', name: 'Washington', state: 'DC', lat: 38.91, lon: -77.04, tz: 'ET', pop: '0.7M', line: 'Marble, light and a river, laid out like a compass.' },
];
