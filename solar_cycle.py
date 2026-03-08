# solar_cycle.py  —  Solar cycle phase and activity model
import math

# Historical data from SILSO / Royal Observatory Belgium
# Each entry: (cycle_number, jd_of_minimum, peak_smoothed_ssn)
SC_MINIMA = [
    (17, 2431090, 151),   # 1944 Feb
    (18, 2434743, 201),   # 1954 Apr
    (19, 2438747, 190),   # 1964 Oct
    (20, 2443310, 157),   # 1976 Jun
    (21, 2446690, 158),   # 1986 Sep
    (22, 2450300, 212),   # 1996 Aug
    (23, 2454834, 120),   # 2008 Dec
    (24, 2458818, 115),   # 2019 Dec
    (25, 2462943, 137),   # ~2030 predicted
]

def get_solar_cycle_data(jd):
    """Find which solar cycle the birth falls in, and the phase within it."""
    idx = len(SC_MINIMA) - 2
    for i in range(len(SC_MINIMA) - 1):
        if SC_MINIMA[i][1] <= jd < SC_MINIMA[i+1][1]:
            idx = i
            break
    if jd < SC_MINIMA[0][1]:
        idx = 0

    s, e = SC_MINIMA[idx], SC_MINIMA[idx + 1]
    phase = min(1.0, max(0.0, (jd - s[1]) / (e[1] - s[1])))

    # Skewed envelope: fast rise (~4yr), slow decline (~7yr)
    if phase < 0.4:
        envelope = math.pow(phase / 0.4, 1.5)
    else:
        envelope = math.pow(1 - (phase - 0.4) / 0.6, 0.8)

    if phase < 0.05:   label = 'Solar Minimum'
    elif phase < 0.40: label = 'Rising Phase'
    elif phase < 0.55: label = 'Solar Maximum'
    elif phase < 0.85: label = 'Declining Phase'
    else:              label = 'Pre-Minimum'

    return {
        'cycle_number':   s[0],
        'phase':          phase,
        'envelope':       envelope,
        'est_ssn':        int(envelope * s[2]),
        'kp_proxy':       round(1 + envelope * 4, 1),
        'phase_label':    label,
        'cycle_peak_ssn': s[2],
    }