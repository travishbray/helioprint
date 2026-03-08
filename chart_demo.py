# chart_demo.py  —  First Helioprint visualisation
import math
import matplotlib.pyplot as plt
import numpy as np
from orbital_engine import date_to_jd, get_planet_positions, get_sun_longitude, get_zodiac_sign, J2000, PLANETS
from lunar import get_lunar_data
from solar_cycle import get_solar_cycle_data
from pineal import calc_pineal_index

# ── CHANGE THIS TO YOUR BIRTH DATE ──────────────────────
YEAR, MONTH, DAY, HOUR = 1977, 9, 6, 4
# ────────────────────────────────────────────────────────

jd        = date_to_jd(YEAR, MONTH, DAY, HOUR)
positions = get_planet_positions(jd)
moon      = get_lunar_data(jd)
sol       = get_solar_cycle_data(jd)
pi        = calc_pineal_index(positions, moon, sol)
sun_lon   = get_sun_longitude(jd)
sign      = get_zodiac_sign(sun_lon)

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig = plt.figure(figsize=(14, 9), facecolor='#0d0d1a')
fig.suptitle(f'HELIOPRINT  ·  {DAY} {MONTHS[MONTH-1]} {YEAR}',
             color='#d4a853', fontsize=14, fontweight='bold', y=0.98)

# ── Panel 1: Orrery ──────────────────────────────────────────────────────────
ax1 = fig.add_subplot(1, 3, 1, facecolor='#06060f')
ax1.set_aspect('equal')
ax1.set_title('Heliocentric Map', color='#d4a853', pad=8)
ax1.tick_params(colors='#444')

PLANET_COLORS = {p[0]: p[6] for p in PLANETS}

# Orbit rings
for p in PLANETS:
    theta = np.linspace(0, 2*math.pi, 200)
    ax1.plot(p[4]*np.cos(theta), p[4]*np.sin(theta), color='#ffffff', alpha=0.06, lw=0.4)

# Sun
ax1.scatter(0, 0, c='#ffd060', s=140, zorder=5)
ax1.annotate('☀', (0, 0.8), color='#ffd060', fontsize=8, ha='center')

# Planets
for p in positions:
    col  = PLANET_COLORS.get(p['name'], '#ffffff')
    size = 80 if p['name'] == 'Jupiter' else 60 if p['name'] == 'Saturn' else 35
    ax1.scatter(p['x'], p['y'], c=col, s=size, zorder=4)
    ax1.annotate(p['symbol'], (p['x'], p['y']), color=col,
                 fontsize=7, textcoords='offset points', xytext=(4, 4))

ax1.set_xlim(-32, 32)
ax1.set_ylim(-32, 32)
for spine in ax1.spines.values():
    spine.set_color('#333')

# ── Panel 2: Birth summary card ──────────────────────────────────────────────
ax2 = fig.add_subplot(1, 3, 2, facecolor='#0d0d1a')
ax2.axis('off')
ax2.set_title('Birth Signature', color='#d4a853', pad=8)

lines = [
    (0.90, f"{sign['symbol']} {sign['name'].upper()}",                    '#d4a853', 16, 'bold'),
    (0.80, f"Sun {sun_lon:.1f}°  ·  {sign['element']}  ·  {sign['modality']}", '#aaaacc',  9, 'normal'),
    (0.70, f"{moon['phase_symbol']}  {moon['phase_name']}",               '#d4c090', 12, 'bold'),
    (0.62, f"Moon in {moon['moon_sign_symbol']} {moon['moon_sign']}",     '#aaaacc',  9, 'normal'),
    (0.54, f"Illumination: {moon['illumination']*100:.0f}%  ·  Age: {moon['age_days']:.1f}d", '#aaaacc', 9, 'normal'),
    (0.44, f"Solar Cycle {sol['cycle_number']}",                          '#e8a030', 12, 'bold'),
    (0.36, sol['phase_label'],                                             '#e8a030',  9, 'normal'),
    (0.28, f"Est. SSN: {sol['est_ssn']}  ·  Kp proxy: {sol['kp_proxy']}",'#aaaacc',  9, 'normal'),
    (0.16, f"◈  Pineal Index: {pi['score']:.0f} / 100",                  '#d4a853', 14, 'bold'),
    (0.08, pi['interpretation'][:45],                                      '#888899',  7, 'normal'),
]
for y_pos, text, col, size, weight in lines:
    ax2.text(0.5, y_pos, text, transform=ax2.transAxes,
             ha='center', va='center', color=col, fontsize=size, fontweight=weight)

# ── Panel 3: Solar cycle curve ───────────────────────────────────────────────
ax3 = fig.add_subplot(1, 3, 3, facecolor='#06060f')
ax3.set_title('Solar Cycle Profile', color='#d4a853', pad=8)

t   = np.linspace(0, 1, 200)
env = np.where(t < 0.4,
               np.power(t / 0.4, 1.5),
               np.power(1 - (t - 0.4) / 0.6, 0.8))

ax3.fill_between(t * 100, env * sol['cycle_peak_ssn'], alpha=0.2, color='#d4a853')
ax3.plot(t * 100, env * sol['cycle_peak_ssn'], color='#d4a853', lw=1.5)
ax3.axvline(sol['phase'] * 100, color='#4fa3e0', lw=1.5, ls='--', label=f"Birth ({sol['phase']*100:.0f}%)")
ax3.set_xlabel('Cycle %',      color='#888')
ax3.set_ylabel('Sunspot Number', color='#888')
ax3.tick_params(colors='#666')
ax3.legend(facecolor='#1a1a2e', labelcolor='#d4a853', fontsize=8)
for spine in ax3.spines.values():
    spine.set_color('#333')

plt.tight_layout()
plt.savefig('helioprint_chart.png', dpi=150, bbox_inches='tight', facecolor='#0d0d1a')
plt.show()
print("✅  Chart saved as helioprint_chart.png")