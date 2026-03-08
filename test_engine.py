# test_engine.py  —  Verify your Phase 1 engine
from orbital_engine import date_to_jd, get_planet_positions, get_sun_longitude, get_zodiac_sign, jd_to_date
from lunar import get_lunar_data
from solar_cycle import get_solar_cycle_data
from pineal import calc_pineal_index

def run_report(label, year, month, day, hour=12):
    print(f"\n{'='*55}")
    print(f"  HELIOPRINT: {label}")
    print(f"{'='*55}")

    jd = date_to_jd(year, month, day, hour)
    print(f"  Julian Date  : {jd:.4f}")
    print(f"  Calendar Date: {jd_to_date(jd)}")

    # Sun
    sun_lon = get_sun_longitude(jd)
    sign = get_zodiac_sign(sun_lon)
    print(f"\n  ☀  Sun: {sun_lon:.2f}°  →  {sign['symbol']} {sign['name']} ({sign['element']})")

    # Moon
    moon = get_lunar_data(jd)
    print(f"  {moon['phase_symbol']}  Moon: {moon['phase_name']}  (age {moon['age_days']:.1f} days,  illum {moon['illumination']*100:.0f}%)")
    print(f"       Moon in {moon['moon_sign_symbol']} {moon['moon_sign']}")
    print(f"       Tidal Index: {moon['tidal_index']:.1f}   Magnetic Coupling: {moon['magnetic_coupling']:.1f}")

    # Solar cycle
    sol = get_solar_cycle_data(jd)
    print(f"\n  ☀  Solar Cycle {sol['cycle_number']}: {sol['phase_label']}  ({sol['phase']*100:.1f}% through)")
    print(f"       Est. SSN: {sol['est_ssn']}   Kp proxy: {sol['kp_proxy']}")

    # Planets
    positions = get_planet_positions(jd)
    print(f"\n  {'Planet':<12} {'Longitude':>10}  {'Dist (AU)':>10}  {'Field @ Earth':>14}")
    print(f"  {'-'*50}")
    for p in positions:
        dist  = '—' if p['name'] == 'Earth' else f"{p['dist_from_earth']:.3f}"
        field = '— (origin)' if p['name'] == 'Earth' else f"{p['field_at_earth']:.3e}"
        print(f"  {p['symbol']} {p['name']:<10} {p['longitude']:>10.2f}°  {dist:>10}  {field:>14}")

    # Pineal
    pi = calc_pineal_index(positions, moon, sol)
    print(f"\n  ◈  PINEAL INDEX: {pi['score']:.1f} / 100  [{pi['band']}]")
    print(f"     {pi['interpretation']}")
    print(f"     Solar: {pi['solar']}  Lunar: {pi['lunar']}  Giants: {pi['giants']}")
    print(f"     Dominant driver: {pi['dominant'].upper()}")

    # Vivaxis window
    from pineal import get_vivaxis_window
    viv = get_vivaxis_window(year, month, day, hour)
    print(f"\n  ◎  VIVAXIS WINDOW")
    print(f"     Birth       : {viv['birth_date']}")
    print(f"     Window closes: {viv['window_end']}  (+90 days)")
    if viv['active']:
        print(f"     ⚡ WINDOW STILL OPEN — {viv['remaining']} days remaining")
    else:
        print(f"     Window closed {viv['elapsed']} days after birth")

if __name__ == '__main__':
    # Test date — known result to verify engine
    run_report('Summer Solstice 1990', 1990, 6, 21, 14)

    # ── YOUR BIRTH DATE ──────────────────────────────────
    # Change the numbers below and run again:
    run_report('My Birth',1977, 9, 6, 4)  # YYYY, M, D, H (24h format)
    # ─────────────────────────────────────────────────────
    from noaa_data import get_geomagnetic_conditions
    print(f"\n  🌍  LIVE CONDITIONS RIGHT NOW:")
    cond = get_geomagnetic_conditions()
    kp   = cond['kp']
    wind = cond['solar_wind']
    if kp['status'] == 'live':
        print(f"       Kp: {kp['kp']}  —  {kp['label']}")
        if wind['speed']:
            print(f"       Solar wind: {wind['speed']:.0f} km/s  —  {wind['wind_label']}")
    else:
        print(f"       NOAA offline — no live data available")
    print(f"\n  ✅  Engine verified. Change 'My Birth' date above to yours!\n")
    