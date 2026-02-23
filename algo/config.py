"""
UNIFIED TRADING SYSTEM — MASTER CONFIGURATION
=============================================
All parameters extracted from:
  - Qullamaggie Trading System Blueprint.docx
  - Strategic Book allocation.xlsx (Kitchin cycle timing)
  - CONVERSATION_CONTEXT.md (Monster Move, CME T+35/T+42)
  - SCRIPT 1 BABA Macro Cycle Navigator (Pine Script weights)
  - Baba projection.Js (cycle anchors)
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict
import math

# ============================================================================
# ACCOUNT & PORTFOLIO
# ============================================================================
INITIAL_CAPITAL = 8_000.0

# --- Qullamaggie Position Sizing (aggressive, concentrated) ---
# He sizes 10-20% of account per position, holds 15-20 positions
# In strong markets: up to 25-30 positions (200-300% invested w/ margin)
MAX_POSITIONS_BULL = 20            # Strong bull: up to 20 positions
MAX_POSITIONS_NEUTRAL = 12         # Neutral: moderate exposure
MAX_POSITIONS_BEAR = 3             # Bear: near zero (preserve capital)
MAX_POSITIONS = 20                 # Absolute ceiling
MIN_POSITIONS = 5

# Risk per trade: Qullamaggie risks ~1% on the STOP, but sizes 10-20% of account
# The difference is tight stops (2-5% from entry). So risk_pct * leverage = big position.
MAX_RISK_PER_TRADE_PCT = 0.03      # 3% of account risk per trade
MAX_TOTAL_RISK_PCT = 0.30          # 30% total open risk
COMMISSION_PCT = 0.001             # 0.1% per side
SLIPPAGE_PCT = 0.001               # 0.1% slippage estimate

# Position as % of equity (Qullamaggie: 10-20% per position)
MAX_POSITION_PCT_OF_EQUITY = 0.20  # Max 20% of equity in single position
TARGET_POSITION_PCT = 0.12         # Target ~12% per position

# ============================================================================
# KITCHIN 41-MONTH CYCLE
# ============================================================================
@dataclass
class KitchinCycleConfig:
    """41-month Kitchin inventory cycle parameters."""
    period_months: float = 41.0
    # Historical trough anchors (from Strategic Book xlsx & projection chart)
    c1_trough: date = date(2015, 9, 1)   # $58 BABA
    c2_trough: date = date(2019, 1, 1)   # $130 BABA
    c3_trough: date = date(2022, 10, 1)  # $58 BABA / $65.39 low
    c4_trough_projected: date = date(2026, 3, 15)  # Projected
    c4_peak_projected: date = date(2027, 12, 1)    # Projected

    # China/EM Kitchin cycle — LEADS US by 12-18 months
    # China inventory cycle runs ~37 months, anchored to its own PPI trough
    # EM cycles are shorter and EARLIER than US: when US peaks, China is already expanding
    # BABA, JD, PDD, NIO etc. follow China's cycle, NOT the US 41-month cycle
    # China's most recent trough: ~Jan 2024 (15 months before US projected Mar 2026 trough)
    # So by Feb 2026, China is ~25 months into expansion = mid-expansion phase
    china_trough: date = date(2024, 1, 1)    # EM trough ~15 months before US C4 trough
    china_period_months: float = 37.0        # China cycles shorter than global

    # Phase definitions (fraction of cycle)
    # 0.00-0.10 = Late Contraction (accumulate zone)
    # 0.10-0.25 = Trough / Accumulation
    # 0.25-0.40 = Early Expansion
    # 0.40-0.55 = Mid Expansion
    # 0.55-0.70 = Late Expansion / Peak
    # 0.70-0.85 = Early Contraction
    # 0.85-1.00 = Late Contraction

    # Cycle score mapping (from Pine Script)
    def get_cycle_score(self, position: float) -> float:
        """Returns 0-100 score based on cycle position (0=trough, 1=next trough)."""
        if position < 0.10:
            return 60.0 + position / 0.10 * 30.0
        elif position < 0.25:
            return 90.0 - (position - 0.10) / 0.15 * 20.0
        elif position < 0.50:
            return 70.0 - (position - 0.25) / 0.25 * 30.0
        elif position < 0.75:
            return 40.0 - (position - 0.50) / 0.25 * 25.0
        else:
            return 15.0 + (position - 0.75) / 0.25 * 45.0

    def get_phase_label(self, position: float) -> str:
        if position < 0.10:
            return "LATE_CONTRACTION"
        elif position < 0.25:
            return "TROUGH_ACCUMULATE"
        elif position < 0.40:
            return "EARLY_EXPANSION"
        elif position < 0.55:
            return "MID_EXPANSION"
        elif position < 0.70:
            return "LATE_EXPANSION_PEAK"
        elif position < 0.85:
            return "EARLY_CONTRACTION"
        else:
            return "LATE_CONTRACTION"

    # Position sizing multiplier by cycle phase (Qullamaggie: aggressive in bull, minimal in bear)
    def get_cycle_sizing_multiplier(self, position: float) -> float:
        """Aggressive near trough/expansion, defensive near peak/contraction."""
        phase = self.get_phase_label(position)
        multipliers = {
            "LATE_CONTRACTION": 2.0,       # Accumulate zone — start building
            "TROUGH_ACCUMULATE": 2.5,      # Max conviction — user's key insight
            "EARLY_EXPANSION": 2.5,        # Ride the wave HARD
            "MID_EXPANSION": 2.0,          # Still aggressive
            "LATE_EXPANSION_PEAK": 1.0,    # Start trimming
            "EARLY_CONTRACTION": 0.4,      # Go mostly to cash
        }
        return multipliers.get(phase, 1.0)


KITCHIN = KitchinCycleConfig()

# ============================================================================
# QULLAMAGGIE SCREENING PARAMETERS (from Blueprint docx)
# ============================================================================
@dataclass
class QullamaggieConfig:
    """Qullamaggie momentum breakout parameters."""

    # --- ADR / Volatility Filter ---
    min_adr_pct: float = 2.0           # ADR(20) >= 2%
    max_adr_pct: float = 30.0          # Filter out garbage

    # --- Trend Filter ---
    # Price > 10 SMA > 20 SMA > 50 SMA, all with positive slope
    trend_mas: List[int] = field(default_factory=lambda: [10, 20, 50])
    long_trend_ma: int = 200           # Must be above 200 SMA for HTF

    # --- Relative Strength ---
    rs_lookback: int = 63              # ~3 months for RS ranking
    rs_top_pct: float = 2.5            # Top 2.5% RS rank for HTFs
    rs_ep_top_pct: float = 10.0        # Looser for EPs

    # --- HTF (High Tight Flag) ---
    htf_prior_run_pct: float = 30.0    # Prior trend: +30-100% in 4-8 weeks
    htf_prior_run_max_pct: float = 100.0
    htf_prior_run_min_weeks: int = 4
    htf_prior_run_max_weeks: int = 8
    htf_consolidation_min_days: int = 5
    htf_consolidation_max_days: int = 40
    htf_max_retracement_pct: float = 25.0
    htf_vcp_atr_ratio: float = 0.50    # 5d ATR < 50% of 20d ATR
    htf_volume_dry_ratio: float = 0.70 # Last 3-5d vol <= 70% of 20d SMA vol

    # --- EP (Episodic Pivot) ---
    ep_min_gap_pct: float = 10.0       # Minimum gap up
    ep_min_rvol: float = 2.0           # Relative volume >= 2x
    ep_min_avg_volume: int = 300_000   # 50d average volume
    ep_base_min_months: int = 3        # 3-6 month flat prior base
    ep_base_max_months: int = 6

    # --- Entry Triggers ---
    breakout_rvol_min: float = 2.0     # RVol >= 2.0 at breakout
    orb_minutes: int = 30              # Opening range breakout window

    # --- Risk Management (Qullamaggie-style aggressive) ---
    risk_per_trade_pct: float = 0.03   # 3% of account risk per trade
    stop_method: str = "base_low"      # "base_low" or "breakout_day_low"
    max_stop_adr_multiple: float = 2.5 # Stop distance <= 2.5x ADR (slightly more room)
    # Qullamaggie: Trim 1/3 to 1/2 after 3-5 day burst, trail rest on 10/20 SMA
    initial_sell_pct: float = 0.33     # Sell 33% (1/3) at first target
    first_target_r_multiple: float = 2.0  # 2R first target
    second_sell_pct: float = 0.33      # Sell another 33% at second target
    second_target_r_multiple: float = 5.0  # 5R second target
    # Qullamaggie trails on 10/20 SMA for momentum breakouts (tighter = locks gains)
    # 50 SMA gives back too much profit — 20 SMA was the setting at ~90% CAGR
    # EPs use 50 SMA (longer swing trades need more room)
    trail_ma: int = 20                 # Trail on 20 SMA — locks in gains, Qullamaggie default
    trail_ma_alt: int = 50             # 50 SMA for EPs (longer-term swing trades)
    # Start trailing after partial profit or after enough days
    trail_from_day: int = 10           # Start trailing after 10 days in trade
    # Breakeven stop: once trade hits 1.5R, move stop to entry price
    # Prevents winning trades from becoming losers before partial trigger at 2R
    breakeven_r_threshold: float = 1.5

    # --- Pyramiding (add to winners) ---
    # Qullamaggie adds to positions that are working
    pyramid_enabled: bool = True
    pyramid_threshold_r: float = 1.0   # Add when position is at 1R+ (sooner)
    pyramid_size_pct: float = 0.75     # Add 75% of original size (aggressive)
    pyramid_max_adds: int = 3          # Max 3 adds per position (compound winners)

    # --- Regime Filter (Market Health) ---
    regime_spy_above_ma: int = 50      # SPY close > 50 SMA
    regime_ema_fast: int = 10          # 10 EMA > 20 EMA for broad market
    regime_ema_slow: int = 20
    max_consecutive_stops: int = 8     # Halt after 8 consecutive stops (low win rate expected)


QMAG = QullamaggieConfig()

# ============================================================================
# MONSTER MOVE DETECTION (0-100 composite)
# ============================================================================
@dataclass
class MonsterMoveConfig:
    """Four-layer monster move scoring system."""

    # Layer 1: Narrative Mispricing (0-25)
    # Revenue contradiction, analyst drift, valuation gap, short interest declining
    narrative_weight: float = 25.0

    # Layer 2: Institutional/Insider Activity (0-25)
    # Insider buying clusters, size vs salary, institutional ownership increase
    institutional_weight: float = 25.0

    # Layer 3: Technical/Cycle Timing (0-25)
    # CME T+35/T+42 flush complete, Kitchin phase, Qullamaggie setup, MA support
    technical_weight: float = 25.0

    # Layer 4: Fundamental Quality Gate (0-25)
    # Revenue growth, positive OCF, manageable debt, ROE>10%, market cap>$10B
    fundamental_weight: float = 25.0

    # Thresholds
    buy_threshold: float = 65.0        # Score > 65 = actionable
    strong_buy_threshold: float = 80.0 # Score > 80 = high conviction


MONSTER = MonsterMoveConfig()

# ============================================================================
# SECTOR ROTATION (Mark Newton methodology)
# ============================================================================
@dataclass
class SectorRotationConfig:
    """Newton's multi-layer sector rotation."""

    # Sector ETFs to track
    sector_etfs: Dict[str, str] = field(default_factory=lambda: {
        "XLK": "Technology",
        "XLF": "Financials",
        "XLE": "Energy",
        "XLI": "Industrials",
        "XLU": "Utilities",
        "XLV": "Healthcare",
        "XLY": "Cons. Disc.",
        "XLP": "Cons. Staples",
        "XLB": "Materials",
        "XLRE": "Real Estate",
        "XLC": "Communication",
    })

    # Intermarket indicators
    dxy_ticker: str = "DX-Y.NYB"        # US Dollar Index
    us10y_ticker: str = "^TNX"           # 10-Year yield
    crude_ticker: str = "CL=F"          # WTI Crude
    gold_ticker: str = "GC=F"           # Gold
    copper_ticker: str = "HG=F"         # Copper
    spy_ticker: str = "SPY"
    qqq_ticker: str = "QQQ"

    # Breadth thresholds
    breadth_bullish_pct: float = 60.0   # >60% stocks above 50d MA = bullish
    breadth_bearish_pct: float = 30.0   # <30% = bearish

    # RS lookback for sector rotation
    rs_lookback: int = 63               # ~3 months
    rs_long_lookback: int = 126         # ~6 months


SECTOR = SectorRotationConfig()

# ============================================================================
# CME T+35 / T+42 CYCLE
# ============================================================================
@dataclass
class CMECycleConfig:
    """CME futures settlement forced buying/selling mechanics."""
    t35_days: int = 35                  # Forced delivery deadline
    t42_days: int = 42                  # Second flush (T+35 + 7)
    t48_days: int = 48                  # Crypto settlement (longer)

    # Major CME quarterly expiry months
    quarterly_expiries: List[int] = field(default_factory=lambda: [3, 6, 9, 12])
    # Typical expiry is 3rd Friday of the month


CME = CMECycleConfig()

# ============================================================================
# MACRO / LIQUIDITY (from Pine Script weights)
# ============================================================================
@dataclass
class MacroConfig:
    """Macro and liquidity overlay settings."""
    # Weights from Pine Script composite
    tech_weight: float = 50.0
    cycle_weight: float = 25.0
    macro_weight: float = 25.0

    # DXY scoring: falling DXY = bullish for international/EM
    dxy_sma_len: int = 63              # ~3 months daily

    # Composite thresholds (from Pine Script)
    buy_threshold: float = 60.0
    sell_threshold: float = 35.0
    strong_buy_threshold: float = 75.0
    strong_sell_threshold: float = 25.0


MACRO = MacroConfig()

# ============================================================================
# TICKER UNIVERSE
# ============================================================================
# Start with liquid US large-caps + key China ADRs
# Will expand based on sector rotation signals

US_CORE_UNIVERSE = [
    # Mega-cap tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ORCL", "CRM",
    # Semis
    "AMD", "INTC", "QCOM", "MU", "MRVL", "AMAT", "LRCX", "KLAC", "SMCI", "ARM",
    # Software / Cloud / Cyber
    "ADBE", "NOW", "PANW", "CRWD", "SNOW", "PLTR", "DDOG", "NET",
    "ZS", "FTNT", "SHOP", "COIN", "MELI", "SE",
    # Financials (high-beta)
    "JPM", "GS", "MS", "V", "MA", "AXP", "BLK",
    # Healthcare / Biotech (growth)
    "UNH", "LLY", "ABBV", "TMO", "ISRG", "VRTX", "REGN",
    # Industrials (cyclical)
    "CAT", "DE", "GE", "HON", "RTX", "LMT", "UNP", "URI",
    # Energy (momentum)
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "OXY",
    # Consumer (high-growth)
    "COST", "HD", "NKE", "SBUX", "MCD", "ABNB", "DASH", "LULU", "DECK",
    # Communication
    "NFLX", "DIS", "TMUS",
]

CHINA_ADR_UNIVERSE = [
    "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI", "BEKE",
    "TME", "BILI", "ZTO", "VNET", "FUTU", "MNSO",
]

SECTOR_ETF_UNIVERSE = list(SectorRotationConfig().sector_etfs.keys()) + [
    "SPY", "QQQ", "IWM", "DIA", "EEM", "FXI",  # China ETF
    "KWEB",  # China internet
    "GLD", "SLV", "USO",  # Commodities
    "TLT", "IEF",  # Bonds
]

FULL_UNIVERSE = US_CORE_UNIVERSE + CHINA_ADR_UNIVERSE

# ============================================================================
# UNIVERSE BUILDER SETTINGS
# ============================================================================
@dataclass
class UniverseConfig:
    """Dynamic universe discovery and filtering parameters."""
    min_market_cap: float = 300_000_000    # $300M minimum market cap
    min_avg_volume: int = 100_000          # 100K shares/day minimum
    min_price: float = 5.0                 # No penny stocks
    max_tickers: int = 3000                # Cap for backtest performance
    refresh_days: int = 7                  # Refresh ticker list weekly
    batch_size: int = 100                  # Download batch size for yfinance
    batch_delay_sec: float = 2.0           # Delay between batches (rate limit)
    # Daily scan pre-filter (fast vectorized check before full scan)
    pre_filter_above_sma: int = 200        # Must be above N-day SMA
    pre_filter_min_adr: float = 2.0        # ADR(20) must exceed this %


UNIVERSE = UniverseConfig()

# ============================================================================
# MACRO ENGINE SETTINGS (forward-looking regime detection)
# ============================================================================
@dataclass
class MacroEngineConfig:
    """Forward-looking macro regime detection using free Yahoo Finance data."""
    enabled: bool = True
    max_boost: float = 1.15       # Never more than +15% sizing
    max_penalty: float = 0.85     # Never more than -15% sizing
    # Weights for composite score
    yield_curve_weight: float = 0.30
    rate_direction_weight: float = 0.25
    copper_gold_weight: float = 0.20
    dollar_weight: float = 0.15
    vix_weight: float = 0.10
    # Earnings engine
    earnings_enabled: bool = True
    earnings_fetch_delay: float = 1.0  # Delay between yfinance calls


MACRO_ENGINE = MacroEngineConfig()

# ============================================================================
# BACKTEST SETTINGS
# ============================================================================
BACKTEST_START = "2014-01-01"   # Covers C1, C2, C3, C4 cycles
BACKTEST_END = "2026-02-20"
BENCHMARK_TICKER = "SPY"

# ============================================================================
# LONGBRIDGE API (placeholder - user needs to fill in)
# ============================================================================
@dataclass
class LongbridgeConfig:
    app_key: str = ""
    app_secret: str = ""
    access_token: str = ""
    # Longbridge supports: US, HK, SG markets
    market: str = "US"


LONGBRIDGE = LongbridgeConfig()
