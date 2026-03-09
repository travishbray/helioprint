# app.py  —  HELIOPRINT Flask web server with timezone support
from flask import Flask, render_template, request, jsonify
from orbital_engine import (date_to_jd, get_planet_positions,
                             get_sun_longitude, get_zodiac_sign, jd_to_date)
from lunar import get_lunar_data
from solar_cycle import get_solar_cycle_data
from pineal import calc_pineal_index, get_vivaxis_window
from noaa_data import get_geomagnetic_conditions
import datetime
import os

app = Flask(__name__)

def local_to_utc(year, month, day, hour_local, timezone_str):
    """Convert local birth time to UTC using pytz if available."""
    try:
        import pytz
        tz       = pytz.timezone(timezone_str)
        local_dt = tz.localize(datetime.datetime(
            year, month, day, int(hour_local), int((hour_local % 1) * 60)
        ))
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60
    except Exception:
        return year, month, day, hour_local

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data       = request.get_json()
    year       = int(data['year'])
    month      = int(data['month'])
    day        = int(data['day'])
    hour_local = float(data.get('hour', 12))
    timezone   = data.get('timezone', 'UTC')

    # Convert to UTC
    if timezone != 'UTC':
        year, month, day, hour = local_to_utc(year, month, day, hour_local, timezone)
    else:
        hour = hour_local

    jd        = date_to_jd(year, month, day, hour)
    positions = get_planet_positions(jd)
    moon      = get_lunar_data(jd)
    sol       = get_solar_cycle_data(jd)
    pi        = calc_pineal_index(positions, moon, sol)
    sun_lon   = get_sun_longitude(jd)
    sign      = get_zodiac_sign(sun_lon)
    viv       = get_vivaxis_window(year, month, day, hour)
    live      = get_geomagnetic_conditions()

    return jsonify({
        'jd':         round(jd, 4),
        'date_label': jd_to_date(jd),
        'utc_note':   f'{int(hour):02d}:{int((hour%1)*60):02d} UTC',
        'sun': {
            'longitude': round(sun_lon, 2),
            'sign':      sign['name'],
            'symbol':    sign['symbol'],
            'element':   sign['element'],
            'modality':  sign['modality'],
            'ruler':     sign['ruler'],
            'degree':    round(sign['degree'], 2),
        },
        'moon': {
            'phase_name':        moon['phase_name'],
            'phase_symbol':      moon['phase_symbol'],
            'age_days':          round(moon['age_days'], 1),
            'illumination':      round(moon['illumination'] * 100, 1),
            'phase_angle':       round(moon['phase_angle'], 1),
            'moon_sign':         moon['moon_sign'],
            'moon_sign_symbol':  moon['moon_sign_symbol'],
            'tidal_index':       round(moon['tidal_index'], 1),
            'magnetic_coupling': round(moon['magnetic_coupling'], 1),
        },
        'solar': {
            'cycle_number': sol['cycle_number'],
            'phase_label':  sol['phase_label'],
            'phase_pct':    round(sol['phase'] * 100, 1),
            'envelope':     round(sol['envelope'] * 100, 1),
            'est_ssn':      sol['est_ssn'],
            'kp_proxy':     sol['kp_proxy'],
            'peak_ssn':     sol['cycle_peak_ssn'],
        },
        'pineal': {
            'score':          pi['score'],
            'band':           pi['band'],
            'interpretation': pi['interpretation'],
            'dominant':       pi['dominant'],
            'solar':          pi['solar'],
            'lunar':          pi['lunar'],
            'giants':         pi['giants'],
            'inner':          pi['inner'],
        },
        'vivaxis': {
            'birth_date': viv['birth_date'],
            'window_end': viv['window_end'],
            'active':     viv['active'],
            'elapsed':    viv['elapsed'],
            'remaining':  viv['remaining'],
        },
        'planets': [
            {
                'name':      p['name'],
                'symbol':    p['symbol'],
                'longitude': round(p['longitude'], 2),
                'x':         round(p['x'], 4),
                'y':         round(p['y'], 4),
                'color':     p['color'],
                'dist':      round(p['dist_from_earth'], 3) if p['name'] != 'Earth' else None,
                'field':     p['field_at_earth'] if p['name'] != 'Earth' else None,
                'tilt':      p['mag_tilt'],
                'character': p['mag_character'],
                'polarity':  p['mag_polarity'],
            }
            for p in positions
        ],
        'live': {
            'kp':         live['kp']['kp'],
            'kp_label':   live['kp']['label'],
            'kp_status':  live['kp']['status'],
            'wind':       live['solar_wind']['speed'],
            'wind_label': live['solar_wind'].get('wind_label', ''),
            'timestamp':  live['timestamp'],
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)