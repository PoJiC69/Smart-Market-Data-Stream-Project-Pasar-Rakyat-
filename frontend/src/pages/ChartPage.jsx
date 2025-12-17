import React, { useEffect, useRef, useState } from "react";
import ControlsBar from "../shared/ControlsBar";
import RecentTable from "../shared/RecentTable";
import { sendIngest, getOpenApi } from "../api";

/**
 * Safe ChartPage
 * - dynamic-imports ForexChart (so missing native module won't crash app)
 * - shows clear error message if load/init fails
 * - provides TinyLineChart fallback (pure React/SVG) so UI remains usable
 */

function TinyLineChart({ data = [], height = 360 }) {
  if (!data.length) {
    return <div style={{ height, display: "flex", alignItems: "center", justifyContent: "center", color: "#666" }}>No data yet</div>;
  }
  const width = 900;
  const h = height;
  const pad = 28;
  const times = data.map((d) => new Date(d.time).getTime());
  const minX = Math.min(...times);
  const maxX = Math.max(...times) || minX + 1;
  const scaleX = (t) => pad + ((t - minX) / (maxX - minX || 1)) * (width - pad * 2);

  const keys = Object.keys(data[data.length - 1] || {}).filter((k) => k !== "time");
  let minY = Infinity, maxY = -Infinity;
  for (const d of data) for (const k of keys) { const v = Number(d[k] || 0); if (v < minY) minY = v; if (v > maxY) maxY = v; }
  if (!isFinite(minY)) { minY = 0; maxY = 1; }
  const yPad = Math.max(1, (maxY - minY) * 0.1);
  minY -= yPad; maxY += yPad;
  const scaleY = (v) => h - pad - ((v - minY) / (maxY - minY || 1)) * (h - pad * 2);

  const COLORS = ["#ff4d4f", "#2b8cff", "#ffa940", "#37b24d"];
  const seriesKeys = keys.slice(0, 4);
  const paths = seriesKeys.map((k) => {
    const pts = data.map((d) => `${scaleX(new Date(d.time).getTime())},${scaleY(Number(d[k] || 0))}`);
    return `M ${pts.join(" L ")}`;
  });

  return (
    <svg viewBox={`0 0 ${width} ${h}`} style={{ width: "100%", height: h }}>
      <rect x="0" y="0" width={width} height={h} fill="#fff" rx="8" />
      {[0,0.25,0.5,0.75,1].map((t,i)=>(
        <line key={i} x1={pad} x2={width-pad} y1={pad+t*(h-pad*2)} y2={pad+t*(h-pad*2)} stroke="#f1f5f9" strokeWidth="1" />
      ))}
      {paths.map((p,i)=> <path key={i} d={p} fill="none" stroke={COLORS[i%COLORS.length]} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />)}
      <g transform={`translate(${pad},12)`}>
        {seriesKeys.map((k,i)=>(
          <g key={k} transform={`translate(${i*110},0)`}>
            <rect width="10" height="10" fill={COLORS[i%COLORS.length]} rx="2" />
            <text x="16" y="10" fontSize="12" fill="#111">{k}</text>
          </g>
        ))}
      </g>
    </svg>
  );
}

export default function ChartPage() {
  const forexRef = useRef(null);
  const [ForexComp, setForexComp] = useState(null);
  const [loadError, setLoadError] = useState(null);

  const [running, setRunning] = useState(false);
  const [deviceCount, setDeviceCount] = useState(() => Number(localStorage.getItem("sim.devices") || 5));
  const [intervalMs, setIntervalMs] = useState(() => Number(localStorage.getItem("sim.interval") || 2000));
  const [useBackend, setUseBackend] = useState(() => localStorage.getItem("sim.backend") === "true");
  const [recent, setRecent] = useState([]);
  const [series, setSeries] = useState([]);
  const [paths, setPaths] = useState([]);
  const [chartSymbol, setChartSymbol] = useState("cabai");

  useEffect(() => {
    // dynamic import ForexChart to avoid top-level import crash
    let mounted = true;
    (async () => {
      try {
        const mod = await import("../shared/ForexChart");
        if (mounted) setForexComp(() => mod.default);
      } catch (e) {
        console.error("Failed to load ForexChart:", e);
        if (mounted) setLoadError(String(e || "Unknown error while loading chart module"));
      }
    })();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const api = await getOpenApi();
        setPaths(Object.keys(api.paths || {}));
      } catch { setPaths([]); }
    })();
  }, []);

  useEffect(() => {
    localStorage.setItem("sim.devices", String(deviceCount));
    localStorage.setItem("sim.interval", String(intervalMs));
    localStorage.setItem("sim.backend", String(useBackend));
  }, [deviceCount, intervalMs, useBackend]);

  useEffect(() => {
    let timer = null;
    if (running) {
      timer = setInterval(() => {
        for (let i = 1; i <= deviceCount; i++) emitOne(i);
      }, Math.max(200, intervalMs));
    }
    return () => timer && clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, deviceCount, intervalMs, useBackend, chartSymbol]);

  function randomPrices() {
    const commodities = ["cabai", "bawang", "tomat", "kentang"];
    const base = { cabai: 15000, bawang: 9000, tomat: 7000, kentang: 5000 };
    const p = {};
    commodities.forEach((c) => { const variance = Math.round(base[c] * (Math.random() * 0.15 - 0.05)); p[c] = base[c] + variance; });
    return p;
  }
  function makePayload(deviceId) { return { timestamp: new Date().toISOString(), market_id: `PASAR-${String(deviceId).padStart(3,"0")}`, region: "JAKARTA", prices: randomPrices() }; }
  function pivotDetailsToPrices(details) { if (!Array.isArray(details)) return null; const prices = {}; for (const d of details) { const key = d.commodity ?? d.commodity_name ?? d.item ?? "unknown"; const val = d.price ?? d.value ?? null; if (key && val != null) prices[key] = val; } return prices; }

  async function emitOne(deviceId) {
    const payload = makePayload(deviceId);
    const entry = { ...payload, sent: false, created_at: new Date().toISOString() };
    if (useBackend) {
      try {
        const res = await sendIngest(payload);
        entry.sent = true;
        if (res && Array.isArray(res.details) && res.details.length) { entry.prices = pivotDetailsToPrices(res.details) || payload.prices; entry.details = res.details; }
        else entry.prices = payload.prices;
      } catch { entry.sent = false; entry.prices = payload.prices; }
    } else { entry.sent = true; entry.prices = payload.prices; }

    pushEntry(entry);
  }

  function pushEntry(entry) {
    setRecent((r) => [entry, ...r].slice(0, 200));
    const price = entry.prices && entry.prices[chartSymbol];
    // update series used by TinyLineChart
    const point = { time: entry.timestamp || entry.created_at, [chartSymbol]: price };
    setSeries((s) => [...s, point].slice(-500));
    // if Forex component loaded, send tick
    if (ForexComp && forexRef.current && typeof forexRef.current.addTick === "function" && price != null) {
      forexRef.current.addTick({ time: entry.timestamp || entry.created_at, price: Number(price), volume: 1 });
    }
  }

  function emitSample() { emitOne(1); }
  function startSim() { setRunning(true); }
  function stopSim() { setRunning(false); }

  return (
    <div className="chart-page">
      <header className="topbar">
        <div className="brand">
          <h1>Smart Market — Candlestick (Safe Mode)</h1>
          <p className="muted">Jika library chart gagal dimuat, akan tampil fallback dan pesan error di bawah.</p>
        </div>
      </header>

      <div className="container">
        <div className="left">
          <div className="card">
            <ControlsBar deviceCount={deviceCount} setDeviceCount={setDeviceCount} intervalMs={intervalMs} setIntervalMs={setIntervalMs} useBackend={useBackend} setUseBackend={setUseBackend} running={running} onStart={startSim} onStop={stopSim} onEmitSample={emitSample} />
            <label style={{ marginTop: 12 }}>Chart commodity:
              <select value={chartSymbol} onChange={(e) => setChartSymbol(e.target.value)} style={{ marginLeft: 8 }}>
                <option value="cabai">cabai</option>
                <option value="bawang">bawang</option>
                <option value="tomat">tomat</option>
                <option value="kentang">kentang</option>
              </select>
            </label>
          </div>

          <div className="card"><h3>Recent Ingests</h3><RecentTable data={recent} /></div>
        </div>

        <div className="right">
          <div className="card chart-card">
            <div className="chart-header"><div><h3>Candlestick — {chartSymbol.toUpperCase()}</h3><p className="muted">Safe loader + fallback</p></div></div>

            {/* If Forex component loaded, render it; otherwise fallback to TinyLineChart */}
            {ForexComp ? (
              <React.Suspense fallback={<div style={{height:360}}>Loading chart...</div>}>
                <ForexComp ref={forexRef} symbol={chartSymbol} timeframeMs={60_000} />
              </React.Suspense>
            ) : (
              <>
                <div style={{ marginBottom: 8 }}>
                  {loadError ? (<div style={{ padding: 8, background: "#fff4f4", color: "#7f1d1d", borderRadius: 6 }}><strong>Chart load error:</strong><div style={{ whiteSpace: "pre-wrap" }}>{loadError}</div></div>) : (<div style={{ color: "#666" }}>Advanced chart not yet loaded — showing lightweight preview</div>)}
                </div>
                <TinyLineChart data={series} height={360} />
              </>
            )}
          </div>

          <div className="card"><h3>API</h3><p className="muted">OpenAPI endpoints:</p><ul className="paths">{paths.length ? paths.map((p) => <li key={p}>{p}</li>) : <li>- none -</li>}</ul></div>
        </div>
      </div>
    </div>
  );
}