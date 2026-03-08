# lunar.py  —  Moon phase and tidal magnetic index
# Algorithm: Jean Meeus 'Astronomical Algorithms' Chapter 47
import math
from orbital_engine import J2000

PHASE_NAMES = [
    (1.85,  'New Moon',        '🌑'),
    (7.38,  'Waxing Crescent', '🌒'),
    (9.22,  'First Quarter',   '🌓'),
    (14.77, 'Waxing Gibbous',  '🌔'),
    (16.61, 'Full Moon',       '🌕'),
    (22.15, 'Waning Gibbous',  '🌖'),
    (23.99, 'Last Quarter',    '🌗'),
    (29.53, 'Waning Crescent', '🌘'),
]

def get_lunar_data(jd):
    T  = (jd - J2000) / 36525
    D  = ((297.85036 + 445267.111480*T) % 360 + 360) % 360
    M  = ((357.52772 +  35999.050340*T) % 360 + 360) % 360
    Mp = ((134.96298 + 477198.867398*T) % 360 + 360) % 360
    L0 = ((218.31650 + 481267.88130 *T) % 360 + 360) % 360

    moon_lon = (L0
        + 6.289 * math.sin(math.radians(Mp))
        - 1.274 * math.sin(math.radians(2*D - Mp))
        + 0.658 * math.sin(math.radians(2*D))
        - 0.214 * math.sin(math.radians(2*Mp))
        - 0.186 * math.sin(math.radians(M)))
    moon_lon = (moon_lon % 360 + 360) % 360

    phase_angle  = D % 360
    age          = (phase_angle / 360) * 29.53059
    illumination = (1 - math.cos(math.radians(phase_angle))) / 2

    phase_name, phase_symbol = 'Waning Crescent', '🌘'
    for limit, name, sym in PHASE_NAMES:
        if age < limit:
            phase_name, phase_symbol = name, sym
            break

    tidal_index = abs(math.cos(math.radians(phase_angle / 2))) * 100
    lmag = (((1 + math.cos(math.radians(phase_angle))) / 2) * 50 +
            ((1 + math.cos(math.radians(phase_angle - 180))) / 2) * 50)

    SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
             'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    SYMS  = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
    sign_idx = int(moon_lon / 30) % 12

    return {
        'phase_angle':      phase_angle,
        'age_days':         age,
        'illumination':     illumination,
        'moon_longitude':   moon_lon,
        'phase_name':       phase_name,
        'phase_symbol':     phase_symbol,
        'tidal_index':      tidal_index,
        'magnetic_coupling': lmag,
        'moon_sign':        SIGNS[sign_idx],
        'moon_sign_symbol': SYMS[sign_idx],
    }