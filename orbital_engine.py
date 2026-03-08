# orbital_engine.py
# Computes planetary positions and magnetic field contributions
# from any birth date using VSOP87 simplified mean elements.
import math

J2000 = 2451545.0

PLANETS = [
    ("Mercury","☿", 252.2509, 4.092339,  0.387, 0.2056, "#b5a99e", 0.0003),
    ("Venus",  "♀", 181.9798, 1.602136,  0.723, 0.0068, "#e8cfa0", 0.0000),
    ("Earth",  "🜨", 100.4649, 0.985647,  1.000, 0.0167, "#4fa3e0", 1.0000),
    ("Mars",   "♂", 355.4330, 0.524033,  1.524, 0.0934, "#c1440e", 0.0002),
    ("Jupiter","♃",  34.3515, 0.083086,  5.203, 0.0485, "#c88b3a", 18000.),
    ("Saturn", "♄",  50.0775, 0.033460,  9.537, 0.0557, "#e4d191", 600.0),
    ("Uranus", "♅", 314.0550, 0.011769, 19.190, 0.0472, "#7de8e8", 50.0),
    ("Neptune","♆", 304.3487, 0.006020, 30.070, 0.0087, "#4b70dd", 25.0),
]

def date_to_jd(year, month, day, hour=12.0):
    """Convert a calendar date to Julian Date number."""
    Y, M = year, month
    if M <= 2:
        Y -= 1
        M += 12
    A = Y // 100
    B = 2 - A + (A // 4)
    jd = int(365.25*(Y+4716)) + int(30.6001*(M+1)) + day + hour/24 + B - 1524.5
    return jd

def jd_to_date(jd):
    """Convert Julian Date back to a readable date string."""
    import datetime
    dt = datetime.datetime(2000, 1, 1, 12) + datetime.timedelta(jd - J2000)
    return dt.strftime('%d %B %Y  %H:%M UTC')

def get_planet_positions(jd):
    """Compute heliocentric x,y positions for all planets at Julian Date jd."""
    results = []
    earth_x, earth_y = 0.0, 0.0

    for name, sym, L0, L1, a, e, col, mag in PLANETS:
        L = ((L0 + L1 * (jd - J2000)) % 360 + 360) % 360
        angle = math.radians(L)
        r = a * (1 - e*e) / (1 + e * math.cos(angle))
        x = r * math.cos(angle)
        y = r * math.sin(angle)

        if name == 'Earth':
            earth_x, earth_y = x, y

        results.append({
            'name': name, 'symbol': sym, 'longitude': L,
            'x': x, 'y': y, 'radius': r,
            'color': col, 'mag_moment': mag, 'eccentricity': e, 'semi_major': a
        })

    for p in results:
        if p['name'] == 'Earth':
            p['dist_from_earth'] = 0.0
            p['field_at_earth'] = 1.0
            continue
        dx = p['x'] - earth_x
        dy = p['y'] - earth_y
        dist = math.sqrt(dx*dx + dy*dy)
        p['dist_from_earth'] = dist
        p['field_at_earth'] = p['mag_moment'] / (dist * dist)

    return results

def get_sun_longitude(jd):
    """Apparent ecliptic longitude of the Sun (determines zodiac sign)."""
    T = (jd - J2000) / 36525
    M = math.radians(357.5291 + 35999.0503 * T)
    C = (1.9146 - 0.004817*T)*math.sin(M) + 0.019993*math.sin(2*M)
    lon = (280.4665 + 36000.7698*T + C) % 360
    return (lon + 360) % 360

def get_zodiac_sign(longitude):
    """Return the zodiac sign for a given ecliptic longitude."""
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
    idx = int(longitude / 30) % 12
    name, sym, element, modality, ruler = SIGNS[idx]
    return {'name':name,'symbol':sym,'element':element,
            'modality':modality,'ruler':ruler,'degree':longitude%30}