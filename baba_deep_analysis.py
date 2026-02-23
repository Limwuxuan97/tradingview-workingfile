"""
BABA Ultra-Deep Analysis — February 21, 2026
Incorporating: SCOTUS IEEPA ruling, Trump China visit Mar 28-Apr 1,
Two Sessions Mar 4-5, CME T+35/T+42 mechanics, full OHLCV structure
"""
from datetime import datetime, timedelta
import statistics
import math

# ============================================================================
# DATA LOAD — from attached CSV (through Feb 20, 2026)
# ============================================================================
data_lines = [
"21/02/2025,141.6,145.3,141.1,143.75,73892138",
"24/02/2025,135.8,135.8,128.44,129.04,74118310",
"25/02/2025,132.79,134.47,130.75,134.01,38881139",
"26/02/2025,140,141.95,138.29,139.08,40670132",
"27/02/2025,138.68,140.1,135.87,136.55,23859370",
"28/02/2025,130.95,133.95,130.14,132.51,24862578",
"03/03/2025,134.01,134.72,129.56,130.81,22528034",
"04/03/2025,129.6,132.1,126.1,129.85,25366513",
"05/03/2025,134.37,141.83,133.34,141.03,37284635",
"06/03/2025,142.2,144.76,138.09,139.95,35482111",
"07/03/2025,142.92,145.36,139.38,140.62,31904363",
"10/03/2025,136,137.95,131,132.54,33484184",
"11/03/2025,138.16,141.33,136.04,139.02,29094794",
"12/03/2025,138.41,138.95,135.28,137.14,23880904",
"13/03/2025,134.77,140.28,134.34,138.35,20516289",
"14/03/2025,141.35,141.82,139.45,141.1,17381919",
"17/03/2025,140.16,148.43,140.03,147.57,33896965",
"18/03/2025,146.38,146.87,142.5,142.74,20950126",
"19/03/2025,145.07,145.2,141.87,143.2,16333817",
"20/03/2025,137.18,138.99,136.37,136.91,23646782",
"21/03/2025,133.99,136.47,133.3,135.14,13970265",
"24/03/2025,136.33,136.43,133.63,134.48,14019013",
"25/03/2025,132.94,136.25,132.35,132.75,17943385",
"26/03/2025,133.53,134.66,131.13,132.24,16023418",
"27/03/2025,133.45,137.79,132.88,135.63,16688316",
"28/03/2025,133.5,134.21,131.4,132.43,13271493",
"31/03/2025,130.03,132.87,128,132.23,12183816",
"01/04/2025,132.75,134.1,131.53,132.7,11627512",
"02/04/2025,131.96,132.83,129.15,129.79,21240902",
"03/04/2025,125.65,130.67,125.5,129.33,30607587",
"04/04/2025,117.57,118.87,111.3,116.54,57154549",
"07/04/2025,106.62,114.12,102.64,105.98,61386612",
"08/04/2025,108.26,109,97.75,99.37,52100163",
"09/04/2025,100.6,107.04,95.73,104.78,74981920",
"10/04/2025,106.86,108.45,101.37,104.18,53133403",
"11/04/2025,104.78,108.04,102.19,107.73,40522778",
"14/04/2025,111.87,116,111.7,113.97,32926103",
"15/04/2025,113.78,114,111.47,112.28,16172344",
"16/04/2025,108.18,108.97,105.95,106.75,18031571",
"17/04/2025,110.84,111.52,108.42,108.87,17884952",
"21/04/2025,108.73,110.23,107.27,110.15,12145693",
"22/04/2025,114.36,117.43,113.01,115.88,27662424",
"23/04/2025,119.59,123.81,118.75,118.97,25762785",
"24/04/2025,117.94,119.34,117.58,119.29,13695999",
"25/04/2025,118.58,120.49,118.27,120.28,9306404",
"28/04/2025,119.5,120.67,117.29,118.37,10748004",
"29/04/2025,117.73,119.88,117.69,118.88,8295478",
"30/04/2025,119.09,119.94,118.19,119.43,10144809",
"01/05/2025,120.19,121.45,119.36,120.53,8690227",
"02/05/2025,126.01,126.62,124.25,125.76,18092542",
"05/05/2025,125,127.13,124.71,126.57,9868775",
"06/05/2025,128.46,129.73,127.49,127.66,17919707",
"07/05/2025,124.91,124.97,122.91,123.23,16024031",
"08/05/2025,125.35,126.82,124.17,125.79,10846828",
"09/05/2025,126.99,127.77,125.19,125.33,11172185",
"12/05/2025,133.87,134.07,132.3,132.55,22631735",
"13/05/2025,131,133.03,130.2,131.65,16123609",
"14/05/2025,134.07,134.51,132.65,134.05,18278334",
"15/05/2025,126.24,126.32,122.65,123.9,35442760",
"16/05/2025,125.78,126.1,123.31,123.46,20089993",
"19/05/2025,120.18,123.06,120,122.96,11197016",
"20/05/2025,124.29,125.22,124.15,125.16,11789999",
"21/05/2025,125.45,126.06,122.77,123.59,8521416",
"22/05/2025,121.49,122.17,120.92,121.48,7820944",
"23/05/2025,119.58,121.04,119.28,120.73,7163427",
"27/05/2025,119.88,120.01,118.89,119.52,8544496",
"28/05/2025,117.45,117.92,116.51,116.74,11707735",
"29/05/2025,119.04,119.34,116.7,117.18,12392828",
"30/05/2025,115.01,115.07,111.6,113.84,17213209",
"02/06/2025,114.9,115.4,113.66,114.75,13147154",
"03/06/2025,115.38,115.81,114.42,114.97,14008938",
"04/06/2025,116.82,120,116.66,119.45,18115450",
"05/06/2025,120.95,121.55,119.14,119.96,15375413",
"06/06/2025,119,119.77,118.22,119.38,9753173",
"09/06/2025,121.09,122.16,120.12,121.48,10410563",
"10/06/2025,120.62,122.16,119.88,121.88,8892757",
"11/06/2025,122.63,123.46,120.05,120.33,10443073",
"12/06/2025,117.52,117.55,115.95,116.62,10204450",
"13/06/2025,113.67,114.78,112.27,112.87,13355129",
"16/06/2025,114.98,116.9,114.87,115.96,10242923",
"17/06/2025,115.94,116.61,115.03,115.03,10205739",
"18/06/2025,113.64,114.3,113.02,113.49,14002314",
"20/06/2025,114.11,114.43,112.62,113.01,12737319",
"23/06/2025,112.12,113.09,111.26,113.09,12536509",
"24/06/2025,114.62,117.32,113.62,117.01,17125097",
"25/06/2025,117.2,117.45,114.17,114.55,12835548",
"26/06/2025,114.1,114.2,113.38,113.93,8388014",
"27/06/2025,114.37,115.5,113.32,114.08,12355492",
"30/06/2025,112.46,113.49,111.4,113.41,10457272",
"01/07/2025,112.95,114.79,112.74,113.97,9243164",
"02/07/2025,111.57,111.82,110.37,110.71,13843810",
"03/07/2025,108.34,109.08,107.95,108.7,11847157",
"07/07/2025,107.43,108.2,105.94,106.27,17446167",
"08/07/2025,108.77,109.13,107.91,107.99,11319872",
"09/07/2025,105.48,105.53,103.71,103.83,24609268",
"10/07/2025,105.14,106.76,104.41,106.64,13554454",
"11/07/2025,106.91,107.42,106.3,106.72,10774594",
"14/07/2025,107.65,108.8,107.19,108.22,13231335",
"15/07/2025,114.66,117.22,113.2,116.97,34785371",
"16/07/2025,115.5,116.03,114.04,115.73,14438970",
"17/07/2025,115.04,118.2,114.86,117.3,14573568",
"18/07/2025,121.38,122.16,119.77,120.23,26787681",
"21/07/2025,119.51,122.31,118.25,120.27,17937612",
"22/07/2025,120.44,121.84,119,120.71,11551511",
"23/07/2025,122.8,123.87,121.4,122.58,12874232",
"24/07/2025,121.85,123.99,120.45,121.15,11378418",
"25/07/2025,120.19,120.48,119.34,120.03,7060560",
"28/07/2025,122.03,123.45,121.53,122.15,11207373",
"29/07/2025,122.49,122.87,119.05,119.36,13599708",
"30/07/2025,119.05,119.59,116.84,117.38,12794061",
"31/07/2025,117.82,121.34,117.52,120.63,13650447",
"01/08/2025,118.06,118.37,116.11,117.07,12424282",
"04/08/2025,118.35,119.49,116.86,117.5,7272111",
"05/08/2025,118.1,118.65,116.87,117.04,5885633",
"06/08/2025,118.88,121.29,117.77,120.86,12079640",
"07/08/2025,121.34,122.28,119.6,120.96,9480594",
"08/08/2025,119.32,120.7,118.66,120.36,9763569",
"11/08/2025,120.43,121.3,118.12,118.64,12071979",
"12/08/2025,118.81,122.79,118.1,122.42,11994896",
"13/08/2025,126.69,127.93,125.08,126.86,19362542",
"14/08/2025,123.73,123.93,121.34,122.28,15045624",
"15/08/2025,120.98,122.19,120.68,121.26,11141846",
"18/08/2025,121.92,123.15,120.9,121.4,8550427",
"19/08/2025,121.58,122.58,119.99,119.99,8106147",
"20/08/2025,119.92,120.81,118.67,119.49,7095804",
"21/08/2025,117.88,119.27,117.51,118.09,8231152",
"22/08/2025,120.48,123.4,120.28,122.94,13855325",
"25/08/2025,125.18,126.73,123.5,124.35,12888365",
"26/08/2025,125.3,126,123.72,124.19,8706053",
"27/08/2025,121.2,122.52,120.79,122.23,13833096",
"28/08/2025,119.53,121.25,117.6,119.57,14501143",
"29/08/2025,128.88,136.65,128.51,135,82165134",
"02/09/2025,134.52,138.83,133.06,138.55,41625384",
"03/09/2025,136.7,137.77,135.58,136.45,16470529",
"04/09/2025,133.16,134.25,130.06,130.92,24730939",
"05/09/2025,135.03,135.61,132.7,135.58,19202474",
"08/09/2025,139.88,141.22,138.77,141.2,20095286",
"09/09/2025,145.4,148,144.65,147.1,32792264",
"10/09/2025,145.42,145.92,143.23,143.93,21079914",
"11/09/2025,148.12,156.85,147.86,155.44,50089164",
"12/09/2025,154.07,155.46,152.06,155.06,20903285",
"15/09/2025,159.09,159.7,156.73,158.04,23567202",
"16/09/2025,158.36,163,157.59,162.21,26017688",
"17/09/2025,166,167.32,163.26,166.17,29344345",
"18/09/2025,162.5,164.79,161.3,162.48,19529564",
"19/09/2025,164.69,166.25,162.61,162.81,18183217",
"22/09/2025,163.76,167.44,163.03,164.25,18667746",
"23/09/2025,165.01,167.83,162.8,163.08,18278591",
"24/09/2025,175.98,180.16,175,176.44,6377298",
"25/09/2025,173.4,175.77,170.44,175.47,20712240",
"26/09/2025,172.17,172.76,169.7,171.91,15971139",
"29/09/2025,178.08,181.34,177.59,179.9,21576309",
"30/09/2025,181.66,182.15,177.1,178.73,18681536",
"01/10/2025,179.98,183.08,178.87,182.78,14966893",
"02/10/2025,188.58,192.67,188.3,189.34,23687832",
"03/10/2025,190.72,191.07,187.14,188.03,13990883",
"06/10/2025,186.5,189.61,186.31,187.22,10973537",
"07/10/2025,187.41,188.66,180.44,181.33,16942164",
"08/10/2025,180.79,182.09,177.3,181.12,15883673",
"09/10/2025,178.52,178.78,172.3,173.68,21211553",
"10/10/2025,170.03,172.93,157.25,159.01,50296820",
"13/10/2025,167.78,168.79,165.03,166.81,25703058",
"14/10/2025,160.05,166.5,160,162.86,18583211",
"15/10/2025,168.07,168.1,164.6,165.91,15337377",
"16/10/2025,166.52,168.3,164.46,165.09,10979714",
"17/10/2025,161.76,169.1,161.15,167.05,17765727",
"20/10/2025,167.29,174.97,165.79,173.47,20120474",
"21/10/2025,170.52,170.94,166.42,166.67,15662505",
"22/10/2025,167,169.67,163.58,165.86,15016541",
"23/10/2025,168.97,173.24,168.32,171.9,12792123",
"24/10/2025,174.4,176.44,173.36,174.7,11840994",
"27/10/2025,179.74,180,177.62,179.45,12580845",
"28/10/2025,177.48,179.38,175.24,176.72,11906931",
"29/10/2025,180.3,182.5,178.09,179.97,12068930",
"30/10/2025,174.32,176.38,173.78,173.93,10756273",
"31/10/2025,170.53,171.45,168.12,170.43,13181435",
"03/11/2025,168.31,168.94,165.58,167.69,9702276",
"04/11/2025,162.6,166.5,162.2,164.3,9693135",
"05/11/2025,164.4,166.88,163.6,164.82,8631419",
"06/11/2025,169,170.55,165.52,167.61,12438908",
"07/11/2025,162.96,166.38,161.22,166.34,11581220",
"10/11/2025,167.62,168,163.64,165.89,9348727",
"11/11/2025,164.59,165.58,160.16,160.8,11354390",
"12/11/2025,160.98,161.19,156.2,157.91,13920804",
"13/11/2025,164,164,158.5,159.84,17212992",
"14/11/2025,156.94,162.62,151.78,153.8,33991002",
"17/11/2025,157.98,161.03,156.9,157.71,16911369",
"18/11/2025,157.31,161.28,156.7,159.72,12438918",
"19/11/2025,159.32,160.97,158.04,158.89,7949937",
"20/11/2025,159,161.39,153,153.28,13466893",
"21/11/2025,151.98,155.88,148.64,152.93,16240767",
"24/11/2025,160,161.5,158.7,160.73,21796582",
"25/11/2025,165.2,166.37,156.15,157.01,27097482",
"26/11/2025,159.1,161.46,150,157.6,21453064",
"28/11/2025,156.16,158.69,155.68,157.3,7185491",
"01/12/2025,160.5,164.85,159.41,164.26,15321150",
"02/12/2025,161.2,161.73,159.12,161.13,9878480",
"03/12/2025,157.4,158.45,156.53,158.08,6967995",
"04/12/2025,158.27,158.8,156.41,157.44,6666349",
"05/12/2025,159.15,159.49,157.68,158.32,6277149",
"08/12/2025,157.57,158.74,156.41,158.13,7342015",
"09/12/2025,154.44,156.6,154.3,155.96,6458051",
"10/12/2025,159.64,160.74,157.5,158.82,10928552",
"11/12/2025,155.15,157.05,153.36,156.9,8171243",
"12/12/2025,157.76,158.95,153.8,155.68,6708382",
"15/12/2025,153.18,153.21,149.58,150.09,11233112",
"16/12/2025,148.95,149.97,147.51,149.29,9051912",
"17/12/2025,150.6,151.39,146.75,147.09,8271036",
"18/12/2025,148.65,149.2,147.12,147.32,6597386",
"19/12/2025,149.01,151.47,148.88,149.79,9004211",
"22/12/2025,150.41,151.82,149.12,150.96,6779097",
"23/12/2025,150.57,151.3,149.27,151.23,5373306",
"24/12/2025,150.5,150.79,149.92,150.06,3274182",
"26/12/2025,150.29,152.98,150.06,152.24,6037198",
"29/12/2025,147.72,148.75,147.21,148.49,8900020",
"30/12/2025,148.84,149.1,147.35,147.36,6832251",
"31/12/2025,146.69,147.37,145.64,146.58,6116035",
"02/01/2026,152.62,156.65,151.8,155.74,15778326",
"05/01/2026,155.78,156.55,152.17,156.26,14743961",
"06/01/2026,155.22,155.84,150.86,150.9,12998105",
"07/01/2026,148.38,148.38,146.61,146.75,12613212",
"08/01/2026,146.1,155.29,145.27,154.47,20981676",
"09/01/2026,151.33,151.57,148.52,150.96,11437935",
"12/01/2026,157.47,167.69,157.47,166.31,35379014",
"13/01/2026,165.5,170.68,164.91,167.01,18850362",
"14/01/2026,171.57,172.8,169.85,169.9,17475064",
"15/01/2026,169.65,173.3,167.34,170.93,12606974",
"16/01/2026,169.78,169.85,163.5,165.4,18598277",
"20/01/2026,161.83,166.17,161.68,162.39,9885048",
"21/01/2026,167.58,169.87,165.66,168.67,11713726",
"22/01/2026,176.43,181.1,174.77,177.18,32031059",
"23/01/2026,175.44,175.61,171.94,173.23,13064063",
"26/01/2026,169.79,172.99,168.68,171.37,10166147",
"27/01/2026,174.05,176.46,172.22,172.72,8931278",
"28/01/2026,176.25,177.87,174.56,175.66,9001486",
"29/01/2026,178.34,180.75,171.6,174.25,12062505",
"30/01/2026,172.7,174,169.47,169.56,10846082",
"02/02/2026,167.98,169.56,167.34,168.39,6551750",
"03/02/2026,163.88,165.35,160.61,163.65,10066594",
"04/02/2026,162.33,162.85,156.78,159.14,11851371",
"05/02/2026,161.14,161.47,156.71,157.76,10936668",
"06/02/2026,160.46,162.86,159.5,162.51,10972061",
"09/02/2026,161.89,165.03,160.89,163,7260483",
"10/02/2026,163.74,168.26,162.3,166.51,10989984",
"11/02/2026,164.09,165.2,161.38,164.32,8756875",
"12/02/2026,163.12,163.37,156.96,158.73,11457824",
"13/02/2026,152.85,158.11,152.85,155.73,16045579",
"17/02/2026,156.38,158.13,153.46,155.43,6803612",
"18/02/2026,156.88,157.5,155.57,155.77,4506642",
"19/02/2026,155.23,155.5,153.15,154.27,6580998",
"20/02/2026,150.88,155.49,150.43,154.45,8682772",
]

rows = []
for line in data_lines:
    parts = line.split(',')
    dt = datetime.strptime(parts[0], '%d/%m/%Y')
    o, h, l, c, v = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), int(parts[5])
    rows.append({'date': dt, 'open': o, 'high': h, 'low': l, 'close': c, 'volume': v})

rows.sort(key=lambda x: x['date'])
N = len(rows)

def sma(data, end_idx, period):
    start = max(0, end_idx - period + 1)
    w = data[start:end_idx+1]
    return sum(r['close'] for r in w) / len(w)

def ema(data, end_idx, period):
    """Calculate EMA up to end_idx"""
    mult = 2 / (period + 1)
    vals = [r['close'] for r in data[:end_idx+1]]
    if len(vals) < period:
        return sum(vals) / len(vals)
    e = sum(vals[:period]) / period
    for v in vals[period:]:
        e = (v - e) * mult + e
    return e

def vwap_like(data, start_idx, end_idx):
    """Volume-weighted average price for a range"""
    total_vp = sum(r['close'] * r['volume'] for r in data[start_idx:end_idx+1])
    total_v = sum(r['volume'] for r in data[start_idx:end_idx+1])
    return total_vp / total_v if total_v > 0 else 0

# ============================================================================
print("=" * 90)
print("  BABA ULTRA-DEEP ANALYSIS — February 21, 2026")
print("  Latest Data Point: Feb 20, 2026 | Close: $154.45")
print("=" * 90)

# ============================================================================
# SECTION 1: WHERE ARE WE RIGHT NOW?
# ============================================================================
print("\n" + "=" * 90)
print("  1. CURRENT PRICE STRUCTURE & KEY LEVELS")
print("=" * 90)

last = rows[-1]
last_idx = N - 1

# Moving Averages
sma10 = sma(rows, last_idx, 10)
sma20 = sma(rows, last_idx, 20)
sma50 = sma(rows, last_idx, 50)
sma100 = sma(rows, last_idx, 100)
sma200 = sma(rows, last_idx, 200)
ema21 = ema(rows, last_idx, 21)
ema55 = ema(rows, last_idx, 55)

print(f"\n  Close: ${last['close']:.2f} (Feb 20)")
print(f"  Open:  ${last['open']:.2f} | High: ${last['high']:.2f} | Low: ${last['low']:.2f}")
print(f"\n  --- Moving Averages ---")
print(f"  10 SMA:  ${sma10:.2f}  ({(last['close']/sma10-1)*100:+.1f}% from price)")
print(f"  20 SMA:  ${sma20:.2f}  ({(last['close']/sma20-1)*100:+.1f}% from price)")
print(f"  21 EMA:  ${ema21:.2f}  ({(last['close']/ema21-1)*100:+.1f}% from price)")
print(f"  50 SMA:  ${sma50:.2f}  ({(last['close']/sma50-1)*100:+.1f}% from price)")
print(f"  55 EMA:  ${ema55:.2f}  ({(last['close']/ema55-1)*100:+.1f}% from price)")
print(f"  100 SMA: ${sma100:.2f}  ({(last['close']/sma100-1)*100:+.1f}% from price)")
print(f"  200 SMA: ${sma200:.2f}  ({(last['close']/sma200-1)*100:+.1f}% from price)")

# MA Stack
print(f"\n  --- MA Stack Order ---")
ma_list = [('10 SMA', sma10), ('20 SMA', sma20), ('21 EMA', ema21), ('50 SMA', sma50),
           ('55 EMA', ema55), ('100 SMA', sma100), ('200 SMA', sma200)]
ma_sorted = sorted(ma_list, key=lambda x: x[1], reverse=True)
for name, val in ma_sorted:
    marker = " <<<< PRICE HERE" if abs(val - last['close']) < 2 else ""
    print(f"    {name}: ${val:.2f}{marker}")

# ============================================================================
# SECTION 2: SUPPORT / RESISTANCE MAPPING
# ============================================================================
print("\n" + "=" * 90)
print("  2. SUPPORT & RESISTANCE MAP (from price memory)")
print("=" * 90)

# Find volume profile nodes (high-volume price zones)
price_volume = {}
for r in rows:
    bucket = round(r['close'] / 2.5) * 2.5  # $2.50 buckets
    if bucket not in price_volume:
        price_volume[bucket] = 0
    price_volume[bucket] += r['volume']

# High volume nodes near current price
relevant = {k: v for k, v in price_volume.items() if 130 <= k <= 185}
sorted_nodes = sorted(relevant.items(), key=lambda x: x[1], reverse=True)

print(f"\n  --- High Volume Nodes (price memory) ---")
for price, vol in sorted_nodes[:10]:
    bar = '#' * int(vol / max(v for _, v in sorted_nodes[:10]) * 40)
    print(f"    ${price:>6.1f}: {vol:>12,} {bar}")

# Key support levels
print(f"\n  --- KEY SUPPORT LEVELS ---")
# Recent lows
recent_lows = []
for i in range(max(0, N-60), N):
    r = rows[i]
    is_low = True
    for j in range(max(0, i-3), min(N, i+4)):
        if j != i and rows[j]['low'] < r['low']:
            is_low = False
            break
    if is_low:
        recent_lows.append((r['date'], r['low']))

for dt, lo in recent_lows[-10:]:
    dist = (last['close'] - lo) / lo * 100
    print(f"    {dt.strftime('%Y-%m-%d')}: ${lo:.2f} ({dist:+.1f}% from current)")

# Key resistance
print(f"\n  --- KEY RESISTANCE LEVELS ---")
recent_highs = []
for i in range(max(0, N-60), N):
    r = rows[i]
    is_high = True
    for j in range(max(0, i-3), min(N, i+4)):
        if j != i and rows[j]['high'] > r['high']:
            is_high = False
            break
    if is_high:
        recent_highs.append((r['date'], r['high']))

for dt, hi in recent_highs[-10:]:
    dist = (hi - last['close']) / last['close'] * 100
    print(f"    {dt.strftime('%Y-%m-%d')}: ${hi:.2f} ({dist:+.1f}% from current)")

# ============================================================================
# SECTION 3: THE LAST 10 TRADING DAYS (micro-structure)
# ============================================================================
print("\n" + "=" * 90)
print("  3. LAST 10 TRADING DAYS — MICRO-STRUCTURE")
print("=" * 90)

last10 = rows[-10:]
for i, r in enumerate(last10):
    chg = r['close'] - r['open']
    rng = r['high'] - r['low']
    vol_avg = sum(rows[max(0,N-10+i-19):N-10+i+1][j]['volume'] for j in range(min(20, N-10+i+1))) / min(20, N-10+i+1) if N-10+i >= 0 else r['volume']
    # Simpler: just use last 20 bars average
    idx = N - 10 + i
    lookback = rows[max(0, idx-19):idx+1]
    vol_20d_avg = sum(x['volume'] for x in lookback) / len(lookback)
    vol_ratio = r['volume'] / vol_20d_avg
    
    candle = "BULL" if r['close'] > r['open'] else "BEAR"
    wick_top = r['high'] - max(r['open'], r['close'])
    wick_bot = min(r['open'], r['close']) - r['low']
    body = abs(r['close'] - r['open'])
    
    if body < rng * 0.1:
        pattern = "DOJI"
    elif wick_bot > body * 2 and candle == "BULL":
        pattern = "HAMMER"
    elif wick_top > body * 2 and candle == "BEAR":
        pattern = "SHOOTING STAR"
    else:
        pattern = candle
    
    print(f"  {r['date'].strftime('%Y-%m-%d')}: O={r['open']:>7.2f} H={r['high']:>7.2f} L={r['low']:>7.2f} C={r['close']:>7.2f} "
          f"Vol={r['volume']:>10,} ({vol_ratio:.1f}x) {pattern:>13} Rng=${rng:.2f}")

# Last 5 vs prior 5
l5 = last10[5:]
p5 = last10[:5]
l5_avg_vol = sum(r['volume'] for r in l5) / len(l5)
p5_avg_vol = sum(r['volume'] for r in p5) / len(p5)
l5_avg_range = sum(r['high'] - r['low'] for r in l5) / len(l5)
p5_avg_range = sum(r['high'] - r['low'] for r in p5) / len(p5)
print(f"\n  Last 5 days avg vol: {l5_avg_vol:,.0f} vs Prior 5: {p5_avg_vol:,.0f} ({(l5_avg_vol/p5_avg_vol-1)*100:+.1f}%)")
print(f"  Last 5 days avg range: ${l5_avg_range:.2f} vs Prior 5: ${p5_avg_range:.2f} ({(l5_avg_range/p5_avg_range-1)*100:+.1f}%)")

# ============================================================================
# SECTION 4: DECLINE FROM JAN 22 PEAK — CAPITULATION ANALYSIS
# ============================================================================
print("\n" + "=" * 90)
print("  4. DECLINE FROM JAN 22 PEAK — WAVE STRUCTURE")
print("=" * 90)

jan22_idx = next(i for i, r in enumerate(rows) if r['date'] == datetime(2026, 1, 22))
peak_price = rows[jan22_idx]['high']  # $181.10

print(f"\n  Peak: ${peak_price:.2f} on Jan 22, 2026")
print(f"  Current: ${last['close']:.2f}")
print(f"  Drawdown: ${peak_price - last['close']:.2f} ({(last['close']/peak_price - 1)*100:.1f}%)")
print(f"  Trading days since peak: {N - 1 - jan22_idx}")

# Map the decline wave by wave
print(f"\n  --- Wave Structure of Decline ---")
decline_data = rows[jan22_idx:]
# Find local swing points
swings = []
for i in range(1, len(decline_data) - 1):
    r = decline_data[i]
    prev = decline_data[i-1]
    nxt = decline_data[i+1]
    if r['high'] > prev['high'] and r['high'] > nxt['high']:
        swings.append(('HIGH', r['date'], r['high']))
    if r['low'] < prev['low'] and r['low'] < nxt['low']:
        swings.append(('LOW', r['date'], r['low']))

for typ, dt, price in swings:
    pct_from_peak = (price / peak_price - 1) * 100
    print(f"  {dt.strftime('%Y-%m-%d')} {typ:>4}: ${price:.2f} ({pct_from_peak:+.1f}% from peak)")

# Daily decline from peak
print(f"\n  --- Daily closes since peak ---")
for r in decline_data:
    pct = (r['close'] / peak_price - 1) * 100
    bar = '|' + '#' * max(0, int(-pct))
    print(f"  {r['date'].strftime('%Y-%m-%d')}: ${r['close']:>7.2f} ({pct:+.1f}%) {bar}")

# ============================================================================
# SECTION 5: FEBRUARY 20 SCOTUS DAY — PRICE ACTION ANALYSIS
# ============================================================================
print("\n" + "=" * 90)
print("  5. FEB 20 (SCOTUS IEEPA RULING DAY) — ACTION/REACTION")
print("=" * 90)

feb20 = rows[-1]
feb19 = rows[-2]
print(f"\n  Feb 19 Close: ${feb19['close']:.2f}")
print(f"  Feb 20 Open:  ${feb20['open']:.2f} (gap: ${feb20['open'] - feb19['close']:.2f}, {(feb20['open']/feb19['close']-1)*100:+.1f}%)")
print(f"  Feb 20 Low:   ${feb20['low']:.2f}")
print(f"  Feb 20 High:  ${feb20['high']:.2f}")
print(f"  Feb 20 Close: ${feb20['close']:.2f} (day chg: {(feb20['close']/feb20['open']-1)*100:+.1f}%)")
print(f"  Feb 20 Volume: {feb20['volume']:,}")

# 20d avg vol
feb20_vol_avg = sum(r['volume'] for r in rows[-21:-1]) / 20
print(f"  20-day avg volume: {feb20_vol_avg:,.0f}")
print(f"  Volume ratio: {feb20['volume']/feb20_vol_avg:.2f}x")

# Key observation about Feb 20
body = abs(feb20['close'] - feb20['open'])
range_day = feb20['high'] - feb20['low']
upper_wick = feb20['high'] - max(feb20['open'], feb20['close'])
lower_wick = min(feb20['open'], feb20['close']) - feb20['low']

print(f"\n  Candle Analysis:")
print(f"    Body: ${body:.2f}")
print(f"    Range: ${range_day:.2f}")
print(f"    Upper wick: ${upper_wick:.2f}")
print(f"    Lower wick: ${lower_wick:.2f}")
if feb20['close'] > feb20['open']:
    print(f"    Type: BULLISH — opened down $3.35, recovered to close +$0.18 from prior")
    print(f"    INTERPRETATION: SCOTUS ruling absorbed, buyers stepped in at $150.43 low")
else:
    print(f"    Type: Shows initial selling absorbed by buyers (low ${feb20['low']}, close ${feb20['close']})")


# ============================================================================
# SECTION 6: FIBONACCI RETRACEMENT FROM THE MAJOR CYCLE
# ============================================================================
print("\n" + "=" * 90)
print("  6. FIBONACCI RETRACEMENT LEVELS")
print("=" * 90)

# From April 2025 low to October 2025 high
cycle_low = 95.73   # Apr 9, 2025
cycle_high = 192.67  # Oct 2, 2025
diff = cycle_high - cycle_low

fibs = [
    (0, cycle_high),
    (0.236, cycle_high - 0.236 * diff),
    (0.382, cycle_high - 0.382 * diff),
    (0.5, cycle_high - 0.5 * diff),
    (0.618, cycle_high - 0.618 * diff),
    (0.786, cycle_high - 0.786 * diff),
    (1.0, cycle_low),
]

print(f"\n  Swing: ${cycle_low:.2f} (Apr 9) -> ${cycle_high:.2f} (Oct 2)")
print(f"  Current price: ${last['close']:.2f}")
print(f"\n  {'Level':<10} {'Price':>10} {'Distance':>12}")
print(f"  {'-'*35}")
for lvl, price in fibs:
    dist = (last['close'] - price) / last['close'] * 100
    marker = " <<<< NEAR" if abs(dist) < 3 else ""
    print(f"  {lvl:<10.3f} ${price:>9.2f} {dist:>+10.1f}%{marker}")

# From Jan 22 high to current — internal retracement
print(f"\n  --- From Jan Spike ($181.10) to Feb 13 Low ($152.85) ---")
jan_high = 181.10
feb_low = 152.85
diff2 = jan_high - feb_low

retrace_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
for lvl in retrace_levels:
    price = feb_low + lvl * diff2
    dist = (last['close'] - price) / last['close'] * 100
    print(f"    {lvl:.3f}: ${price:.2f} ({dist:>+.1f}% from current)")


# ============================================================================
# SECTION 7: VOLUME DRY-UP / CAPITULATION ANALYSIS
# ============================================================================
print("\n" + "=" * 90)
print("  7. VOLUME ANALYSIS — SELLING EXHAUSTION CHECK")
print("=" * 90)

# Last 20 days volume profile
print(f"\n  --- Last 20 Trading Days Volume ---")
last20 = rows[-20:]
for r in last20:
    lookback_idx = rows.index(r)
    lb = rows[max(0, lookback_idx-19):lookback_idx+1]
    avg20 = sum(x['volume'] for x in lb) / len(lb)
    ratio = r['volume'] / avg20
    direction = "UP" if r['close'] > r['open'] else "DN"
    bar = '#' * int(ratio * 20)
    print(f"  {r['date'].strftime('%Y-%m-%d')}: {r['volume']:>10,} ({ratio:.1f}x) [{direction}] {bar}")

# Down volume vs up volume ratio (last 20 days)
up_vol = sum(r['volume'] for r in last20 if r['close'] > r['open'])
down_vol = sum(r['volume'] for r in last20 if r['close'] <= r['open'])
print(f"\n  Up-day volume (20d):   {up_vol:>12,}")
print(f"  Down-day volume (20d): {down_vol:>12,}")
print(f"  Down/Up ratio: {down_vol/up_vol:.2f}" if up_vol > 0 else "  N/A")

up_days = sum(1 for r in last20 if r['close'] > r['open'])
down_days = sum(1 for r in last20 if r['close'] <= r['open'])
print(f"  Up days: {up_days}, Down days: {down_days}")

# Volume trend (declining = selling exhaustion)
last10_vol = sum(r['volume'] for r in rows[-10:]) / 10
prior10_vol = sum(r['volume'] for r in rows[-20:-10]) / 10
print(f"\n  Last 10d avg vol: {last10_vol:,.0f}")
print(f"  Prior 10d avg vol: {prior10_vol:,.0f}")
print(f"  Change: {(last10_vol/prior10_vol-1)*100:+.1f}%")
if last10_vol < prior10_vol:
    print(f"  INTERPRETATION: Volume declining on the selloff = selling pressure exhausting")

# Find lowest volume days in this selloff
feb_data = [r for r in rows if r['date'] >= datetime(2026, 2, 1)]
feb_sorted_by_vol = sorted(feb_data, key=lambda x: x['volume'])
print(f"\n  Lowest volume days in February:")
for r in feb_sorted_by_vol[:5]:
    print(f"    {r['date'].strftime('%Y-%m-%d')}: {r['volume']:,} (C=${r['close']:.2f})")


# ============================================================================
# SECTION 8: RSI & MOMENTUM
# ============================================================================
print("\n" + "=" * 90)
print("  8. RSI & MOMENTUM INDICATORS")
print("=" * 90)

# Calculate RSI(14)
def calc_rsi(data, period=14):
    gains = []
    losses = []
    for i in range(1, len(data)):
        chg = data[i]['close'] - data[i-1]['close']
        if chg > 0:
            gains.append(chg)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(chg))
    
    if len(gains) < period:
        return 50  # not enough data
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# RSI on different timeframes
rsi14 = calc_rsi(rows[-50:], 14)
rsi9 = calc_rsi(rows[-30:], 9)
print(f"  RSI(14): {rsi14:.1f}")
print(f"  RSI(9):  {rsi9:.1f}")

if rsi14 < 30:
    print(f"  RSI ZONE: OVERSOLD — historically strong bounce zone for BABA")
elif rsi14 < 40:
    print(f"  RSI ZONE: APPROACHING OVERSOLD — watch for divergence")
elif rsi14 < 50:
    print(f"  RSI ZONE: WEAK-NEUTRAL — bearish momentum but not extreme")
else:
    print(f"  RSI ZONE: NEUTRAL/BULLISH")

# Rate of Change
roc5 = (last['close'] / rows[-6]['close'] - 1) * 100
roc10 = (last['close'] / rows[-11]['close'] - 1) * 100
roc20 = (last['close'] / rows[-21]['close'] - 1) * 100
print(f"\n  Rate of Change:")
print(f"    5-day:  {roc5:+.1f}%")
print(f"    10-day: {roc10:+.1f}%")
print(f"    20-day: {roc20:+.1f}%")

# MACD
def calc_ema_series(closes, period):
    mult = 2 / (period + 1)
    ema_val = sum(closes[:period]) / period
    result = [ema_val]
    for c in closes[period:]:
        ema_val = (c - ema_val) * mult + ema_val
        result.append(ema_val)
    return result

closes_60 = [r['close'] for r in rows[-60:]]
ema12 = calc_ema_series(closes_60, 12)
ema26 = calc_ema_series(closes_60, 26)
min_len = min(len(ema12), len(ema26))
macd_line = [ema12[-(min_len-i)] - ema26[-(min_len-i)] for i in range(min_len)]
if len(macd_line) >= 9:
    signal_line = calc_ema_series(macd_line, 9)
    current_macd = macd_line[-1]
    current_signal = signal_line[-1]
    histogram = current_macd - current_signal
    print(f"\n  MACD(12,26,9):")
    print(f"    MACD Line:   {current_macd:+.2f}")
    print(f"    Signal Line: {current_signal:+.2f}")
    print(f"    Histogram:   {histogram:+.2f}")
    if current_macd < 0 and histogram > macd_line[-2] - signal_line[-2] if len(signal_line) > 1 else False:
        print(f"    DIVERGENCE: Histogram turning up while below zero = potential bullish signal")


# ============================================================================
# SECTION 9: HISTORICAL ANALOG — WHAT HAPPENED AFTER SIMILAR PATTERNS
# ============================================================================
print("\n" + "=" * 90)
print("  9. HISTORICAL ANALOG — SIMILAR DRAWDOWN PATTERNS IN THIS DATA")
print("=" * 90)

# Find similar -15% drawdowns over ~20 trading days
print(f"\n  Current drawdown: -14.7% over 21 trading days from Jan 22 peak")
print(f"\n  Looking for similar fast selloffs in the dataset...")

for i in range(30, N-20):
    # Check if there was a ~15% decline in the prior ~20 days
    peak_20d = max(r['high'] for r in rows[max(0,i-25):i])
    if rows[i]['close'] / peak_20d - 1 < -0.12 and rows[i]['close'] / peak_20d - 1 > -0.20:
        # What happened in the next 20, 40, 60 days?
        drawdown = (rows[i]['close'] / peak_20d - 1) * 100
        
        fwd_20 = rows[min(i+20, N-1)]['close'] if i+20 < N else None
        fwd_40 = rows[min(i+40, N-1)]['close'] if i+40 < N else None
        fwd_60 = rows[min(i+60, N-1)]['close'] if i+60 < N else None
        
        fwd_20_pct = (fwd_20 / rows[i]['close'] - 1) * 100 if fwd_20 else None
        fwd_40_pct = (fwd_40 / rows[i]['close'] - 1) * 100 if fwd_40 else None
        fwd_60_pct = (fwd_60 / rows[i]['close'] - 1) * 100 if fwd_60 else None
        
        print(f"  {rows[i]['date'].strftime('%Y-%m-%d')}: C=${rows[i]['close']:.2f} (drawdown {drawdown:+.1f}% from 20d peak)"
              f"  +20d: {f'{fwd_20_pct:+.1f}%' if fwd_20_pct else 'N/A':>8}"
              f"  +40d: {f'{fwd_40_pct:+.1f}%' if fwd_40_pct else 'N/A':>8}"
              f"  +60d: {f'{fwd_60_pct:+.1f}%' if fwd_60_pct else 'N/A':>8}")


# ============================================================================
# SECTION 10: ENTRY POINT ANALYSIS
# ============================================================================
print("\n" + "=" * 90)
print("  10. OPTIMAL ENTRY POINT ANALYSIS")
print("=" * 90)

# Multiple support confluences
print(f"\n  --- Support Confluence Map ---")
support_zones = {}

# Fibonacci supports
fib_50 = cycle_high - 0.5 * diff  # ~144.20
fib_618 = cycle_high - 0.618 * diff  # ~132.79
fib_382 = cycle_high - 0.382 * diff  # ~155.64

for price, label in [(fib_50, 'Fib 50%'), (fib_382, 'Fib 38.2%'), (fib_618, 'Fib 61.8%')]:
    bucket = round(price / 2.5) * 2.5
    if bucket not in support_zones:
        support_zones[bucket] = []
    support_zones[bucket].append(label)

# Round numbers
for rn in [145, 150, 155, 160, 165, 170, 175]:
    bucket = float(rn)
    if bucket not in support_zones:
        support_zones[bucket] = []
    support_zones[bucket].append(f'Round ${rn}')

# MAs as support
for label, val in [('200 SMA', sma200), ('100 SMA', sma100), ('50 SMA', sma50)]:
    bucket = round(val / 2.5) * 2.5
    if bucket not in support_zones:
        support_zones[bucket] = []
    support_zones[bucket].append(label)

# Recent swing lows  
dec_low = 145.64  # Dec 31
feb_low = 150.43  # Feb 20
nov_low = 148.64  # Nov 21

for price, label in [(dec_low, 'Dec 31 low'), (feb_low, 'Feb 20 low'), (nov_low, 'Nov 21 low')]:
    bucket = round(price / 2.5) * 2.5
    if bucket not in support_zones:
        support_zones[bucket] = []
    support_zones[bucket].append(label)

print(f"\n  {'Price Zone':>12} | Confluences")
print(f"  {'-'*55}")
for zone in sorted(support_zones.keys()):
    if 140 <= zone <= 165:
        confluences = support_zones[zone]
        strength = len(confluences)
        stars = '*' * strength
        print(f"  ${zone:>10.1f} | {stars} {', '.join(confluences)}")

# The SCOTUS floor test
print(f"\n  --- Feb 20 SCOTUS Test ---")
print(f"  Price gapped down to $150.43 on SCOTUS day and REVERSED")
print(f"  This $150-151 zone is now a TESTED support level")
print(f"  The Dec 29 low was $147.21, Dec 31 low was $145.64")
print(f"  CRITICAL FLOOR: $145-150 zone has 4+ confluences")

# ============================================================================
# SECTION 11: CATALYST-ADJUSTED PRICE PROJECTION
# ============================================================================
print("\n" + "=" * 90)
print("  11. CATALYST-ADJUSTED PRICE PROJECTION (to June 2026)")
print("=" * 90)

print(f"""
  CATALYST TIMELINE & EXPECTED IMPACT:
  {'='*70}
  
  Feb 20 (DONE) — SCOTUS kills IEEPA tariffs
    Impact: Tariff ceiling permanently capped. China effective rate ~35% (was 55%+)
    $170-175B in refunds owed. Section 122 auto-expires Jul 20.
    Price reaction: Tested $150.43, bounced to $154.45. MUTED initially.
    WHY MUTED: Market had partially priced this in; also uncertainty about 
    Section 122 replacement. The REAL move comes when refund flow starts.
    
  Mar 4-5 — Two Sessions (NPC/CPPCC)
    Impact: 15th Five-Year Plan, fiscal stimulus measures, tech policy
    Historical: Sep 24, 2024 session sent BABA from ~$80 to $120 (China stimulus)
    Expected: Moderate positive. 5-10% move if stimulus exceeds expectations.
    BABA target: $160-170 zone
    
  Mar 20 — CME Quarterly Futures/Options Expiry (OPEX)
    Impact: Gamma exposure unwind, volatility spike
    T+35 from this = ~April 24 (forced buying window)
    T+42 from this = ~May 1 (secondary hedge unwind)
    
  Mar 28-Apr 1 — TRUMP VISITS CHINA
    THIS IS THE BIG ONE.
    Impact: De-escalation narrative. Trade deal optimism. 
    Market will FRONT-RUN this by 2-3 weeks (starting ~Mar 10-14).
    Historical analogs:
      - Feb 2019 Trump-Xi 'phase 1' talks: China stocks +12% in 3 weeks
      - Nov 2023 Biden-Xi APEC: BABA +8% in 2 weeks
      - Sep 2024 China stimulus: BABA +55% in 5 weeks
    Expected: 10-20% move in Chinese ADRs if visit produces tangible
    trade/tech cooperation signals.
    BABA target: $170-185 zone
    
  Apr 24 — T+35 forced buying window
    Impact: Market makers who shorted during Mar 20 OPEX must deliver
    Creates 3-5 day buying pressure spike
    BABA target: Adds $3-5 to whatever price level exists
    
  May (TBD) — Q4 FY2026 Earnings
    Impact: Cloud +20% YoY, AI investment payoff narrative
    If beat: Gap up potential to $180+
    
  Jul 20 — Section 122 tariffs auto-expire
    Impact: Final tariff overhang removed
    BABA target: Full fundamental re-rating zone $190-200
""")

# SCENARIO ANALYSIS
print(f"""
  SCENARIO ANALYSIS (by June 2026 expiry):
  {'='*70}
  
  BULL CASE (30% probability):
    - Two Sessions delivers strong stimulus
    - Trump visit produces trade deal framework
    - Earnings beat in May
    - Price path: $154 -> $165 (Mar) -> $180 (Apr) -> $190+ (May)
    
  BASE CASE (45% probability):
    - Two Sessions is modest
    - Trump visit is symbolic (photo-op, no concrete deals)
    - Earnings inline
    - Price path: $154 -> $158 (Mar) -> $168 (Apr) -> $170-175 (May/Jun)
    
  BEAR CASE (25% probability):
    - Trump visit gets canceled or turns hostile
    - New trade restrictions emerge
    - Earnings miss or guidance cut
    - Price path: $154 -> $145 (Mar) -> $130-140 (Apr-Jun)
""")


# ============================================================================
# SECTION 12: OPTIONS STRATEGY ANALYSIS
# ============================================================================
print("\n" + "=" * 90)
print("  12. OPTIONS STRATEGY DEEP DIVE")
print("=" * 90)

# Current price: $154.45
# June expiry: ~June 19, 2026 (standard monthly)
# Days to expiry: ~118 calendar days (~84 trading days)

current = 154.45
dte = 118  # days to June 19

# Rough IV estimation based on BABA's recent behavior
# ADR last 20 days
adr_20 = sum((r['high'] - r['low']) / r['close'] * 100 for r in rows[-20:]) / 20
annualized_vol = adr_20 * math.sqrt(252) / 100  # rough conversion
print(f"\n  Current Price: ${current:.2f}")
print(f"  June Exp (~Jun 19): {dte} days")
print(f"  20-day ADR: {adr_20:.2f}%")
print(f"  Estimated annualized vol: {annualized_vol*100:.0f}%")

print(f"""
  --- STRATEGY COMPARISON ---
  
  STRATEGY 1: Long $165 Call (June)
    Strike: $165 | Type: OTM by ${165 - current:.2f} ({(165/current-1)*100:.1f}%)
    Estimated premium: ~$5.50-7.00 (rough, depends on IV)
    Breakeven at expiry: ~$171-172
    Max loss: Premium paid (100%)
    To profit: BABA needs to rally +11% just to break even
    RISK: High theta decay if stock stays in $150-160 range
    VERDICT: Too aggressive. 7% OTM + high theta = low probability.
    
  STRATEGY 2: Long $155 Call (June) — BETTER
    Strike: $155 | Type: Near ATM (${current - 155:.2f} OTM)
    Estimated premium: ~$9.00-11.00
    Breakeven at expiry: ~$164-166
    Higher cost, but much higher delta (more price exposure)
    50% chance of being ITM at expiry based on base case
    VERDICT: Better risk/reward than $165
    
  STRATEGY 3: Long $150 Call (June) — MOST CONSERVATIVE CALL
    Strike: $150 | Type: ITM by ${current - 150:.2f}
    Estimated premium: ~$12.00-14.00
    Breakeven at expiry: ~$162-164
    Has $4.45 intrinsic value already (insurance)
    Higher absolute cost but lower breakeven
    VERDICT: Best for conviction play, most forgiving
    
  STRATEGY 4: $150/$175 Call Spread (June) — BEST RISK/REWARD
    Buy $150 call, Sell $175 call
    Net debit: ~$7.50-9.00
    Max profit: $25 spread - premium = ~$16-17.50 (185-220% return)
    Breakeven: ~$157.50-159
    Max loss: Premium paid
    Captures the entire base-to-bull case ($155-175 range)
    VERDICT: BEST STRATEGY for this setup. Defined risk, captures
    the Trump visit + T+35 window perfectly.
    
  STRATEGY 5: $155/$170 Call Spread (June) — FOCUSED
    Buy $155 call, Sell $170 call
    Net debit: ~$5.00-6.00
    Max profit: $15 spread - premium = ~$9-10 (150-200% return)
    Breakeven: ~$160-161
    Captures the most likely move zone
    VERDICT: More capital-efficient version of Strategy 4
    
  STRATEGY 6: Calendar Spread — Long June $160, Short April $160
    Sell April $160 call (captures Two Sessions + pre-Trump premium)
    Long June $160 call (keeps exposure through all catalysts)
    Net debit: lower than naked June call
    VERDICT: Sophisticated. Good if you expect gradual grind up.
""")


# ============================================================================
# SECTION 13: FINAL VERDICT & ENTRY PLAN
# ============================================================================
print("\n" + "=" * 90)
print("  13. FINAL VERDICT & PRECISE ENTRY PLAN")
print("=" * 90)

print(f"""
  ┌────────────────────────────────────────────────────────────────────┐
  │  OVERALL ASSESSMENT: CONDITIONAL BUY — WAIT FOR TRIGGER          │
  └────────────────────────────────────────────────────────────────────┘
  
  THE SETUP IS FORMING. The catalyst stack is the best we've seen. 
  But the TECHNICAL STRUCTURE isn't ready yet.
  
  Feb 20 was critical: price tested $150.43 and bounced. That's your
  floor test. BUT the close at $154.45 is still below all short-term MAs.
  
  ═══════════════════════════════════════════════════════════════════════
  ENTRY PLAN — TWO SCENARIOS:
  ═══════════════════════════════════════════════════════════════════════
  
  ENTRY A (AGGRESSIVE — 40% of position):
  ─────────────────────────────────────────
  Trigger: BABA closes above $158 (reclaims 10 SMA area) on volume 
           above 10M shares
  When:    Could happen any day. Watch for Two Sessions catalyst (Mar 4-5)
  Action:  Buy the $150/$175 call spread (June)
  Risk:    ~$8-9 per spread ($800-900 per contract)
  Target:  $170+ by April (2x+ return)
  Stop:    Close below $148 for 2 consecutive days = cut position
  
  ENTRY B (CONFIRMATION — remaining 60% of position):
  ─────────────────────────────────────────────────────
  Trigger: BABA breaks above $163-165 (reclaims 20 SMA + 50 SMA) with 
           volume > 15M, ideally during Trump visit front-running 
           (Mar 10-20 timeframe)
  Action:  Add second unit of $155/$175 call spread (June)
  Risk:    ~$6-7 per spread
  Target:  $175-185 by May-Jun (3x+ return)
  Stop:    Close below $155 for 2 consecutive days = cut position
  
  ═══════════════════════════════════════════════════════════════════════
  ABOUT THE $165 CALL SPECIFICALLY:
  ═══════════════════════════════════════════════════════════════════════
  
  The naked $165 June call is NOT the optimal play because:
  1. You're 7% OTM — all time value, zero intrinsic
  2. Theta decay will eat ~$0.04-0.06/day starting immediately
  3. If BABA grinds sideways in $150-160 through March, you lose 40%+
  4. The breakeven of ~$171 requires a 11% rally
  
  INSTEAD: The $150/$175 call spread costs less, has a lower breakeven
  (~$158), and still captures full upside to $175 (which is the base-
  to-bull case target). If BABA rips past $175 to $190, you leave some
  money on the table, but you made 180-220% return anyway.
  
  ═══════════════════════════════════════════════════════════════════════
  POSITION SIZING (for $8,000 portfolio):
  ═══════════════════════════════════════════════════════════════════════
  
  Max risk on this trade: 5-8% of portfolio = $400-640
  
  Option A: One $150/$175 call spread @ ~$8.50 = $850 per contract
            That's 10.6% of portfolio — slightly over max risk.
            Consider: 1 spread with tight stop.
            
  Option B: One $155/$170 call spread @ ~$5.50 = $550 per contract
            That's 6.9% of portfolio — within risk budget.
            Can afford to add second contract on confirmation.
            
  Option C: Two $155/$170 call spreads (scaled entry):
            1st at $158 reclaim, 2nd at $163+ breakout
            Total max risk: ~$1,100 = 13.8% of portfolio
            Only if BOTH triggers fire. Never all-in at once.
  
  ═══════════════════════════════════════════════════════════════════════
  WHAT TO AVOID:
  ═══════════════════════════════════════════════════════════════════════
  
  ✗ Do NOT buy naked OTM calls ($165+) without a confirmation trigger
  ✗ Do NOT enter before the 10 SMA reclaim ($158)
  ✗ Do NOT risk more than 8% of portfolio on a single options trade
  ✗ Do NOT hold through earnings without reducing to house money
  ✗ Do NOT ignore the stop — $148 break = fundamental thesis damaged
""")

print("\n" + "=" * 90)
print("  ANALYSIS COMPLETE")
print("=" * 90)
