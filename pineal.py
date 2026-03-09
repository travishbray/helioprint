# pineal.py  —  Composite Pineal Sensitivity Index + Vivaxis window
# All 8 planets included. Inner planets weighted lightly — their fields
# are real but orders of magnitude smaller than the gas giants.
import math
import datetime

def calc_pineal_index(positions, lunar_data, solar_data):
    """
    Composite score (0-100) from solar, lunar, and all planetary contributions.

    Field law: B ∝ moment × cos(tilt) / r³  (correct magnetic dipole)

    Planet weights reflect actual magnetic moment magnitudes:
      Jupiter  × 15  — dominant, 19,500× Earth
      Saturn   × 8   — strong,   578×   Earth
      Uranus   × 5   — moderate, 48×    Earth (tilt-reduced)
      Neptune  × 3   — moderate, 26×    Earth (tilt-reduced)
      Earth    × 0   — origin, not applicable
      Mars     × 1   — crustal remnants, very weak
      Mercury  × 0.8 — weak but real aligned dipole
      Venus    × 0.2 — induced only, negligible
    """
    def field(name):
        p = next((x for x in positions if x['name'] == name), None)
        return p['field_at_earth'] if p and p['name'] != 'Earth' else 0.0

    jup = field('Jupiter')
    sat = field('Saturn')
    ura = field('Uranus')
    nep = field('Neptune')
    mar = field('Mars')
    mer = field('Mercury')
    ven = field('Venus')

    # Log-scaled to handle wide dynamic range across all planets
    giant_contrib = (
        math.log10(1 + jup) * 15 +
        math.log10(1 + sat) * 8  +
        math.log10(1 + ura) * 5  +
        math.log10(1 + nep) * 3
    )

    inner_contrib = (
        math.log10(1 + mar) * 1.0 +
        math.log10(1 + mer) * 0.8 +
        math.log10(1 + ven) * 0.2
    )

    solar_contrib = solar_data['envelope'] * 35
    lunar_contrib = (lunar_data['magnetic_coupling'] / 100) * 25

    raw   = solar_contrib + lunar_contrib + giant_contrib + inner_contrib
    score = min(100.0, max(0.0, raw))

    # Dominant driver
    dominant = max(
        ('solar',  solar_contrib),
        ('lunar',  lunar_contrib),
        ('giants', giant_contrib),
        ('inner',  inner_contrib),
        key=lambda x: x[1]
    )[0]

    solar_phase = solar_data['phase_label']

    if score > 70:
        band = 'Elevated'
        if dominant == 'solar':
            interp = f'Elevated — {solar_phase.lower()} driving strong geomagnetic activity'
        elif dominant == 'lunar':
            interp = f'Elevated — {lunar_data["phase_name"].lower()} lunar alignment dominant'
        elif dominant == 'giants':
            jup_dist = next((p["dist_from_earth"] for p in positions if p["name"]=="Jupiter"), 0)
            interp = f'Elevated — Jupiter proximity dominant (field: {jup:.1f}, dist: {jup_dist:.2f} AU)'
        else:
            interp = f'Elevated — inner planet alignment contributing'
    elif score > 40:
        band = 'Moderate'
        if dominant == 'solar':
            interp = f'Moderate — {solar_phase.lower()} sun, mixed environment'
        elif dominant == 'lunar':
            interp = f'Moderate — lunar phase the primary influence'
        else:
            interp = f'Moderate — gas giant fields dominant over quiet sun'
    else:
        band = 'Quiet'
        interp = 'Quiet — solar minimum, weak lunar coupling, distant gas giants'

    return {
        'score':          round(score, 1),
        'band':           band,
        'interpretation': interp,
        'dominant':       dominant,
        'solar':          round(solar_contrib, 1),
        'lunar':          round(lunar_contrib, 1),
        'giants':         round(giant_contrib, 1),
        'inner':          round(inner_contrib, 2),
    }


def get_vivaxis_window(year, month, day, hour=12):
    """90-day post-birth magnetic calibration window."""
    birth   = datetime.datetime(year, month, day,
                                int(hour), int((hour % 1) * 60))
    end     = birth + datetime.timedelta(days=90)
    today   = datetime.datetime.now()
    elapsed = (today - birth).days
    active  = 0 <= elapsed <= 90

    return {
        'birth_date': birth.strftime('%d %B %Y'),
        'window_end': end.strftime('%d %B %Y'),
        'days':       90,
        'active':     active,
        'elapsed':    elapsed if elapsed >= 0 else None,
        'remaining':  max(0, 90 - elapsed) if active else 0,
    }