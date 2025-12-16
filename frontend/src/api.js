import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:6969";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function getOpenApiPaths() {
  const r = await client.get("/openapi.json");
  const paths = Object.keys(r.data.paths || {});
  return paths.sort();
}

export async function sendSampleIngest() {
  const payload = {
    timestamp: new Date().toISOString(),
    market_id: "PASAR-001",
    prices: { cabai: 15000, bawang: 9000 },
  };
  const r = await client.post("/ingest", payload);
  return r.data;
}
