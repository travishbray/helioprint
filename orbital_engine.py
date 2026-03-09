# orbital_engine.py
# Planetary positions and magnetic field contributions.
# Magnetic field law: dipole B ∝ moment × cos(tilt) / r³
import math

J2000 = 2451545.0

# VSOP87 simplified mean elements:
# (name, symbol, L0, L1, semi-major axis AU, eccentricity, hex colour)
PLANETS = [
    ("Mercury","☿", 252.2509, 4.092339,  0.387, 0.2056, "#b5a99e"),
    ("Venus",  "♀", 181.9798, 1.602136,  0.723, 0.0068, "#e8cfa0"),
    ("Earth",  "🜨", 100.4649, 0.985647,  1.000, 0.0167, "#4fa3e0"),
    ("Mars",   "♂", 355.4330, 0.524033,  1.524, 0.0934, "#c1440e"),
    ("Jupiter","♃",  34.3515, 0.083086,  5.203, 0.0485, "#c88b3a"),
    ("Saturn", "♄",  50.0775, 0.033460,  9.537, 0.0557, "#e4d191"),
    ("Uranus", "♅", 314.0550, 0.011769, 19.190, 0.0472, "#7de8e8"),
    ("Neptune","♆", 304.3487, 0.006020, 30.070, 0.0087, "#4b70dd"),
]

# Magnetic properties from NASA planetary fact sheets / Connerney (2007)
# moment: dipole moment relative to Earth = 1.0
# tilt:   angle between magnetic dipole axis and rotation axis (degrees)
# character: qualitative description of field type
# polarity: normal = same as Earth, reverse = opposite
PLANET_MAGNETICS = {
    "Mercury": {"moment": 0.0006,  "tilt":  14.0, "character": "Weak · aligned",     "polarity": "normal"},
    "Venus":   {"moment": 0.00003, "tilt":   0.0, "character": "Induced only",        "polarity": "none"},
    "Earth":   {"moment": 1.0,     "tilt":  11.5, "character": "Coherent dipole",     "polarity": "normal"},
    "Mars":    {"moment": 0.0002,  "tilt":   0.0, "character": "Crustal remnants",    "polarity": "none"},
    "Jupiter": {"moment": 19500.,  "tilt":   9.6, "character": "Dominant · reverse",  "polarity": "reverse"},
    "Saturn":  {"moment": 578.,    "tilt":   0.0, "character": "Perfect dipole",      "polarity": "normal"},
    "Uranus":  {"moment": 48.,     "tilt":  58.6, "character": "Anomalous · offset",  "polarity": "reverse"},
    "Neptune": {"moment": 26.,     "tilt":  46.8, "character": "Anomalous · offset",  "polarity": "normal"},
}

def date_to_jd(year, month, day, hour=12.0):
    """Convert a calendar date to Julian Date."""
    Y, M = year, month
    if M <= 2:
        Y -= 1
        M += 12
    A = Y // 100
    B = 2 - A + (A // 4)
    return int(365.25*(Y+4716)) + int(30.6001*(M+1)) + day + hour/24 + B - 1524.5

def jd_to_date(jd):
    """Convert Julian Date to readable string."""
    import datetime
    dt = datetime.datetime(2000, 1, 1, 12) + datetime.timedelta(jd - J2000)
    return dt.strftime('%d %B %Y  %H:%M UTC')

def get_planet_positions(jd):
    """
    Compute heliocentric positions and magnetic field at Earth for all planets.
    Uses correct magnetic dipole field law: B ∝ moment × cos(tilt) / r³
    The cos(tilt) factor accounts for the projection of the dipole axis
    toward Earth — highly tilted fields (Uranus, Neptune) couple less efficiently.
    """
    results = []
    earth_x, earth_y = 0.0, 0.0

    for name, sym, L0, L1, a, e, col in PLANETS:
        L     = ((L0 + L1 * (jd - J2000)) % 360 + 360) % 360
        angle = math.radians(L)
        r     = a * (1 - e*e) / (1 + e * math.cos(angle))
        x     = r * math.cos(angle)
        y     = r * math.sin(angle)

        if name == 'Earth':
            earth_x, earth_y = x, y

        mag = PLANET_MAGNETICS[name]
        results.append({
            'name':      name,
            'symbol':    sym,
            'longitude': L,
            'x': x, 'y': y,
            'radius':    r,
            'color':     col,
            'mag_moment':  mag['moment'],
            'mag_tilt':    mag['tilt'],
            'mag_character': mag['character'],
            'mag_polarity':  mag['polarity'],
            'eccentricity': e,
            'semi_major':   a,
        })

    # Compute magnetic field at Earth for each planet
    for p in results:
        if p['name'] == 'Earth':
            p['dist_from_earth'] = 0.0
            p['field_at_earth']  = 1.0
            continue

        dx   = p['x'] - earth_x
        dy   = p['y'] - earth_y
        dist = math.sqrt(dx*dx + dy*dy)  # AU

        # Dipole field: B ∝ moment / r³
        # Orientation factor: cos(tilt) — how aligned the dipole is toward Earth
        # For Uranus (58.6°) this is 0.52; for Saturn (0°) it's 1.0
        tilt_factor = math.cos(math.radians(p['mag_tilt']))
        raw_field   = (p['mag_moment'] * tilt_factor) / (dist ** 3)

        p['dist_from_earth'] = dist
        p['field_at_earth']  = max(0.0, raw_field)

    return results

def get_sun_longitude(jd):
    """Apparent ecliptic longitude of the Sun."""
    T   = (jd - J2000) / 36525
    M   = math.radians(357.5291 + 35999.0503 * T)
    C   = (1.9146 - 0.004817*T)*math.sin(M) + 0.019993*math.sin(2*M)
    lon = (280.4665 + 36000.7698*T + C) % 360
    return (lon + 360) % 360

def get_zodiac_sign(longitude):
    """Return zodiac sign data for an ecliptic longitude."""
    SIGNS = [
        ("Aries","♈","Fire","Cardinal","Mars"),
        ("Taurus","♉","Earth","Fixed","Venus"),
        ("Gemini","♊","Air","Mutable","Mercury"),
        ("Cancer","♋","Water","Cardinal","Moon"),
        ("Leo","♌","Fire","Fixed","Sun"),
        ("Virgo","♍","Earth","Mutable","Mercury"),
        ("Libra","♎","Air","Cardinal","Venus"),
        ("Scorpio","♏","Water","Fixed","Mars"),
        ("Sagittarius","♐","Fire","Mutable","Jupiter"),
        ("Capricorn","♑","Earth","Cardinal","Saturn"),
        ("Aquarius","♒","Air","Fixed","Uranus"),
        ("Pisces","♓","Water","Mutable","Neptune"),
    ]
    idx  = int(longitude / 30) % 12
    name, sym, element, modality, ruler = SIGNS[idx]
    return {
        'name': name, 'symbol': sym, 'element': element,
        'modality': modality, 'ruler': ruler, 'degree': longitude % 30
    }