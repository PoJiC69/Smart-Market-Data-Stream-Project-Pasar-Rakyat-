import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:6969";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 8000,
  headers: { "Content-Type": "application/json" }
});

/**
 * sendIngest(payload)
 * - payload expected { timestamp, market_id, region?, prices: {commodity: value, ...} }
 * Returns axios response data
 */
export async function sendIngest(payload) {
  const res = await client.post("/ingest", payload);
  return res.data;
}

export async function getOpenApi() {
  const res = await client.get("/openapi.json");
  return res.data;
}