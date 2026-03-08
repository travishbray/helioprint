# noaa_data.py  —  Live solar and geomagnetic data from NOAA
# No API key required. Uses NOAA Space Weather Prediction Center.
import urllib.request
import json
from datetime import datetime, timezone

NOAA_KP_URL   = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
NOAA_WIND_URL = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"

def fetch_json(url, timeout=8):
    """Fetch JSON from a URL. Returns None if unreachable."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  ⚠  Could not reach NOAA ({e}). Using offline fallback.")
        return None

def get_live_kp():
    """Fetch the current planetary Kp index from NOAA."""
    data = fetch_json(NOAA_KP_URL)
    if not data:
        return {'kp': None, 'status': 'offline', 'label': 'Unavailable'}

    latest = data[-1]
    kp = float(latest.get('kp_index', 0))

    if kp < 2:    label = 'Quiet'
    elif kp < 4:  label = 'Unsettled'
    elif kp < 5:  label = 'Active'
    elif kp < 6:  label = 'Minor Storm'
    elif kp < 7:  label = 'Major Storm'
    else:         label = 'Severe Storm'

    return {
        'kp':       kp,
        'label':    label,
        'timestamp': latest.get('time_tag', 'unknown'),
        'status':   'live',
    }

def get_live_solar_wind():
    """Fetch live solar wind speed and density from NOAA."""
    data = fetch_json(NOAA_WIND_URL)
    if not data:
        return {'speed': None, 'density': None, 'status': 'offline'}

    latest = data[-1]
    speed   = latest.get('proton_speed')
    density = latest.get('proton_density')

    if speed is None:
        return {'speed': None, 'density': None, 'status': 'offline'}

    speed = float(speed)

    if speed < 400:   wind_label = 'Slow'
    elif speed < 600: wind_label = 'Moderate'
    elif speed < 800: wind_label = 'Fast'
    else:             wind_label = 'Very Fast — storm risk'

    return {
        'speed':      speed,
        'density':    float(density) if density else None,
        'wind_label': wind_label,
        'timestamp':  latest.get('time_tag', 'unknown'),
        'status':     'live',
    }

def get_geomagnetic_conditions():
    """Combines Kp and solar wind into a single condition summary."""
    return {
        'timestamp':  datetime.now(timezone.utc).strftime('%d %b %Y  %H:%M UTC'),
        'kp':         get_live_kp(),
        'solar_wind': get_live_solar_wind(),
    }

def print_conditions():
    """Print a formatted live conditions report."""
    cond = get_geomagnetic_conditions()
    print(f"\n  🌍  LIVE GEOMAGNETIC CONDITIONS")
    print(f"  {'─'*45}")
    print(f"  Timestamp  : {cond['timestamp']}")

    kp = cond['kp']
    if kp['status'] == 'live':
        print(f"  Kp Index   : {kp['kp']}  —  {kp['label']}")
        print(f"  Reading    : {kp['timestamp']}")
    else:
        print(f"  Kp Index   : Offline")

    wind = cond['solar_wind']
    if wind['status'] == 'live' and wind['speed']:
        print(f"  Solar Wind : {wind['speed']:.0f} km/s  —  {wind['wind_label']}")
        if wind['density']:
            print(f"  Density    : {wind['density']:.1f} p/cm³")
    else:
        print(f"  Solar Wind : Offline")

if __name__ == '__main__':
    print_conditions()