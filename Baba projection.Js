import { useState } from "react";
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceArea, Legend, Area, ComposedChart, Line } from "recharts";

// BABA monthly closing prices from IPO Sep 2014 to Feb 2026
const babaMonthly = [
  { date: "2014-09", price: 89.89 },
  { date: "2014-10", price: 99.54 },
  { date: "2014-11", price: 113.97 },
  { date: "2014-12", price: 103.99 },
  { date: "2015-01", price: 102.06 },
  { date: "2015-02", price: 86.03 },
  { date: "2015-03", price: 84.95 },
  { date: "2015-04", price: 81.71 },
  { date: "2015-05", price: 85.36 },
  { date: "2015-06", price: 82.37 },
  { date: "2015-07", price: 75.03 },
  { date: "2015-08", price: 63.45 },
  { date: "2015-09", price: 60.97 },
  { date: "2015-10", price: 78.48 },
  { date: "2015-11", price: 79.32 },
  { date: "2015-12", price: 81.27 },
  { date: "2016-01", price: 66.99 },
  { date: "2016-02", price: 71.60 },
  { date: "2016-03", price: 79.30 },
  { date: "2016-04", price: 79.52 },
  { date: "2016-05", price: 80.07 },
  { date: "2016-06", price: 79.56 },
  { date: "2016-07", price: 86.38 },
  { date: "2016-08", price: 95.81 },
  { date: "2016-09", price: 104.40 },
  { date: "2016-10", price: 98.85 },
  { date: "2016-11", price: 91.50 },
  { date: "2016-12", price: 88.09 },
  { date: "2017-01", price: 98.60 },
  { date: "2017-02", price: 100.65 },
  { date: "2017-03", price: 107.18 },
  { date: "2017-04", price: 112.97 },
  { date: "2017-05", price: 125.52 },
  { date: "2017-06", price: 141.57 },
  { date: "2017-07", price: 157.38 },
  { date: "2017-08", price: 169.10 },
  { date: "2017-09", price: 174.43 },
  { date: "2017-10", price: 186.41 },
  { date: "2017-11", price: 183.45 },
  { date: "2017-12", price: 172.43 },
  { date: "2018-01", price: 196.28 },
  { date: "2018-02", price: 188.53 },
  { date: "2018-03", price: 178.74 },
  { date: "2018-04", price: 183.76 },
  { date: "2018-05", price: 195.53 },
  { date: "2018-06", price: 190.30 },
  { date: "2018-07", price: 170.44 },
  { date: "2018-08", price: 169.07 },
  { date: "2018-09", price: 163.55 },
  { date: "2018-10", price: 145.78 },
  { date: "2018-11", price: 147.79 },
  { date: "2018-12", price: 137.07 },
  { date: "2019-01", price: 163.71 },
  { date: "2019-02", price: 183.48 },
  { date: "2019-03", price: 183.92 },
  { date: "2019-04", price: 186.56 },
  { date: "2019-05", price: 155.13 },
  { date: "2019-06", price: 169.37 },
  { date: "2019-07", price: 168.20 },
  { date: "2019-08", price: 174.38 },
  { date: "2019-09", price: 168.39 },
  { date: "2019-10", price: 175.12 },
  { date: "2019-11", price: 200.40 },
  { date: "2019-12", price: 212.10 },
  { date: "2020-01", price: 208.10 },
  { date: "2020-02", price: 209.50 },
  { date: "2020-03", price: 193.64 },
  { date: "2020-04", price: 203.70 },
  { date: "2020-05", price: 202.80 },
  { date: "2020-06", price: 216.38 },
  { date: "2020-07", price: 252.00 },
  { date: "2020-08", price: 286.39 },
  { date: "2020-09", price: 291.20 },
  { date: "2020-10", price: 307.84 },
  { date: "2020-11", price: 264.85 },
  { date: "2020-12", price: 232.73 },
  { date: "2021-01", price: 257.02 },
  { date: "2021-02", price: 232.05 },
  { date: "2021-03", price: 222.72 },
  { date: "2021-04", price: 228.52 },
  { date: "2021-05", price: 211.96 },
  { date: "2021-06", price: 214.35 },
  { date: "2021-07", price: 195.19 },
  { date: "2021-08", price: 163.80 },
  { date: "2021-09", price: 148.50 },
  { date: "2021-10", price: 164.37 },
  { date: "2021-11", price: 126.74 },
  { date: "2021-12", price: 118.77 },
  { date: "2022-01", price: 118.23 },
  { date: "2022-02", price: 109.65 },
  { date: "2022-03", price: 107.77 },
  { date: "2022-04", price: 89.73 },
  { date: "2022-05", price: 93.42 },
  { date: "2022-06", price: 118.97 },
  { date: "2022-07", price: 91.47 },
  { date: "2022-08", price: 91.80 },
  { date: "2022-09", price: 77.00 },
  { date: "2022-10", price: 65.39 },
  { date: "2022-11", price: 82.40 },
  { date: "2022-12", price: 88.09 },
  { date: "2023-01", price: 113.92 },
  { date: "2023-02", price: 90.85 },
  { date: "2023-03", price: 96.58 },
  { date: "2023-04", price: 85.71 },
  { date: "2023-05", price: 82.51 },
  { date: "2023-06", price: 87.74 },
  { date: "2023-07", price: 93.50 },
  { date: "2023-08", price: 88.55 },
  { date: "2023-09", price: 84.21 },
  { date: "2023-10", price: 85.24 },
  { date: "2023-11", price: 76.49 },
  { date: "2023-12", price: 77.72 },
  { date: "2024-01", price: 71.84 },
  { date: "2024-02", price: 75.21 },
  { date: "2024-03", price: 73.28 },
  { date: "2024-04", price: 78.78 },
  { date: "2024-05", price: 80.60 },
  { date: "2024-06", price: 73.37 },
  { date: "2024-07", price: 76.16 },
  { date: "2024-08", price: 83.08 },
  { date: "2024-09", price: 107.89 },
  { date: "2024-10", price: 95.36 },
  { date: "2024-11", price: 85.58 },
  { date: "2024-12", price: 85.99 },
  { date: "2025-01", price: 90.70 },
  { date: "2025-02", price: 113.42 },
  { date: "2025-03", price: 130.56 },
  { date: "2025-04", price: 120.28 },
  { date: "2025-05", price: 131.77 },
  { date: "2025-06", price: 137.67 },
  { date: "2025-07", price: 140.22 },
  { date: "2025-08", price: 145.94 },
  { date: "2025-09", price: 160.18 },
  { date: "2025-10", price: 192.67 },
  { date: "2025-11", price: 166.51 },
  { date: "2025-12", price: 146.64 },
  { date: "2026-01", price: 158.31 },
  { date: "2026-02", price: 155.77 },
];

// Forward months for projection
const futureMonths = [
  "2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10","2026-11","2026-12",
  "2027-01","2027-02","2027-03","2027-04","2027-05","2027-06","2027-07","2027-08","2027-09","2027-10","2027-11","2027-12",
  "2028-01","2028-02","2028-03","2028-04","2028-05","2028-06","2028-07","2028-08","2028-09","2028-10","2028-11","2028-12",
];

/*
  PROJECTION MODEL
  
  The 41-month cycle composite gives us DIRECTION (when momentum rises/falls).
  To project PRICE, we need to combine:
  1. The cycle phase (sinusoidal, anchored at troughs)
  2. A secular growth trend (BABA's long-term trajectory)
  3. Cycle amplitude (how much the price swings around trend)
  
  Cycle anchoring:
  - C3 trough: Oct 2022 (month index 97)
  - C4 projected trough: ~Mar 2026 (month index ~138, i.e. 41 months from C3)
  - C4 projected peak: ~Dec 2027 (month index ~159, i.e. ~21 months after C4 trough)
  
  We project 3 scenarios (bull / base / bear) with different trough depths and peak heights.
*/

const C3_TROUGH_IDX = 97; // Oct 2022
const PERIOD = 41;
const LAST_ACTUAL_IDX = babaMonthly.length - 1; // Feb 2026

// Build full dataset with projections
function buildProjectionData() {
  const allDates = [...babaMonthly.map(d => d.date), ...futureMonths];
  
  return allDates.map((date, i) => {
    const isActual = i <= LAST_ACTUAL_IDX;
    const actualPrice = isActual ? babaMonthly[i].price : null;
    
    // Cycle composite (sinusoidal, trough at C3_TROUGH_IDX, period=41)
    const phase = ((i - C3_TROUGH_IDX) / PERIOD) * 2 * Math.PI;
    const cycleRaw = -Math.cos(phase);
    const cycleNorm = (cycleRaw + 1) * 50;
    
    // --- PROJECTION PATHS (only for future months) ---
    let bull = null, base = null, bear = null;
    
    if (i > LAST_ACTUAL_IDX) {
      const monthsFromNow = i - LAST_ACTUAL_IDX;
      const currentPrice = 155.77;
      
      // C4 trough expected ~month index 138 (Mar 2026), which is ~1 month from now
      // C4 peak expected ~month index 159 (Dec 2027)
      const troughIdx = C3_TROUGH_IDX + PERIOD; // 138 = Mar 2026
      const peakIdx = troughIdx + Math.round(PERIOD / 2); // ~159 = Dec 2027
      
      // Cycle factor: -1 at trough, +1 at peak
      const projPhase = ((i - troughIdx) / PERIOD) * 2 * Math.PI;
      const cycleFactor = -Math.cos(projPhase); // -1 at trough, +1 at peak
      
      // BULL: shallow trough at $140, peak at $300, secular uptrend +2%/mo
      const bullTrough = 140;
      const bullPeak = 300;
      const bullMid = (bullTrough + bullPeak) / 2;
      const bullAmp = (bullPeak - bullTrough) / 2;
      const bullTrend = 1.005; // 0.5% monthly drift up
      bull = Math.round((bullMid + bullAmp * cycleFactor) * Math.pow(bullTrend, monthsFromNow) * 10) / 10;
      
      // BASE: trough at $125, peak at $260
      const baseTrough = 125;
      const basePeak = 260;
      const baseMid = (baseTrough + basePeak) / 2;
      const baseAmp = (basePeak - baseTrough) / 2;
      const baseTrend = 1.003;
      base = Math.round((baseMid + baseAmp * cycleFactor) * Math.pow(baseTrend, monthsFromNow) * 10) / 10;
      
      // BEAR: trough at $100, peak at $200
      const bearTrough = 100;
      const bearPeak = 200;
      const bearMid = (bearTrough + bearPeak) / 2;
      const bearAmp = (bearPeak - bearTrough) / 2;
      const bearTrend = 1.001;
      bear = Math.round((bearMid + bearAmp * cycleFactor) * Math.pow(bearTrend, monthsFromNow) * 10) / 10;
    }
    
    // Also connect the last actual price to projections
    if (i === LAST_ACTUAL_IDX) {
      bull = actualPrice;
      base = actualPrice;
      bear = actualPrice;
    }
    
    return {
      date,
      price: actualPrice,
      cycle: Math.round(cycleNorm * 10) / 10,
      bull,
      base,
      bear,
      isProjection: i > LAST_ACTUAL_IDX,
    };
  });
}

const fullData = buildProjectionData();

// Trim to show from 2017 onwards for readability (index 28 = Jan 2017)
const chartData = fullData.filter((d, i) => i >= 28);

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const isProj = payload[0]?.payload?.isProjection;
    return (
      <div className="bg-gray-900 border border-gray-600 rounded-lg p-3 text-xs shadow-xl">
        <p className="text-gray-300 font-mono mb-1.5 text-sm">{label}{isProj ? " (projected)" : ""}</p>
        {payload.map((p, i) => {
          if (p.value === null || p.value === undefined) return null;
          return (
            <p key={i} style={{ color: p.color || p.stroke }} className="font-medium">
              {p.name}: {p.name === "41-Mo Cycle" ? `${p.value}%` : `$${p.value}`}
            </p>
          );
        })}
      </div>
    );
  }
  return null;
};

export default function BABACycleProjection() {
  const [showCycle, setShowCycle] = useState(true);
  const [showBull, setShowBull] = useState(true);
  const [showBase, setShowBase] = useState(true);
  const [showBear, setShowBear] = useState(true);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">
            BABA — 41-Month Cycle Price Projection
          </h1>
          <p className="text-gray-500 text-sm">
            Dewey/Kitchin cycle composite overlaid with 3-scenario forward price path • C4 trough projected ~Mar 2026 • C4 peak projected ~Dec 2027
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-4 mb-4 text-sm">
          <label className="flex items-center gap-2 text-purple-300 cursor-pointer">
            <input type="checkbox" checked={showCycle} onChange={() => setShowCycle(!showCycle)} className="rounded" />
            41-Mo Cycle
          </label>
          <label className="flex items-center gap-2 text-green-300 cursor-pointer">
            <input type="checkbox" checked={showBull} onChange={() => setShowBull(!showBull)} className="rounded" />
            Bull ($140→$300)
          </label>
          <label className="flex items-center gap-2 text-yellow-300 cursor-pointer">
            <input type="checkbox" checked={showBase} onChange={() => setShowBase(!showBase)} className="rounded" />
            Base ($125→$260)
          </label>
          <label className="flex items-center gap-2 text-red-300 cursor-pointer">
            <input type="checkbox" checked={showBear} onChange={() => setShowBear(!showBear)} className="rounded" />
            Bear ($100→$200)
          </label>
        </div>

        {/* Main Chart */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 md:p-6 mb-6">
          <ResponsiveContainer width="100%" height={520}>
            <ComposedChart data={chartData} margin={{ top: 20, right: 60, left: 15, bottom: 30 }}>
              <defs>
                <linearGradient id="bullGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="baseGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#eab308" stopOpacity={0.12} />
                  <stop offset="100%" stopColor="#eab308" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="bearGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.1} />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="cycleGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#6b7280", fontSize: 9 }}
                interval={5}
                angle={-45}
                textAnchor="end"
                height={55}
              />
              <YAxis
                yAxisId="price"
                tick={{ fill: "#9ca3af", fontSize: 11 }}
                domain={[50, 340]}
                tickFormatter={(v) => `$${v}`}
              />
              {showCycle && (
                <YAxis
                  yAxisId="cycle"
                  orientation="right"
                  tick={{ fill: "#a78bfa", fontSize: 10 }}
                  domain={[0, 100]}
                  tickFormatter={(v) => `${v}%`}
                />
              )}
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11 }} />

              {/* Projection zone background */}
              <ReferenceArea
                yAxisId="price"
                x1="2026-02"
                x2="2028-12"
                fill="#6366f1"
                fillOpacity={0.04}
              />

              {/* C3 Trough marker */}
              <ReferenceLine yAxisId="price" x="2022-10" stroke="#22c55e" strokeDasharray="6 3" strokeOpacity={0.5} label={{ value: "C3 Trough", fill: "#22c55e", fontSize: 10, position: "top" }} />
              {/* C4 Projected Trough */}
              <ReferenceLine yAxisId="price" x="2026-03" stroke="#eab308" strokeDasharray="6 3" strokeOpacity={0.7} label={{ value: "C4 Trough (proj)", fill: "#eab308", fontSize: 10, position: "top" }} />
              {/* C4 Projected Peak */}
              <ReferenceLine yAxisId="price" x="2027-12" stroke="#f97316" strokeDasharray="6 3" strokeOpacity={0.5} label={{ value: "C4 Peak (proj)", fill: "#f97316", fontSize: 10, position: "top" }} />
              {/* Now line */}
              <ReferenceLine yAxisId="price" x="2026-02" stroke="#60a5fa" strokeWidth={2} strokeOpacity={0.6} label={{ value: "NOW", fill: "#60a5fa", fontSize: 11, position: "insideTopRight" }} />

              {/* Cycle composite */}
              {showCycle && (
                <Area
                  yAxisId="cycle"
                  type="monotone"
                  dataKey="cycle"
                  stroke="#a78bfa"
                  fill="url(#cycleGrad)"
                  strokeWidth={1.5}
                  name="41-Mo Cycle"
                  dot={false}
                  strokeDasharray="none"
                />
              )}

              {/* Bull projection */}
              {showBull && (
                <Area
                  yAxisId="price"
                  type="monotone"
                  dataKey="bull"
                  stroke="#22c55e"
                  fill="url(#bullGrad)"
                  strokeWidth={2}
                  strokeDasharray="8 4"
                  name="Bull Path"
                  dot={false}
                  connectNulls={false}
                />
              )}

              {/* Base projection */}
              {showBase && (
                <Area
                  yAxisId="price"
                  type="monotone"
                  dataKey="base"
                  stroke="#eab308"
                  fill="url(#baseGrad)"
                  strokeWidth={2}
                  strokeDasharray="8 4"
                  name="Base Path"
                  dot={false}
                  connectNulls={false}
                />
              )}

              {/* Bear projection */}
              {showBear && (
                <Area
                  yAxisId="price"
                  type="monotone"
                  dataKey="bear"
                  stroke="#ef4444"
                  fill="url(#bearGrad)"
                  strokeWidth={2}
                  strokeDasharray="8 4"
                  name="Bear Path"
                  dot={false}
                  connectNulls={false}
                />
              )}

              {/* Actual price (solid, on top) */}
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke="#60a5fa"
                strokeWidth={2.5}
                dot={false}
                name="BABA Actual"
                connectNulls={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Projection Table */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 mb-6">
          <h2 className="text-lg font-semibold mb-4">Cycle-Based Price Milestones</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700 text-gray-400 text-xs">
                  <th className="py-2 text-left">Date</th>
                  <th className="py-2 text-left">Cycle Phase</th>
                  <th className="py-2 text-right text-green-400">Bull</th>
                  <th className="py-2 text-right text-yellow-400">Base</th>
                  <th className="py-2 text-right text-red-400">Bear</th>
                  <th className="py-2 text-left pl-4">Reasoning</th>
                </tr>
              </thead>
              <tbody className="text-gray-300">
                <tr className="border-b border-gray-800 bg-blue-950/20">
                  <td className="py-2.5 font-mono text-blue-300">Feb 2026</td>
                  <td className="py-2.5 text-gray-400">Late downswing</td>
                  <td className="py-2.5 text-right font-mono">$155</td>
                  <td className="py-2.5 text-right font-mono">$155</td>
                  <td className="py-2.5 text-right font-mono">$155</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">Current price (actual)</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="py-2.5 font-mono text-yellow-300">Mar–Apr 2026</td>
                  <td className="py-2.5 text-green-400">C4 TROUGH</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$140</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$125</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$100</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">41 months from Oct 2022 C3 trough. Max selling pressure.</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="py-2.5 font-mono">Jun 2026</td>
                  <td className="py-2.5 text-gray-400">Early upswing</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$165</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$145</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$115</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">Recovery begins as cycle momentum inflects positive</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="py-2.5 font-mono">Oct 2026</td>
                  <td className="py-2.5 text-gray-400">Mid-upswing</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$210</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$180</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$140</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">Restocking accelerates, AI/cloud catalysts kick in</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="py-2.5 font-mono">Dec 2026</td>
                  <td className="py-2.5 text-gray-400">Upswing</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$230</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$195</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$155</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">Year-end target. Prior ATH zone re-test in bull case.</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="py-2.5 font-mono">Jun 2027</td>
                  <td className="py-2.5 text-gray-400">Late upswing</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$275</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$235</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$180</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">Approaching cycle peak zone. Momentum peaking.</td>
                </tr>
                <tr className="border-b border-gray-800 bg-orange-950/20">
                  <td className="py-2.5 font-mono text-orange-300">Dec 2027</td>
                  <td className="py-2.5 text-red-400">C4 PEAK</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$305</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$260</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$200</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">~21 months post-trough. Cycle peak = time to reduce.</td>
                </tr>
                <tr className="border-b border-gray-800">
                  <td className="py-2.5 font-mono">Jun 2028</td>
                  <td className="py-2.5 text-gray-400">Early downswing</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$270</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$220</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$165</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">Rollover begins. Begin reducing positions.</td>
                </tr>
                <tr className="bg-gray-800/50">
                  <td className="py-2.5 font-mono text-gray-400">Aug 2029</td>
                  <td className="py-2.5 text-green-400">C5 TROUGH</td>
                  <td className="py-2.5 text-right font-mono text-green-400">$200</td>
                  <td className="py-2.5 text-right font-mono text-yellow-400">$165</td>
                  <td className="py-2.5 text-right font-mono text-red-400">$110</td>
                  <td className="py-2.5 text-xs text-gray-500 pl-4">41 months from C4 trough. Next buy zone.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Key Assumptions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-green-950/20 rounded-xl border border-green-900/40 p-5">
            <h3 className="font-semibold text-green-300 text-sm mb-2">🟢 Bull Case Assumptions</h3>
            <ul className="text-xs text-gray-400 space-y-1.5">
              <li>• China cycle diverges positively from US</li>
              <li>• Shallow trough: $140 (200-EMA holds)</li>
              <li>• AI/Qwen monetization accelerates revenue</li>
              <li>• Ant Group restructuring clears regulatory</li>
              <li>• PBOC easing continues through H1 2026</li>
              <li>• Peak target: $300 (near Oct 2020 ATH)</li>
            </ul>
          </div>
          <div className="bg-yellow-950/20 rounded-xl border border-yellow-900/40 p-5">
            <h3 className="font-semibold text-yellow-300 text-sm mb-2">🟡 Base Case Assumptions</h3>
            <ul className="text-xs text-gray-400 space-y-1.5">
              <li>• Correlated pullback with US SPX -15%</li>
              <li>• Trough: $125 (prior breakout level)</li>
              <li>• Recovery led by earnings improvement</li>
              <li>• Cloud/international segments stabilize</li>
              <li>• Geopolitics neutral (no new escalation)</li>
              <li>• Peak target: $260 (2018 high zone)</li>
            </ul>
          </div>
          <div className="bg-red-950/20 rounded-xl border border-red-900/40 p-5">
            <h3 className="font-semibold text-red-300 text-sm mb-2">🔴 Bear Case Assumptions</h3>
            <ul className="text-xs text-gray-400 space-y-1.5">
              <li>• 1260H list + new sanctions escalation</li>
              <li>• Trough: $100 (re-test 2024 lows)</li>
              <li>• China property crisis worsens</li>
              <li>• Tech regulation returns</li>
              <li>• VIE structure / delisting fears resurface</li>
              <li>• Peak target: $200 (capped recovery)</li>
            </ul>
          </div>
        </div>

        {/* Methodology Note */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="text-sm font-semibold text-indigo-300 mb-2">Methodology</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            The projection uses a sinusoidal cycle composite (period = 41 months) anchored at the C3 trough (Oct 2022, $65.39). 
            Each scenario defines a trough price, peak price, and secular drift rate. The cycle composite determines the <em>shape</em> of the 
            path (when it dips and rallies), while the scenario parameters determine the <em>magnitude</em>. The C4 trough is projected at 
            month 138 (Mar 2026 = 41 months from Oct 2022). The C4 peak is projected at ~month 159 (Dec 2027 = half-cycle later). 
            This is a mechanical cycle model — it does not incorporate real-time news, earnings, or policy changes. The pink cycle 
            line measures momentum amplitude (0% = trough, 100% = peak), not price level. Use the cycle for timing; use fundamental 
            analysis for magnitude.
          </p>
          <p className="text-xs text-gray-500 mt-2">
            ⚠️ Cycle-based projections are probabilistic timing tools, not price guarantees. Not investment advice.
          </p>
        </div>
      </div>
    </div>
  );
}