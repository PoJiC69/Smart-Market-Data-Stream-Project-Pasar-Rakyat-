import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from "recharts";

/**
 * PriceChart
 * Expects data = [{time: ISO, cabai: 15000, bawang:9000, ...}, ...]
 */
export default function PriceChart({ data = [] }) {
  // choose colors for commodities dynamically
  const colors = ["#ff4d4f", "#2b8cff", "#ffa940", "#37b24d"];
  const keys = data.length ? Object.keys(data[data.length - 1]).filter((k) => k !== "time") : ["cabai", "bawang"];

  // normalize labels
  const normalized = data.map((d) => ({
    ...d,
    timeLabel: new Date(d.time).toLocaleTimeString()
  }));

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <LineChart data={normalized}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timeLabel" minTickGap={20} />
          <YAxis />
          <Tooltip />
          <Legend />
          {keys.map((k, i) => (
            <Line key={k} type="monotone" dataKey={k} stroke={colors[i % colors.length]} dot={false} strokeWidth={2} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}