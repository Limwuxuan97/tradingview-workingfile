"""
PERFORMANCE DASHBOARD — Interactive HTML Report
=================================================
Generates a self-contained HTML dashboard with:
  1. Equity curve vs SPY benchmark
  2. Drawdown chart
  3. Monthly returns heatmap
  4. Trade distribution by setup type
  5. Kitchin cycle phase analysis
  6. Rolling Sharpe ratio
  7. Win/Loss distribution
  8. Top trades table
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, List, Optional


def generate_dashboard(results: dict, output_path: str = None) -> str:
    """Generate a self-contained HTML dashboard from backtest results."""
    
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backtest_results",
            f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    p = results["performance"]
    t = results["trades"]
    b = results["benchmark"]
    cycle = results.get("cycle", {})
    equity_data = results.get("equity_curve", {})
    trade_log = results.get("trade_log", [])

    # Prepare equity curve data
    eq_dates = list(equity_data.keys())
    eq_values = list(equity_data.values())
    
    # Calculate SPY-equivalent equity (normalized to same start)
    initial_eq = eq_values[0] if eq_values else 8000
    spy_return_pct = b.get("spy_return_pct", 0)
    
    # Monthly returns
    monthly_returns = _compute_monthly_returns(equity_data)
    
    # Drawdown series
    dd_data = _compute_drawdown(eq_values)
    
    # Trade stats by setup
    setup_stats = t.get("by_setup", {})
    
    # Win/loss distribution
    pnl_values = [tr["pnl"] for tr in trade_log]
    r_values = [tr["r_multiple"] for tr in trade_log]
    
    # Top trades
    sorted_trades = sorted(trade_log, key=lambda x: x["pnl"], reverse=True)
    top_winners = sorted_trades[:10]
    top_losers = sorted_trades[-10:][::-1]
    
    # Phase distribution
    phase_data = cycle.get("phases_traded", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Algo Trading System — Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-muted: #8b949e;
            --green: #3fb950;
            --red: #f85149;
            --blue: #58a6ff;
            --purple: #bc8cff;
            --yellow: #d29922;
            --orange: #db6d28;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #1a1e2e, #0d1117);
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        .header h1 {{
            font-size: 28px;
            background: linear-gradient(90deg, var(--blue), var(--purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header .subtitle {{ color: var(--text-muted); margin-top: 5px; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        .kpi-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 18px;
            text-align: center;
        }}
        .kpi-card .label {{ color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
        .kpi-card .value {{ font-size: 28px; font-weight: 700; margin-top: 5px; }}
        .kpi-card .value.positive {{ color: var(--green); }}
        .kpi-card .value.negative {{ color: var(--red); }}
        .kpi-card .value.neutral {{ color: var(--blue); }}
        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }}
        .chart-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
        }}
        .chart-card.full {{ grid-column: 1 / -1; }}
        .chart-card h3 {{ color: var(--blue); margin-bottom: 15px; font-size: 16px; }}
        .chart-container {{ position: relative; height: 300px; }}
        .chart-container.tall {{ height: 400px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid var(--border); }}
        th {{ color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px; }}
        td {{ color: var(--text); }}
        th:first-child, td:first-child {{ text-align: left; }}
        .positive {{ color: var(--green); }}
        .negative {{ color: var(--red); }}
        .cycle-bar {{
            display: inline-block;
            height: 20px;
            border-radius: 3px;
            margin: 2px 1px;
        }}
        .monthly-grid {{
            display: grid;
            grid-template-columns: auto repeat(12, 1fr) auto;
            gap: 2px;
            font-size: 11px;
        }}
        .monthly-cell {{
            padding: 6px 4px;
            text-align: center;
            border-radius: 3px;
            font-weight: 500;
        }}
        .monthly-header {{ color: var(--text-muted); font-weight: 600; }}
        @media (max-width: 900px) {{
            .chart-grid {{ grid-template-columns: 1fr; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Unified Trading System — Performance Report</h1>
        <div class="subtitle">Qullamaggie Momentum + Kitchin Cycle Overlay | {eq_dates[0][:10] if eq_dates else 'N/A'} to {eq_dates[-1][:10] if eq_dates else 'N/A'}</div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Total Return</div>
            <div class="value {'positive' if p['total_return_pct'] > 0 else 'negative'}">{p['total_return_pct']:+.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="label">CAGR</div>
            <div class="value {'positive' if p['cagr_pct'] > 0 else 'negative'}">{p['cagr_pct']:+.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="label">Max Drawdown</div>
            <div class="value negative">{p['max_drawdown_pct']:.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="label">Sharpe Ratio</div>
            <div class="value {'positive' if p['sharpe_ratio'] > 1 else 'neutral'}">{p['sharpe_ratio']:.3f}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Sortino Ratio</div>
            <div class="value {'positive' if p['sortino_ratio'] > 1 else 'neutral'}">{p['sortino_ratio']:.3f}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Profit Factor</div>
            <div class="value {'positive' if t['profit_factor'] > 1.3 else 'neutral'}">{t['profit_factor']:.3f}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Win Rate</div>
            <div class="value neutral">{t['win_rate_pct']:.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="label">Total Trades</div>
            <div class="value neutral">{t['total']}</div>
        </div>
        <div class="kpi-card">
            <div class="label">Alpha vs SPY</div>
            <div class="value {'positive' if b['alpha_pct'] > 0 else 'negative'}">{b['alpha_pct']:+.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="label">Final Equity</div>
            <div class="value positive">${p['final_equity']:,.0f}</div>
        </div>
    </div>

    <!-- Charts -->
    <div class="chart-grid">
        <!-- Equity Curve -->
        <div class="chart-card full">
            <h3>Equity Curve vs SPY Benchmark</h3>
            <div class="chart-container tall">
                <canvas id="equityChart"></canvas>
            </div>
        </div>

        <!-- Drawdown -->
        <div class="chart-card full">
            <h3>Drawdown</h3>
            <div class="chart-container">
                <canvas id="drawdownChart"></canvas>
            </div>
        </div>

        <!-- Setup Distribution -->
        <div class="chart-card">
            <h3>Trades by Setup Type</h3>
            <div class="chart-container">
                <canvas id="setupPie"></canvas>
            </div>
        </div>

        <!-- Win Rate by Setup -->
        <div class="chart-card">
            <h3>Win Rate & Avg R by Setup</h3>
            <div class="chart-container">
                <canvas id="setupBar"></canvas>
            </div>
        </div>

        <!-- R-Multiple Distribution -->
        <div class="chart-card">
            <h3>R-Multiple Distribution</h3>
            <div class="chart-container">
                <canvas id="rDistChart"></canvas>
            </div>
        </div>

        <!-- Cycle Phase Performance -->
        <div class="chart-card">
            <h3>Kitchin Cycle Phase Distribution</h3>
            <div class="chart-container">
                <canvas id="cycleChart"></canvas>
            </div>
        </div>

        <!-- Monthly Returns Heatmap -->
        <div class="chart-card full">
            <h3>Monthly Returns Heatmap (%)</h3>
            <div id="monthlyHeatmap" class="monthly-grid">
                {_generate_monthly_heatmap_html(monthly_returns)}
            </div>
        </div>

        <!-- Top Trades Table -->
        <div class="chart-card">
            <h3>Top 10 Winners</h3>
            <table>
                <tr><th>Ticker</th><th>Setup</th><th>Entry</th><th>PnL</th><th>R</th><th>Days</th></tr>
                {''.join(f'<tr><td>{tr["ticker"]}</td><td>{tr["setup"]}</td><td>{tr["entry_date"]}</td><td class="positive">${tr["pnl"]:,.0f}</td><td>{tr["r_multiple"]:.1f}</td><td>{tr["days"]}</td></tr>' for tr in top_winners)}
            </table>
        </div>

        <!-- Top Losers -->
        <div class="chart-card">
            <h3>Top 10 Losers</h3>
            <table>
                <tr><th>Ticker</th><th>Setup</th><th>Entry</th><th>PnL</th><th>R</th><th>Days</th></tr>
                {''.join(f'<tr><td>{tr["ticker"]}</td><td>{tr["setup"]}</td><td>{tr["entry_date"]}</td><td class="negative">${tr["pnl"]:,.0f}</td><td>{tr["r_multiple"]:.1f}</td><td>{tr["days"]}</td></tr>' for tr in top_losers)}
            </table>
        </div>
    </div>

    <script>
        Chart.defaults.color = '#c9d1d9';
        Chart.defaults.borderColor = '#30363d';
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif';

        // === EQUITY CURVE ===
        const eqLabels = {json.dumps(eq_dates[::5])};  // Sample every 5 days for performance
        const eqValues = {json.dumps(eq_values[::5])};
        const initialEq = {initial_eq};
        const spyReturn = {spy_return_pct / 100};
        const spyValues = eqLabels.map((_, i) => initialEq * (1 + spyReturn * i / (eqLabels.length - 1)));

        new Chart(document.getElementById('equityChart'), {{
            type: 'line',
            data: {{
                labels: eqLabels.map(d => d.substring(0, 10)),
                datasets: [
                    {{
                        label: 'Strategy',
                        data: eqValues,
                        borderColor: '#58a6ff',
                        backgroundColor: 'rgba(88, 166, 255, 0.1)',
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.1,
                    }},
                    {{
                        label: 'SPY Buy & Hold',
                        data: spyValues,
                        borderColor: '#8b949e',
                        borderDash: [5, 5],
                        borderWidth: 1.5,
                        pointRadius: 0,
                        tension: 0.1,
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{
                    x: {{ display: true, ticks: {{ maxTicksLimit: 12 }} }},
                    y: {{ display: true, ticks: {{ callback: v => '$' + v.toLocaleString() }} }}
                }}
            }}
        }});

        // === DRAWDOWN ===
        const ddValues = {json.dumps(dd_data[::5])};
        new Chart(document.getElementById('drawdownChart'), {{
            type: 'line',
            data: {{
                labels: eqLabels.map(d => d.substring(0, 10)),
                datasets: [{{
                    label: 'Drawdown %',
                    data: ddValues,
                    borderColor: '#f85149',
                    backgroundColor: 'rgba(248, 81, 73, 0.15)',
                    fill: true,
                    borderWidth: 1.5,
                    pointRadius: 0,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ ticks: {{ maxTicksLimit: 12 }} }},
                    y: {{ ticks: {{ callback: v => v.toFixed(0) + '%' }} }}
                }}
            }}
        }});

        // === SETUP PIE ===
        const setupNames = {json.dumps(list(setup_stats.keys()))};
        const setupCounts = {json.dumps([s['count'] for s in setup_stats.values()])};
        new Chart(document.getElementById('setupPie'), {{
            type: 'doughnut',
            data: {{
                labels: setupNames,
                datasets: [{{
                    data: setupCounts,
                    backgroundColor: ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff'],
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});

        // === SETUP BAR ===
        const setupWR = {json.dumps([round(s['win_rate'], 1) for s in setup_stats.values()])};
        const setupR = {json.dumps([round(s['avg_r'], 2) for s in setup_stats.values()])};
        new Chart(document.getElementById('setupBar'), {{
            type: 'bar',
            data: {{
                labels: setupNames,
                datasets: [
                    {{ label: 'Win Rate %', data: setupWR, backgroundColor: '#3fb950' }},
                    {{ label: 'Avg R-Multiple', data: setupR, backgroundColor: '#58a6ff' }},
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});

        // === R-MULTIPLE DISTRIBUTION ===
        const rValues = {json.dumps([round(r, 1) for r in r_values])};
        const rBins = {{}};
        rValues.forEach(r => {{
            const bin = Math.max(-3, Math.min(10, Math.round(r)));
            rBins[bin] = (rBins[bin] || 0) + 1;
        }});
        const rLabels = Object.keys(rBins).sort((a, b) => a - b);
        const rCounts = rLabels.map(k => rBins[k]);
        const rColors = rLabels.map(k => k >= 0 ? '#3fb950' : '#f85149');

        new Chart(document.getElementById('rDistChart'), {{
            type: 'bar',
            data: {{
                labels: rLabels.map(r => r + 'R'),
                datasets: [{{ label: 'Count', data: rCounts, backgroundColor: rColors }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});

        // === CYCLE PHASE ===
        const phaseLabels = {json.dumps(list(phase_data.keys()))};
        const phaseCounts = {json.dumps(list(phase_data.values()))};
        const phaseColors = [
            '#f85149', '#d29922', '#3fb950', '#58a6ff', '#bc8cff', '#db6d28'
        ];
        new Chart(document.getElementById('cycleChart'), {{
            type: 'bar',
            data: {{
                labels: phaseLabels,
                datasets: [{{
                    label: 'Trading Days',
                    data: phaseCounts,
                    backgroundColor: phaseColors,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {{ x: {{ beginAtZero: true }} }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _compute_monthly_returns(equity_data: dict) -> dict:
    """Compute monthly returns from equity curve."""
    monthly = {}
    prev_equity = None
    prev_month = None
    
    for date_str, equity in equity_data.items():
        date_str = str(date_str)[:10]
        try:
            year = int(date_str[:4])
            month = int(date_str[5:7])
        except (ValueError, IndexError):
            continue
        
        key = (year, month)
        
        if prev_month is not None and key != prev_month:
            if prev_equity and prev_equity > 0:
                ret = (equity / prev_equity - 1) * 100
                monthly[prev_month] = round(ret, 1)
            prev_equity = equity
        
        prev_month = key
        if prev_equity is None:
            prev_equity = equity
    
    return monthly


def _compute_drawdown(equity_values: list) -> list:
    """Compute drawdown percentage series."""
    if not equity_values:
        return []
    
    peak = equity_values[0]
    dd = []
    for eq in equity_values:
        peak = max(peak, eq)
        dd.append(round((eq - peak) / peak * 100, 2) if peak > 0 else 0)
    return dd


def _generate_monthly_heatmap_html(monthly_returns: dict) -> str:
    """Generate HTML grid cells for monthly returns heatmap."""
    if not monthly_returns:
        return "<div>No monthly data available</div>"
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    years = sorted(set(y for y, m in monthly_returns.keys()))
    
    # Header row
    html = '<div class="monthly-cell monthly-header">Year</div>'
    for m in months:
        html += f'<div class="monthly-cell monthly-header">{m}</div>'
    html += '<div class="monthly-cell monthly-header">Total</div>'
    
    for year in years:
        html += f'<div class="monthly-cell monthly-header">{year}</div>'
        year_total = 0
        has_data = False
        
        for m_idx in range(1, 13):
            ret = monthly_returns.get((year, m_idx))
            if ret is not None:
                has_data = True
                year_total += ret
                # Color gradient
                if ret > 5:
                    bg = "rgba(63, 185, 80, 0.6)"
                elif ret > 2:
                    bg = "rgba(63, 185, 80, 0.35)"
                elif ret > 0:
                    bg = "rgba(63, 185, 80, 0.15)"
                elif ret > -2:
                    bg = "rgba(248, 81, 73, 0.15)"
                elif ret > -5:
                    bg = "rgba(248, 81, 73, 0.35)"
                else:
                    bg = "rgba(248, 81, 73, 0.6)"
                html += f'<div class="monthly-cell" style="background:{bg}">{ret:+.1f}</div>'
            else:
                html += '<div class="monthly-cell" style="opacity:0.3">—</div>'
        
        # Year total
        if has_data:
            color = "var(--green)" if year_total > 0 else "var(--red)"
            html += f'<div class="monthly-cell" style="color:{color};font-weight:700">{year_total:+.1f}</div>'
        else:
            html += '<div class="monthly-cell">—</div>'
    
    return html


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        # Find most recent results file
        results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backtest_results"
        )
        files = sorted([f for f in os.listdir(results_dir) if f.endswith(".json")])
        if not files:
            print("No results files found!")
            sys.exit(1)
        results_file = os.path.join(results_dir, files[-1])
    
    with open(results_file, "r") as f:
        results = json.load(f)
    
    output = generate_dashboard(results)
    print(f"Dashboard generated: {output}")
