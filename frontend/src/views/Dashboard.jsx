import React, { useEffect, useState } from "react";
import Controls from "../components/Controls";
import PriceChart from "../components/PriceChart";
import DataTable from "../components/DataTable";
import SimulationManager from "../components/SimulationManager";
import { getOpenApi } from "../api";

export default function Dashboard() {
  const [paths, setPaths] = useState([]);
  const [recent, setRecent] = useState([]); // array of ingest results
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const api = await getOpenApi();
        setPaths(Object.keys(api.paths || {}));
      } catch {
        setPaths([]);
      }
    })();
  }, []);

  // callback when new simulated/actual ingest produced
  function handleNewIngest(entry) {
    // entry: { timestamp, market_id, region, prices, sent: boolean, details?:[...] }
    setRecent((r) => [entry, ...r].slice(0, 200));
    // transform into chart points: pivot by date
    const time = new Date(entry.timestamp).toISOString();
    const point = { time };
    const prices = entry.prices || {};
    Object.entries(prices).forEach(([k, v]) => (point[k] = v));
    setChartData((c) => {
      const merged = [...c];
      merged.push(point);
      // keep last 200 and ensure sorted
      return merged.slice(-200);
    });
  }

  return (
    <div className="dashboard">
      <div className="panel-grid">
        <div className="panel card">
          <h3>Realtime Prices</h3>
          <PriceChart data={chartData} />
        </div>

        <div className="panel card">
          <h3>Simulation Controls</h3>
          <Controls />
          <SimulationManager onEmit={handleNewIngest} />
        </div>

        <div className="panel card wide">
          <h3>Recent Ingests</h3>
          <DataTable data={recent} />
        </div>

        <div className="panel card">
          <h3>API</h3>
          <p className="muted">OpenAPI paths discovered:</p>
          <ul className="paths">
            {paths.length ? paths.map((p) => <li key={p}>{p}</li>) : <li>- none -</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}