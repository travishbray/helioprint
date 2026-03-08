# pineal.py  —  Composite Pineal Sensitivity Index + Vivaxis window
import math
import datetime

def calc_pineal_index(positions, lunar_data, solar_data):
    """
    Composite score (0-100) modelling the intensity of the
    cosmic magnetic environment at birth.
    """
    jup = next((p['field_at_earth'] for p in positions if p['name'] == 'Jupiter'), 0)
    sat = next((p['field_at_earth'] for p in positions if p['name'] == 'Saturn'),  0)

    giant_contrib = math.log10(1 + jup) * 20 + math.log10(1 + sat) * 12
    solar_contrib = solar_data['envelope'] * 35
    lunar_contrib = (lunar_data['magnetic_coupling'] / 100) * 25

    raw   = solar_contrib + lunar_contrib + giant_contrib
    score = min(100.0, max(0.0, raw))

    # ── Smart interpretation based on what's actually driving the score ──────
    dominant = max(
        ('solar',  solar_contrib),
        ('lunar',  lunar_contrib),
        ('giants', giant_contrib),
        key=lambda x: x[1]
    )[0]

    solar_phase = solar_data['phase_label']

    if score > 70:
        band = 'Elevated'
        if dominant == 'solar':
            interp = f'Elevated — driven by {solar_phase.lower()} solar activity'
        elif dominant == 'lunar':
            interp = f'Elevated — driven by {lunar_data["phase_name"].lower()} lunar alignment'
        else:
            interp = f'Elevated — driven by Jupiter proximity (field: {jup:.0f})'

    elif score > 40:
        band = 'Moderate'
        if dominant == 'solar':
            interp = f'Moderate — {solar_phase.lower()} sun, balanced environment'
        elif dominant == 'lunar':
            interp = f'Moderate — lunar phase the primary influence'
        else:
            interp = f'Moderate — gas giant fields dominant, quiet sun'

    else:
        band = 'Quiet'
        interp = f'Quiet — solar minimum, weak lunar coupling, distant gas giants'

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
    """
    Calculate the Vivaxis calibration window.
    The magnetic bridging field of birth is theorised to dissolve
    ~90 days after birth. Birth trauma may fix it permanently.
    """
    birth = datetime.datetime(year, month, day, int(hour),
                              int((hour % 1) * 60))
    end   = birth + datetime.timedelta(days=90)

    # Check if window is still open (birth was less than 90 days ago)
    today   = datetime.datetime.now()
    elapsed = (today - birth).days
    active  = 0 <= elapsed <= 90

    return {
        'birth_date':  birth.strftime('%d %B %Y'),
        'window_end':  end.strftime('%d %B %Y'),
        'days':        90,
        'active':      active,
        'elapsed':     elapsed if elapsed >= 0 else None,
        'remaining':   max(0, 90 - elapsed) if active else 0,
    }