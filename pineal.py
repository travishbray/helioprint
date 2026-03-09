# pineal.py  —  Composite Pineal Sensitivity Index + Vivaxis window
# Updated to use corrected 1/r³ dipole field law and all 4 outer planets.
import math
import datetime

def calc_pineal_index(positions, lunar_data, solar_data):
    """
    Composite score (0-100) from solar, lunar, and gas giant contributions.

    Gas giant field scaling (log10, tuned to 1/r³ values):
      Jupiter max at opposition (~4 AU): field ≈ 305  → log10(306)×15 ≈ 37
      Saturn  max at opposition (~8 AU): field ≈ 1.1  → log10(2.1)×8  ≈ 2.6
      Uranus/Neptune: small but non-zero contributions included.
    """
    def field(name):
        p = next((x for x in positions if x['name'] == name), None)
        return p['field_at_earth'] if p else 0.0

    jup = field('Jupiter')
    sat = field('Saturn')
    ura = field('Uranus')
    nep = field('Neptune')

    # Log-scaled to handle wide dynamic range (1/r³ values span many orders)
    giant_contrib = (
        math.log10(1 + jup) * 15 +
        math.log10(1 + sat) * 8  +
        math.log10(1 + ura) * 5  +
        math.log10(1 + nep) * 3
    )

    solar_contrib = solar_data['envelope'] * 35
    lunar_contrib = (lunar_data['magnetic_coupling'] / 100) * 25

    raw   = solar_contrib + lunar_contrib + giant_contrib
    score = min(100.0, max(0.0, raw))

    # Dominant driver
    dominant = max(
        ('solar',  solar_contrib),
        ('lunar',  lunar_contrib),
        ('giants', giant_contrib),
        key=lambda x: x[1]
    )[0]

    solar_phase = solar_data['phase_label']

    # Smart interpretation — no more generic labels
    if score > 70:
        band = 'Elevated'
        if dominant == 'solar':
            interp = f'Elevated — {solar_phase.lower()} driving strong geomagnetic activity'
        elif dominant == 'lunar':
            interp = f'Elevated — {lunar_data["phase_name"].lower()} lunar alignment dominant'
        else:
            jup_dist = next((p["dist_from_earth"] for p in positions if p["name"]=="Jupiter"), 0)
            interp = f'Elevated — Jupiter proximity dominant (field: {jup:.1f}, dist: {jup_dist:.2f} AU)'
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