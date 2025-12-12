// Minimal Leaflet map with WebSocket updates that place colored circles for markets.
// In production this would use a heatmap plugin and real geo coordinates.

const map = L.map('map').setView([-2.5, 118], 5); // center of Indonesia
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '' }).addTo(map);

// Example market locations (mock)
const markets = {
  "PASAR-001": {lat: -6.2, lon: 106.8, name: "Jakarta"},
  "PASAR-002": {lat: -6.9, lon: 107.6, name: "Bandung"},
  "PASAR-003": {lat: -7.25, lon: 112.75, name: "Surabaya"}
};

const markers = {};
for (const [id, m] of Object.entries(markets)) {
  markers[id] = L.circle([m.lat, m.lon], {radius: 50000, color: '#00f', fillOpacity: 0.2}).addTo(map).bindPopup(`${m.name} (${id})`);
}

// Connect to WS providing live price updates (example: from /ws/prices on platform)
// For simplicity, this demo doesn't connect to the main WS; you can adapt the endpoint path.
const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/alerts/ws/`); // placeholder
ws.onmessage = (ev) => {
  try {
    const msg = JSON.parse(ev.data);
    // if msg.type === 'price_update' update markers colors/size
    // For demo we'll ignore
  } catch(e) {}
};