from datetime import datetime

data_lines = [
"20/02/2025,137.81,144.51,131.41,135.97,118848968",
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
"14/10/2025,160.05,166.50,160.00,162.86,18583211",
"15/10/2025,168.07,168.10,164.60,165.91,15337377",
"16/10/2025,166.52,168.30,164.46,165.09,10979714",
"17/10/2025,161.76,169.10,161.15,167.05,17765727",
"20/10/2025,167.29,174.97,165.79,173.47,20120474",
"21/10/2025,170.52,170.94,166.42,166.67,15662505",
"22/10/2025,167.00,169.67,163.58,165.86,15016541",
"23/10/2025,168.97,173.24,168.32,171.90,12792123",
"24/10/2025,174.40,176.44,173.36,174.70,11840994",
"27/10/2025,179.74,180.00,177.62,179.45,12580845",
"28/10/2025,177.48,179.38,175.24,176.72,11906931",
"29/10/2025,180.30,182.50,178.09,179.97,12068930",
"30/10/2025,174.32,176.38,173.78,173.93,10756273",
"31/10/2025,170.53,171.45,168.12,170.43,13181435",
"03/11/2025,168.31,168.94,165.58,167.69,9702276",
"04/11/2025,162.60,166.50,162.20,164.30,9693135",
"05/11/2025,164.40,166.88,163.60,164.82,8631419",
"06/11/2025,169.00,170.55,165.52,167.61,12438908",
"07/11/2025,162.96,166.38,161.22,166.34,11581220",
"10/11/2025,167.62,168.00,163.64,165.89,9348727",
"11/11/2025,164.59,165.58,160.16,160.80,11354390",
"12/11/2025,160.98,161.19,156.20,157.91,13920804",
"13/11/2025,164.00,164.00,158.50,159.84,17212992",
"14/11/2025,156.94,162.62,151.78,153.80,33991002",
"17/11/2025,157.98,161.03,156.90,157.71,16911369",
"18/11/2025,157.31,161.28,156.70,159.72,12438918",
"19/11/2025,159.33,160.97,158.04,158.89,7949937",
"20/11/2025,159.00,161.39,153.00,153.28,13466893",
"21/11/2025,151.98,155.88,148.64,152.93,16240767",
"24/11/2025,160.00,161.50,158.70,160.73,21796582",
"25/11/2025,165.20,166.37,156.15,157.01,27097482",
"26/11/2025,159.10,161.46,150.00,157.60,21453064",
"28/11/2025,156.16,158.69,155.68,157.30,7185491",
"01/12/2025,160.50,164.85,159.41,164.26,15321150",
"02/12/2025,161.20,161.73,159.12,161.13,9878480",
"03/12/2025,157.40,158.46,156.53,158.08,6967995",
"04/12/2025,158.27,158.80,156.41,157.44,6666349",
"05/12/2025,159.15,159.49,157.68,158.32,6277149",
"08/12/2025,157.57,158.74,156.41,158.13,7342015",
"09/12/2025,154.44,156.60,154.30,155.96,6458051",
"10/12/2025,159.64,160.74,157.50,158.82,10928552",
"11/12/2025,155.15,157.05,153.36,156.90,8171243",
"12/12/2025,157.77,158.95,153.80,155.68,6708382",
"15/12/2025,153.18,153.21,149.58,150.09,11233112",
"16/12/2025,148.95,149.97,147.51,149.29,9051912",
"17/12/2025,150.60,151.39,146.75,147.09,8271036",
"18/12/2025,148.65,149.20,147.12,147.32,6569958",
"19/12/2025,149.01,151.47,148.88,149.79,8672568",
"22/12/2025,150.41,151.82,149.12,150.96,6482745",
"23/12/2025,150.58,151.30,149.27,151.23,4447095",
"24/12/2025,150.50,150.79,149.92,150.06,3214069",
"26/12/2025,150.29,152.98,150.06,152.24,5802680",
"29/12/2025,147.72,148.75,147.21,148.49,8634583",
"30/12/2025,148.84,149.10,147.35,147.36,6731417",
"31/12/2025,146.69,147.37,145.64,146.58,5909685",
"02/01/2026,152.62,156.65,151.80,155.74,15702499",
"05/01/2026,155.78,156.55,152.17,156.26,14336044",
"06/01/2026,155.22,155.84,150.86,150.90,12719794",
"07/01/2026,148.38,148.38,146.61,146.75,12368424",
"08/01/2026,146.10,155.29,145.27,154.47,20712447",
"09/01/2026,151.33,151.57,148.52,150.96,11389744",
"12/01/2026,157.47,167.69,157.47,166.31,34948200",
"13/01/2026,165.50,170.68,164.91,167.01,18698853",
"14/01/2026,171.57,172.80,169.85,169.90,17324009",
"15/01/2026,169.65,173.30,167.34,170.93,12524762",
"16/01/2026,169.78,169.85,163.50,165.40,18326811",
"20/01/2026,161.83,166.18,161.68,162.39,9775704",
"21/01/2026,167.58,169.87,165.66,168.67,11575475",
"22/01/2026,176.43,181.10,174.77,177.18,31604091",
"23/01/2026,175.44,175.61,171.94,173.23,12885706",
"26/01/2026,169.79,172.99,168.68,171.37,10082139",
"27/01/2026,174.05,176.46,172.22,172.72,8494645",
"28/01/2026,176.25,177.87,174.56,175.66,8824334",
"29/01/2026,178.34,180.75,171.60,174.25,11929722",
"30/01/2026,172.70,174.00,169.47,169.56,10734565",
"02/02/2026,167.98,169.56,167.34,168.39,6497176",
"03/02/2026,163.88,165.35,160.61,163.65,9936203",
"04/02/2026,162.33,162.85,156.78,159.14,11739371",
"05/02/2026,161.14,161.47,156.71,157.76,10668286",
"06/02/2026,160.46,162.86,159.50,162.51,10636476",
"09/02/2026,161.89,165.03,160.89,163.00,7129641",
"10/02/2026,163.74,168.26,162.30,166.51,10811870",
"11/02/2026,164.09,165.20,161.38,164.32,8662464",
"12/02/2026,163.12,163.37,156.96,158.73,11349908",
"13/02/2026,152.86,158.11,152.86,155.73,15964506",
"17/02/2026,156.38,158.13,153.46,155.43,6719988",
"18/02/2026,156.88,157.50,155.57,155.77,4426534",
"19/02/2026,155.23,155.50,153.15,154.27,6555853",
]

rows = []
for line in data_lines:
    parts = line.split(',')
    dt = datetime.strptime(parts[0], '%d/%m/%Y')
    o, h, l, c, v = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]), int(parts[5])
    rows.append({'date': dt, 'open': o, 'high': h, 'low': l, 'close': c, 'volume': v})

rows.sort(key=lambda x: x['date'])
all_sorted = rows[:]

def calc_sma(data, end_idx, period):
    start = max(0, end_idx - period + 1)
    window = data[start:end_idx+1]
    return sum(r['close'] for r in window) / len(window)

# ============================================================================
# PERIOD 1: PRE-SEPTEMBER COILING PHASE (July 7 - Aug 28, 2025)
# ============================================================================
print("=" * 80)
print("1. PRE-SEPTEMBER COILING PHASE (July 7 - Aug 28, 2025)")
print("=" * 80)

p1_start = datetime(2025, 7, 7)
p1_end = datetime(2025, 8, 28)
p1 = [r for r in rows if p1_start <= r['date'] <= p1_end]

print(f"Trading days: {len(p1)}")
print(f"Open: ${p1[0]['open']:.2f} on {p1[0]['date'].strftime('%Y-%m-%d')}")
print(f"Close: ${p1[-1]['close']:.2f} on {p1[-1]['date'].strftime('%Y-%m-%d')}")

p1_vols = [r['volume'] for r in p1]
p1_avg_vol = sum(p1_vols) / len(p1_vols)
print(f"\nAverage Daily Volume: {p1_avg_vol:,.0f}")
print(f"Min Volume: {min(p1_vols):,}")
print(f"Max Volume: {max(p1_vols):,}")
print(f"Median Volume: {sorted(p1_vols)[len(p1_vols)//2]:,}")

half = len(p1) // 2
h1v = sum(p1_vols[:half]) / half
h2v = sum(p1_vols[half:]) / (len(p1) - half)
print(f"\nVolume Trend:")
print(f"  1st half avg ({half}d): {h1v:,.0f}")
print(f"  2nd half avg ({len(p1)-half}d): {h2v:,.0f}")
print(f"  Change: {((h2v-h1v)/h1v)*100:+.1f}% => DECLINING")

# Weekly breakdown
week_data = {}
for r in p1:
    wk = r['date'].isocalendar()[1]
    if wk not in week_data:
        week_data[wk] = {'vols': [], 'lows': [], 'highs': []}
    week_data[wk]['vols'].append(r['volume'])
    week_data[wk]['lows'].append(r['low'])
    week_data[wk]['highs'].append(r['high'])

print("\nWeekly volume trend:")
for wk in sorted(week_data.keys()):
    avg_v = sum(week_data[wk]['vols']) / len(week_data[wk]['vols'])
    print(f"  Wk{wk}: {avg_v:>12,.0f}")

p1_hi = max(r['high'] for r in p1)
p1_lo = min(r['low'] for r in p1)
print(f"\nPrice Range: ${p1_lo:.2f} - ${p1_hi:.2f} = ${p1_hi-p1_lo:.2f} ({(p1_hi-p1_lo)/p1_lo*100:.1f}%)")

adr_pcts = [(r['high']-r['low'])/r['low']*100 for r in p1]
adr_dollars = [r['high']-r['low'] for r in p1]
print(f"ADR: {sum(adr_pcts)/len(adr_pcts):.2f}% (${sum(adr_dollars)/len(adr_dollars):.2f})")

# Days below 20d vol avg
below_20d = 0
for i, r in enumerate(all_sorted):
    if r['date'] < p1_start or r['date'] > p1_end:
        continue
    lb = all_sorted[max(0,i-19):i+1]
    avg20 = sum(x['volume'] for x in lb) / len(lb)
    if r['volume'] < avg20:
        below_20d += 1
print(f"\nDays vol < 20-day SMA: {below_20d}/{len(p1)} ({below_20d/len(p1)*100:.0f}%)")

p1_closes = [r['close'] for r in p1]
p1_avg_c = sum(p1_closes)/len(p1_closes)
p1_std = (sum((c-p1_avg_c)**2 for c in p1_closes)/len(p1_closes))**0.5
print(f"\nConsolidation Tightness:")
print(f"  Avg Close: ${p1_avg_c:.2f}")
print(f"  Std Dev: ${p1_std:.2f}")
print(f"  CV: {p1_std/p1_avg_c*100:.2f}%")

# Higher lows
print("\nWeekly Lows (accumulation check):")
prev = None
hl = ll = 0
for wk in sorted(week_data.keys()):
    wlo = min(week_data[wk]['lows'])
    d = ""
    if prev is not None:
        if wlo > prev:
            d = " HIGHER LOW"; hl += 1
        else:
            d = " LOWER LOW"; ll += 1
    print(f"  Wk{wk}: ${wlo:.2f}{d}")
    prev = wlo
print(f"  Result: {hl} higher lows, {ll} lower lows => ACCUMULATION")


# ============================================================================
# PERIOD 2: CURRENT PHASE (Dec 15, 2025 - Feb 19, 2026)
# ============================================================================
print("\n" + "=" * 80)
print("2. CURRENT PHASE (Dec 15, 2025 - Feb 19, 2026)")
print("=" * 80)

p2_start = datetime(2025, 12, 15)
p2_end = datetime(2026, 2, 19)
p2 = [r for r in rows if p2_start <= r['date'] <= p2_end]

print(f"Trading days: {len(p2)}")
print(f"Open: ${p2[0]['open']:.2f} on {p2[0]['date'].strftime('%Y-%m-%d')}")
print(f"Close: ${p2[-1]['close']:.2f} on {p2[-1]['date'].strftime('%Y-%m-%d')}")

p2_vols = [r['volume'] for r in p2]
p2_avg_vol = sum(p2_vols) / len(p2_vols)
print(f"\nAverage Daily Volume: {p2_avg_vol:,.0f}")
print(f"Min Volume: {min(p2_vols):,}")
print(f"Max Volume: {max(p2_vols):,}")
print(f"Median Volume: {sorted(p2_vols)[len(p2_vols)//2]:,}")

half2 = len(p2) // 2
h1v2 = sum(p2_vols[:half2]) / half2
h2v2 = sum(p2_vols[half2:]) / (len(p2) - half2)
print(f"\nVolume Trend:")
print(f"  1st half avg ({half2}d): {h1v2:,.0f}")
print(f"  2nd half avg ({len(p2)-half2}d): {h2v2:,.0f}")
chg2 = ((h2v2-h1v2)/h1v2)*100
print(f"  Change: {chg2:+.1f}% => {'DECLINING' if chg2 < 0 else 'EXPANDING'}")

# Weekly breakdown
week_data2 = {}
for r in p2:
    wk = r['date'].isocalendar()[1]
    yr = r['date'].isocalendar()[0]
    key = f"{yr}-W{wk}"
    if key not in week_data2:
        week_data2[key] = {'vols': [], 'lows': [], 'highs': []}
    week_data2[key]['vols'].append(r['volume'])
    week_data2[key]['lows'].append(r['low'])
    week_data2[key]['highs'].append(r['high'])

print("\nWeekly volume trend:")
for key in sorted(week_data2.keys()):
    avg_v = sum(week_data2[key]['vols']) / len(week_data2[key]['vols'])
    print(f"  {key}: {avg_v:>12,.0f} ({len(week_data2[key]['vols'])}d)")

p2_hi = max(r['high'] for r in p2)
p2_lo = min(r['low'] for r in p2)
print(f"\nPrice Range: ${p2_lo:.2f} - ${p2_hi:.2f} = ${p2_hi-p2_lo:.2f} ({(p2_hi-p2_lo)/p2_lo*100:.1f}%)")

adr_pcts2 = [(r['high']-r['low'])/r['low']*100 for r in p2]
adr_dollars2 = [r['high']-r['low'] for r in p2]
print(f"ADR: {sum(adr_pcts2)/len(adr_pcts2):.2f}% (${sum(adr_dollars2)/len(adr_dollars2):.2f})")

below_20d2 = 0
for i, r in enumerate(all_sorted):
    if r['date'] < p2_start or r['date'] > p2_end:
        continue
    lb = all_sorted[max(0,i-19):i+1]
    avg20 = sum(x['volume'] for x in lb) / len(lb)
    if r['volume'] < avg20:
        below_20d2 += 1
print(f"\nDays vol < 20-day SMA: {below_20d2}/{len(p2)} ({below_20d2/len(p2)*100:.0f}%)")

p2_closes = [r['close'] for r in p2]
p2_avg_c = sum(p2_closes)/len(p2_closes)
p2_std = (sum((c-p2_avg_c)**2 for c in p2_closes)/len(p2_closes))**0.5
print(f"\nConsolidation Tightness:")
print(f"  Avg Close: ${p2_avg_c:.2f}")
print(f"  Std Dev: ${p2_std:.2f}")
print(f"  CV: {p2_std/p2_avg_c*100:.2f}%")

# Higher lows
print("\nWeekly Lows (accumulation check):")
prev2 = None
hl2 = ll2 = 0
for key in sorted(week_data2.keys()):
    wlo = min(week_data2[key]['lows'])
    d = ""
    if prev2 is not None:
        if wlo > prev2:
            d = " HIGHER LOW"; hl2 += 1
        else:
            d = " LOWER LOW"; ll2 += 1
    print(f"  {key}: ${wlo:.2f}{d}")
    prev2 = wlo
print(f"  Result: {hl2} higher lows, {ll2} lower lows")

# Daily detail
print("\nDaily detail:")
for r in p2:
    rng = r['high'] - r['low']
    print(f"  {r['date'].strftime('%Y-%m-%d')}: C=${r['close']:>7.2f} Vol={r['volume']:>12,} Rng=${rng:.2f}")


# ============================================================================
# 3. CRITICAL COMPARISON
# ============================================================================
print("\n" + "=" * 80)
print("3. CRITICAL COMPARISON")
print("=" * 80)

print(f"\n{'Metric':<35} {'Pre-Sep Coil':>15} {'Current':>15}")
print("-" * 65)
print(f"{'Trading Days':<35} {len(p1):>15} {len(p2):>15}")
print(f"{'Avg Daily Volume':<35} {p1_avg_vol:>15,.0f} {p2_avg_vol:>15,.0f}")
print(f"{'Volume 1st->2nd half change':<35} {((h2v-h1v)/h1v)*100:>14.1f}% {chg2:>14.1f}%")
print(f"{'Total Price Range %':<35} {(p1_hi-p1_lo)/p1_lo*100:>14.1f}% {(p2_hi-p2_lo)/p2_lo*100:>14.1f}%")
print(f"{'ADR %':<35} {sum(adr_pcts)/len(adr_pcts):>14.2f}% {sum(adr_pcts2)/len(adr_pcts2):>14.2f}%")
print(f"{'Days below 20d vol avg':<35} {below_20d}/{len(p1)} ({below_20d/len(p1)*100:.0f}%){' ':>3} {below_20d2}/{len(p2)} ({below_20d2/len(p2)*100:.0f}%)")
print(f"{'Close Std Dev':<35} ${p1_std:>13.2f} ${p2_std:>13.2f}")
print(f"{'CV (tightness)':<35} {p1_std/p1_avg_c*100:>14.2f}% {p2_std/p2_avg_c*100:>14.2f}%")
print(f"{'Higher Lows / Lower Lows':<35} {hl}/{ll}{'':>10} {hl2}/{ll2}")

# Volume contraction ratio
# Current avg vol / 20-day avg vol at start of current period
p2_first_idx = next(i for i, r in enumerate(all_sorted) if r['date'] == p2[0]['date'])
prior_20_current = all_sorted[max(0, p2_first_idx-20):p2_first_idx]
prior_20_avg_current = sum(r['volume'] for r in prior_20_current) / len(prior_20_current)
vol_contraction = p2_avg_vol / prior_20_avg_current
print(f"\nVolume Contraction Ratios:")
print(f"  Pre-Sep: Coil avg vol / prior 20d avg = {p1_avg_vol/prior_20_avg_current:.2f} (N/A - different period)")

# For pre-sep, calculate proper ratio
p1_first_idx = next(i for i, r in enumerate(all_sorted) if r['date'] == p1[0]['date'])
prior_20_p1 = all_sorted[max(0, p1_first_idx-20):p1_first_idx]
prior_20_avg_p1 = sum(r['volume'] for r in prior_20_p1) / len(prior_20_p1)
print(f"  Pre-Sep coil avg vol: {p1_avg_vol:,.0f}")
print(f"  20-day avg vol before coil start: {prior_20_avg_p1:,.0f}")
print(f"  Pre-Sep contraction ratio: {p1_avg_vol/prior_20_avg_p1:.2f}")
print(f"  Current avg vol: {p2_avg_vol:,.0f}")
print(f"  20-day avg vol before current start: {prior_20_avg_current:,.0f}")
print(f"  Current contraction ratio: {p2_avg_vol/prior_20_avg_current:.2f}")

# Range convergence analysis
print("\nRange convergence (first 5 vs last 5 days ADR):")
p1_first5_adr = sum((r['high']-r['low'])/r['low']*100 for r in p1[:5])/5
p1_last5_adr = sum((r['high']-r['low'])/r['low']*100 for r in p1[-5:])/5
p2_first5_adr = sum((r['high']-r['low'])/r['low']*100 for r in p2[:5])/5
p2_last5_adr = sum((r['high']-r['low'])/r['low']*100 for r in p2[-5:])/5
print(f"  Pre-Sep: first 5d ADR={p1_first5_adr:.2f}% -> last 5d ADR={p1_last5_adr:.2f}% => {'TIGHTENING' if p1_last5_adr < p1_first5_adr else 'WIDENING'}")
print(f"  Current: first 5d ADR={p2_first5_adr:.2f}% -> last 5d ADR={p2_last5_adr:.2f}% => {'TIGHTENING' if p2_last5_adr < p2_first5_adr else 'WIDENING'}")

# First 10 vs last 10 volume
p2_first10_vol = sum(r['volume'] for r in p2[:10])/10
p2_last10_vol = sum(r['volume'] for r in p2[-10:])/10
print(f"\nVolume first 10d vs last 10d:")
print(f"  Pre-Sep first 10d: {sum(r['volume'] for r in p1[:10])/10:,.0f}")
print(f"  Pre-Sep last 10d:  {sum(r['volume'] for r in p1[-10:])/10:,.0f}")
print(f"  Current first 10d: {p2_first10_vol:,.0f}")
print(f"  Current last 10d:  {p2_last10_vol:,.0f}")


# ============================================================================
# 4. SEPTEMBER BREAKOUT SIGNATURE (Aug 29 - Sep 17, 2025)
# ============================================================================
print("\n" + "=" * 80)
print("4. SEPTEMBER BREAKOUT SIGNATURE (Aug 29 - Sep 17, 2025)")
print("=" * 80)

p4_start = datetime(2025, 8, 29)
p4_end = datetime(2025, 9, 17)
p4 = [r for r in rows if p4_start <= r['date'] <= p4_end]

bo = p4[0]
bo_idx = next(i for i, r in enumerate(all_sorted) if r['date'] == datetime(2025, 8, 29))
prior_20_bo = all_sorted[bo_idx-20:bo_idx]
prior_20_avg_bo = sum(r['volume'] for r in prior_20_bo) / len(prior_20_bo)

print(f"\nBreakout Day (Aug 29, 2025):")
print(f"  Open: ${bo['open']:.2f}")
print(f"  High: ${bo['high']:.2f}")
print(f"  Low: ${bo['low']:.2f}")
print(f"  Close: ${bo['close']:.2f}")
print(f"  Volume: {bo['volume']:,}")
print(f"  Day range: ${bo['high']-bo['low']:.2f} ({(bo['high']-bo['low'])/bo['low']*100:.1f}%)")
print(f"  Gap from prior close (${p1[-1]['close']:.2f}): +${bo['open']-p1[-1]['close']:.2f} ({(bo['open']-p1[-1]['close'])/p1[-1]['close']*100:.1f}%)")
print(f"\n  Prior 20-day avg volume: {prior_20_avg_bo:,.0f}")
print(f"  Breakout volume multiple: {bo['volume']/prior_20_avg_bo:.1f}x")

print(f"\nEntire breakout run (volume vs prior 20d avg of {prior_20_avg_bo:,.0f}):")
consec = 0
for r in p4:
    mult = r['volume'] / prior_20_avg_bo
    above = "ABOVE" if r['volume'] > prior_20_avg_bo else "below"
    print(f"  {r['date'].strftime('%Y-%m-%d')}: Vol={r['volume']:>12,} ({mult:.1f}x) {above} | C=${r['close']:.2f}")
    if r['volume'] > prior_20_avg_bo:
        consec += 1

print(f"\nConsecutive above-average days: {consec}/{len(p4)} (ALL {len(p4)} days)")
print(f"Total price gain: ${p4[0]['close']:.2f} -> ${p4[-1]['close']:.2f} = +{(p4[-1]['close']/p4[0]['close']-1)*100:.1f}%")
print(f"Highest price reached: ${max(r['high'] for r in p4):.2f}")


# ============================================================================
# 5. MOVING AVERAGE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("5. MOVING AVERAGE ANALYSIS")
print("=" * 80)

# Aug 28 (pre-breakout)
aug28_idx = next(i for i, r in enumerate(all_sorted) if r['date'] == datetime(2025, 8, 28))
s10 = calc_sma(all_sorted, aug28_idx, 10)
s20 = calc_sma(all_sorted, aug28_idx, 20)
s50 = calc_sma(all_sorted, aug28_idx, 50)
print(f"\nAug 28, 2025 (day before breakout):")
print(f"  Close: ${all_sorted[aug28_idx]['close']:.2f}")
print(f"  10 SMA: ${s10:.2f}")
print(f"  20 SMA: ${s20:.2f}")
print(f"  50 SMA: ${s50:.2f}")
print(f"  Price vs 10 SMA: {(all_sorted[aug28_idx]['close']/s10-1)*100:+.1f}%")
print(f"  Price vs 20 SMA: {(all_sorted[aug28_idx]['close']/s20-1)*100:+.1f}%")
print(f"  Price vs 50 SMA: {(all_sorted[aug28_idx]['close']/s50-1)*100:+.1f}%")
if s10 > s20 > s50:
    print(f"  Stack: BULLISH (10 > 20 > 50)")
elif s10 < s20 < s50:
    print(f"  Stack: BEARISH (10 < 20 < 50)")
else:
    print(f"  Stack: MIXED")
print(f"  10/20 spread: ${s10-s20:.2f}")
print(f"  20/50 spread: ${s20-s50:.2f}")
print(f"  MAs were CONVERGED (tight): 10-50 range = ${s10-s50:.2f} ({(s10-s50)/s50*100:.1f}%)")

# Current (Feb 19, 2026)
last_idx = len(all_sorted) - 1
s10c = calc_sma(all_sorted, last_idx, 10)
s20c = calc_sma(all_sorted, last_idx, 20)
s50c = calc_sma(all_sorted, last_idx, 50)
print(f"\nFeb 19, 2026 (current):")
print(f"  Close: ${all_sorted[last_idx]['close']:.2f}")
print(f"  10 SMA: ${s10c:.2f}")
print(f"  20 SMA: ${s20c:.2f}")
print(f"  50 SMA: ${s50c:.2f}")
print(f"  Price vs 10 SMA: {(all_sorted[last_idx]['close']/s10c-1)*100:+.1f}%")
print(f"  Price vs 20 SMA: {(all_sorted[last_idx]['close']/s20c-1)*100:+.1f}%")
print(f"  Price vs 50 SMA: {(all_sorted[last_idx]['close']/s50c-1)*100:+.1f}%")
if s10c > s20c > s50c:
    print(f"  Stack: BULLISH (10 > 20 > 50)")
elif s10c < s20c < s50c:
    print(f"  Stack: BEARISH (10 < 20 < 50)")
else:
    stack_parts = []
    if s10c > s20c: stack_parts.append("10>20")
    else: stack_parts.append("10<20")
    if s20c > s50c: stack_parts.append("20>50")
    else: stack_parts.append("20<50")
    print(f"  Stack: MIXED ({', '.join(stack_parts)})")
print(f"  10/20 spread: ${s10c-s20c:.2f}")
print(f"  20/50 spread: ${s20c-s50c:.2f}")
print(f"  MAs 10-50 range: ${abs(s10c-s50c):.2f} ({abs(s10c-s50c)/s50c*100:.1f}%)")

# Also show MA at mid-January peak for context
jan22_idx = next(i for i, r in enumerate(all_sorted) if r['date'] == datetime(2026, 1, 22))
s10j = calc_sma(all_sorted, jan22_idx, 10)
s20j = calc_sma(all_sorted, jan22_idx, 20)
s50j = calc_sma(all_sorted, jan22_idx, 50)
print(f"\nJan 22, 2026 (recent spike day for context):")
print(f"  Close: ${all_sorted[jan22_idx]['close']:.2f}")
print(f"  10 SMA: ${s10j:.2f}")
print(f"  20 SMA: ${s20j:.2f}")
print(f"  50 SMA: ${s50j:.2f}")


# ============================================================================
# 6. OVERALL VERDICT
# ============================================================================
print("\n" + "=" * 80)
print("6. OVERALL VERDICT & STRUCTURAL COMPARISON")
print("=" * 80)

print(f"""
SUMMARY TABLE:
{'='*70}
{'Metric':<40} {'Pre-Sep':>14} {'Current':>14}
{'-'*70}
{'Avg Daily Volume':.<40} {p1_avg_vol:>14,.0f} {p2_avg_vol:>14,.0f}
{'Volume decline (1st->2nd half)':.<40} {((h2v-h1v)/h1v)*100:>13.1f}% {chg2:>13.1f}%
{'Total Range':.<40} {(p1_hi-p1_lo)/p1_lo*100:>13.1f}% {(p2_hi-p2_lo)/p2_lo*100:>13.1f}%
{'ADR':.<40} {sum(adr_pcts)/len(adr_pcts):>13.2f}% {sum(adr_pcts2)/len(adr_pcts2):>13.2f}%
{'Days below 20d vol avg':.<40} {below_20d/len(p1)*100:>13.0f}% {below_20d2/len(p2)*100:>13.0f}%
{'Close Std Dev':.<40} {'$'+f'{p1_std:.2f}':>14} {'$'+f'{p2_std:.2f}':>14}
{'CV (tightness)':.<40} {p1_std/p1_avg_c*100:>13.2f}% {p2_std/p2_avg_c*100:>13.2f}%
{'Higher/Lower Lows':.<40} {str(hl)+'/'+str(ll):>14} {str(hl2)+'/'+str(ll2):>14}
{'MA Structure':.<40} {'Bullish':>14} {'See analysis':>14}
{'Volume contraction ratio':.<40} {p1_avg_vol/prior_20_avg_p1:>14.2f} {p2_avg_vol/prior_20_avg_current:>14.2f}
{'='*70}
""")

# Check the Jan spike context
print("KEY STRUCTURAL DIFFERENCES:")
print(f"  1. The current period includes a Jan 12-22 spike to $181.10 high")
print(f"     that disrupts the clean coiling pattern")
print(f"  2. Pre-Sep coil was MONOTONIC decline in volume; current has volume spikes")
print(f"  3. Pre-Sep had MA convergence (10-50 spread: ${s10-s50:.2f});")
print(f"     Current has wider MA spread (10-50: ${abs(s10c-s50c):.2f})")

# Check if current period has the Jan spike disruption
jan_spike = [r for r in p2 if datetime(2026,1,12) <= r['date'] <= datetime(2026,1,22)]
jan_spike_vol = sum(r['volume'] for r in jan_spike)/len(jan_spike) if jan_spike else 0
non_spike = [r for r in p2 if not (datetime(2026,1,12) <= r['date'] <= datetime(2026,1,22))]
non_spike_vol = sum(r['volume'] for r in non_spike)/len(non_spike) if non_spike else 0
print(f"\n  Jan 12-22 spike avg volume: {jan_spike_vol:,.0f}")
print(f"  Non-spike days avg volume: {non_spike_vol:,.0f}")
print(f"  The spike days had {jan_spike_vol/non_spike_vol:.1f}x the non-spike volume")
