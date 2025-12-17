import React, { useEffect, useImperativeHandle, useRef, useState, forwardRef } from "react";

/**
 * Pure-SVG Forex-like Candlestick Chart (no external deps)
 *
 * Usage:
 *  - <ForexChart ref={ref} timeframeMs={60000} height={420} />
 *  - ref.current.addTick({ time: ISOString, price: Number, volume?: Number })
 *
 * Features:
 *  - Aggregates ticks to candles by timeframeMs (default 1 minute)
 *  - Renders candles + volume histogram + simple axes (time & price)
 *  - Tooltip on hover shows OHLC for nearest candle
 *  - Wheel to zoom (change visible candle count)
 *
 * Notes:
 *  - Designed for realtime updates: addTick is fast and updates chart using rAF batching.
 *  - No external libraries required.
 */

function bucketStartMs(ms, tf) {
  return Math.floor(ms / tf) * tf;
}

function formatTimeLabel(iso) {
  const d = new Date(iso);
  // show hh:mm
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const COLORS = {
  up: "#16a34a",
  down: "#ef4444",
  wick: "#0f172a",
  grid: "#eef2f7",
  bg: "#ffffff"
};

const DEFAULT_VISIBLE = 50;

const ForexChart = forwardRef(function ForexChart(
  { timeframeMs = 60_000, height = 420, maxCandles = 1000, initialCandles = [] },
  ref
) {
  const containerRef = useRef(null);
  const [width, setWidth] = useState(900);
  const candlesRef = useRef([]); // array of { time(startISO), open, high, low, close, volume }
  const pendingTicksRef = useRef([]);
  const [visibleCount, setVisibleCount] = useState(DEFAULT_VISIBLE);
  const [renderStamp, setRenderStamp] = useState(0); // bump to trigger render
  const rafRef = useRef(null);
  const hoverRef = useRef({ over: false, x: 0, y: 0, index: -1 });

  // init with initialCandles if provided
  useEffect(() => {
    if (Array.isArray(initialCandles) && initialCandles.length) {
      candlesRef.current = initialCandles.map((c) => ({
        time: c.time,
        start: new Date(c.time).getTime(),
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
        volume: c.volume || 0
      })).slice(-maxCandles);
      setRenderStamp((s) => s + 1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // resize observer
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(() => {
      setWidth(el.clientWidth || 900);
    });
    obs.observe(el);
    setWidth(el.clientWidth || 900);
    return () => obs.disconnect();
  }, []);

  // batching updates from addTick
  function scheduleFlush() {
    if (rafRef.current) return;
    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null;
      const ticks = pendingTicksRef.current.splice(0);
      if (ticks.length === 0) return;
      // process ticks
      for (const t of ticks) {
        const ms = new Date(t.time).getTime();
        const start = bucketStartMs(ms, timeframeMs);
        let last = candlesRef.current.length ? candlesRef.current[candlesRef.current.length - 1] : null;
        if (!last || last.start !== start) {
          // new candle
          const newCandle = { time: new Date(start).toISOString(), start, open: t.price, high: t.price, low: t.price, close: t.price, volume: t.volume || 0 };
          // if previous exists and its open is null, set open to prev close etc.
          candlesRef.current.push(newCandle);
          // trim
          if (candlesRef.current.length > maxCandles) candlesRef.current.splice(0, candlesRef.current.length - maxCandles);
        } else {
          // update existing candle
          last.high = Math.max(last.high, t.price);
          last.low = Math.min(last.low, t.price);
          last.close = t.price;
          last.volume = (last.volume || 0) + (t.volume || 0);
        }
      }
      setRenderStamp((s) => s + 1);
    });
  }

  // exposed API
  useImperativeHandle(ref, () => ({
    addTick(tick) {
      if (!tick || typeof tick.price !== "number") return;
      // ensure time is present
      if (!tick.time) tick.time = new Date().toISOString();
      pendingTicksRef.current.push({ time: tick.time, price: Number(tick.price), volume: Number(tick.volume || 0) });
      scheduleFlush();
    },
    setCandles(candles = []) {
      candlesRef.current = (candles || []).map((c) => ({ time: c.time, start: new Date(c.time).getTime(), open: c.open, high: c.high, low: c.low, close: c.close, volume: c.volume || 0 })).slice(-maxCandles);
      setRenderStamp((s) => s + 1);
    },
    getCandles() {
      return candlesRef.current.slice();
    }
  }));

  // mouse/hover handling for tooltip
  function onMouseMove(e) {
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    hoverRef.current.over = true;
    hoverRef.current.x = x;
    hoverRef.current.y = y;
    // compute index
    const visible = getVisibleCandles();
    const candleW = innerWidth() / Math.max(1, visible.length);
    const idx = Math.floor((x - paddingLeft()) / candleW);
    hoverRef.current.index = Math.min(Math.max(0, idx), visible.length - 1);
    setRenderStamp((s) => s + 1); // trigger render for tooltip
  }
  function onMouseLeave() {
    hoverRef.current.over = false;
    hoverRef.current.index = -1;
    setRenderStamp((s) => s + 1);
  }

  // wheel to zoom
  function onWheel(e) {
    if (e.deltaY > 0) setVisibleCount((v) => Math.min(200, Math.max(8, Math.floor(v * 0.9))));
    else setVisibleCount((v) => Math.min(200, Math.max(8, Math.floor(v * 1.1))));
  }

  function innerWidth() {
    return Math.max(200, width - 120); // leave left axis & margin
  }
  function paddingLeft() {
    return 80;
  }
  function paddingBottom() {
    return 28;
  }

  function getVisibleCandles() {
    const all = candlesRef.current;
    if (!all.length) return [];
    return all.slice(-visibleCount);
  }

  // rendering helpers
  const visible = getVisibleCandles();
  const prices = visible.flatMap((c) => [c.high, c.low]);
  const maxPrice = prices.length ? Math.max(...prices) : 1;
  const minPrice = prices.length ? Math.min(...prices) : 0;
  const pricePad = (maxPrice - minPrice) * 0.06 || Math.max(1, maxPrice * 0.02);
  const yMax = maxPrice + pricePad;
  const yMin = minPrice - pricePad;

  function yFor(price) {
    // map price to y
    const ih = height - paddingBottom() - 20;
    const p = (price - yMin) / (yMax - yMin || 1);
    return 20 + (1 - p) * ih;
  }

  function xForIndex(i) {
    const iw = innerWidth();
    const cw = iw / Math.max(1, visible.length);
    return paddingLeft() + i * cw + cw / 2;
  }

  // tooltip data
  let tooltip = null;
  if (hoverRef.current.over && visible.length) {
    const idx = Math.min(Math.max(0, hoverRef.current.index), visible.length - 1);
    const c = visible[idx];
    tooltip = { idx, candle: c, x: xForIndex(idx), y: hoverRef.current.y };
  }

  // build grid Y labels
  const yTicks = 5;
  const yLabels = [];
  for (let i = 0; i <= yTicks; i++) {
    const v = yMin + (i / yTicks) * (yMax - yMin);
    yLabels.push(v);
  }

  // time labels (every Nth)
  const timeLabels = visible.map((c) => formatTimeLabel(c.time));
  const timeLabelEvery = Math.ceil(visible.length / 6);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height, background: COLORS.bg, borderRadius: 8, position: "relative", userSelect: "none" }}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      onWheel={onWheel}
    >
      <svg width="100%" height={height}>
        {/* background grid */}
        {yLabels.map((v, i) => {
          const y = yFor(v);
          return <line key={i} x1={paddingLeft()} x2={width - 20} y1={y} y2={y} stroke={COLORS.grid} strokeWidth="1" />;
        })}

        {/* price axis labels */}
        {yLabels.map((v, i) => {
          const y = yFor(v);
          return (
            <text key={i} x={paddingLeft() - 10} y={y + 4} fontSize="12" textAnchor="end" fill="#374151">
              {Math.round(v)}
            </text>
          );
        })}

        {/* candles */}
        {visible.map((c, i) => {
          const x = xForIndex(i);
          const iw = innerWidth();
          const cw = Math.max(4, iw / Math.max(1, visible.length) * 0.6);
          const isUp = c.close >= c.open;
          const color = isUp ? COLORS.up : COLORS.down;
          const yOpen = yFor(c.open);
          const yClose = yFor(c.close);
          const yHigh = yFor(c.high);
          const yLow = yFor(c.low);
          const rectY = Math.min(yOpen, yClose);
          const rectH = Math.max(1, Math.abs(yClose - yOpen));
          // wick line
          return (
            <g key={c.start || i}>
              {/* wick */}
              <line x1={x} x2={x} y1={yHigh} y2={yLow} stroke={COLORS.wick} strokeWidth={1} />
              {/* body */}
              <rect x={x - cw / 2} y={rectY} width={cw} height={rectH} fill={color} stroke={color} rx={1} />
            </g>
          );
        })}

        {/* time axis labels */}
        {visible.map((c, i) => {
          if (i % timeLabelEvery !== 0) return null;
          const x = xForIndex(i);
          return (
            <text key={i} x={x} y={height - 6} fontSize="12" textAnchor="middle" fill="#6b7280">
              {formatTimeLabel(c.time)}
            </text>
          );
        })}

        {/* volume histogram at bottom (small) */}
        {visible.length > 0 &&
          (() => {
            const volMax = Math.max(...visible.map((c) => c.volume || 0), 1);
            const volTop = height - paddingBottom() - 60;
            const volBase = height - paddingBottom();
            return visible.map((c, i) => {
              const x = xForIndex(i);
              const iw = innerWidth();
              const cw = Math.max(2, iw / Math.max(1, visible.length) * 0.6);
              const h = ((c.volume || 0) / volMax) * 40;
              const isUp = c.close >= c.open;
              const color = isUp ? "#bbf7d0" : "#ffd7d7";
              return <rect key={"v" + i} x={x - cw / 2} y={volBase - h} width={cw} height={h} fill={color} opacity="0.9" />;
            });
          })()}

        {/* crosshair & tooltip markers */}
        {tooltip && (
          <>
            <line x1={tooltip.x} x2={tooltip.x} y1={8} y2={height - paddingBottom()} stroke="#94a3b8" strokeDasharray="3 3" />
            <rect x={tooltip.x + 8} y={12} width="180" height="86" rx="6" fill="#0f172a" opacity="0.92" />
            <text x={tooltip.x + 16} y={30} fontSize="12" fill="#fff">
              {formatTimeLabel(tooltip.candle.time)}
            </text>
            <text x={tooltip.x + 16} y={48} fontSize="12" fill="#fff">
              Open: {tooltip.candle.open}
            </text>
            <text x={tooltip.x + 16} y={64} fontSize="12" fill="#fff">
              High: {tooltip.candle.high}
            </text>
            <text x={tooltip.x + 16} y={80} fontSize="12" fill="#fff">
              Low: {tooltip.candle.low}
            </text>
            <text x={tooltip.x + 16} y={96} fontSize="12" fill="#fff">
              Close: {tooltip.candle.close}
            </text>
          </>
        )}
      </svg>

      {/* small footer with controls */}
      <div style={{ position: "absolute", right: 12, bottom: 6, fontSize: 12, color: "#6b7280" }}>
        Showing last {visible.length} candles — Wheel to zoom
      </div>
    </div>
  );
});

export default ForexChart;