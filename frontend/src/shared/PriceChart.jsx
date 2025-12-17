import React from "react";

/**
 * TinyLineChart - lightweight SVG line chart for quick preview
 * Props: data = [{ time: ISO, cabai: number, bawang: number, ... }, ...]
 * Renders up to 200 points, auto-scales.
 */
export default function TinyLineChart({ data = [] }) {
  const width = 900;
  const height = 320;
  if (!data || data.length === 0) {
    return (
      <div style={{ width, height, display: "flex", alignItems: "center", justifyContent: "center", color: "#666" }}>
        No data yet
      </div>
    );
  }

  // determine keys (commodities)
  const last = data[data.length - 1];
  const keys = Object.keys(last).filter((k) => k !== "time" && k !== "timeLabel");
  // build points for first two keys max
  const seriesKeys = keys.slice(0, 4);

  // prepare x/y scale
  const times = data.map((d) => new Date(d.time).getTime());
  const xs = times;
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs) || minX + 1;
  const pad = 24;
  const scaleX = (t) => pad + ((t - minX) / (maxX - minX || 1)) * (width - pad * 2);

  // compute Y min/max across chosen keys
  let minY = Infinity;
  let maxY = -Infinity;
  for (const d of data) {
    for (const k of seriesKeys) {
      const v = Number(d[k] ?? 0);
      if (Number.isFinite(v)) {
        if (v < minY) minY = v;
        if (v > maxY) maxY = v;
      }
    }
  }
  if (!isFinite(minY)) {
    minY = 0;
    maxY = 1;
  }
  // add padding
  const yPad = Math.max(1, (maxY - minY) * 0.1);
  minY -= yPad;
  maxY += yPad;
  const scaleY = (v) => height - pad - ((v - minY) / (maxY - minY || 1)) * (height - pad * 2);

  // colors
  const COLORS = ["#ff4d4f", "#2b8cff", "#ffa940", "#37b24d"];

  const paths = seriesKeys.map((k) => {
    const pts = data.map((d) => {
      const x = scaleX(new Date(d.time).getTime());
      const y = scaleY(Number(d[k] ?? 0));
      return `${x},${y}`;
    });
    return `M ${pts.join(" L ")}`;
  });

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height }}>
      {/* background */}
      <rect x="0" y="0" width={width} height={height} fill="#fff" rx="8" />
      {/* grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((t, i) => (
        <line key={i} x1={pad} x2={width - pad} y1={pad + t * (height - pad * 2)} y2={pad + t * (height - pad * 2)} stroke="#f1f5f9" strokeWidth="1" />
      ))}
      {/* series paths */}
      {paths.map((p, i) => (
        <path key={i} d={p} fill="none" stroke={COLORS[i % COLORS.length]} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      ))}
      {/* legend */}
      <g transform={`translate(${pad},${8})`}>
        {seriesKeys.map((k, i) => (
          <g key={k} transform={`translate(${i * 110},0)`}>
            <rect width="10" height="10" fill={COLORS[i % COLORS.length]} rx="2" />
            <text x="16" y="10" fontSize="12" fill="#111">{k}</text>
          </g>
        ))}
      </g>
    </svg>
  );
}