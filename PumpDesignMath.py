import math

R = 8.314
P_source = 101325
T = 293.15
TARGET_PRESSURE = 300000  # 3 bar in Pa
CHAMBER_SIDE = 1  # m
COVERAGE = 0.8
CONTACT_ANGLE = math.pi / 3
MAX_SIM = 60 * 60 * 24 * 7  # 1 week in seconds

results = []

for r_mm in range(1, 101):                          # pipe radius 1–100mm
    for power_x10 in range(1, 201):                 # power 0.1–20kW in 0.1 steps
        for rpm in range(500, 5001, 100):           # rpm 500–5000

            power = power_x10 / 10
            r = r_mm / 1000

            torque = (power * 1000) / (rpm * 2 * math.pi / 60)

            pipe_area = math.pi * r ** 2
            shaft_r = 3 * r
            contact_len = 2 * r  # one tube diameter — conservative upper bound
            disp_per_rev = pipe_area * contact_len
            flow_rate = COVERAGE * disp_per_rev * (rpm / 60)

            max_pressure = torque / (pipe_area * shaft_r)

            if max_pressure < TARGET_PRESSURE:
                continue

            # time to reach target: pressure = (P_source * flow_rate * t) / (R * T) * (R * T) / chamber_vol
            # simplifies to: t = TARGET * chamber_vol / (P_source * flow_rate)
            chamber_vol = CHAMBER_SIDE ** 3
            time_to_target = (TARGET_PRESSURE * chamber_vol) / (P_source * flow_rate)

            if time_to_target > MAX_SIM:
                continue

            score = (1 / time_to_target) * (1 / power) * 1e6

            results.append({
                'r_mm': r_mm,
                'power': power,
                'rpm': rpm,
                'torque': torque,
                'flow_rate': flow_rate,
                'max_pressure_bar': max_pressure / 100000,
                'time_to_target_s': time_to_target,
                'score': score
            })

results.sort(key=lambda x: x['score'], reverse=True)

print(f"Total viable combinations: {len(results)}\n")
print(f"{'Rank':<5} {'r(mm)':<7} {'Power(kW)':<11} {'RPM':<7} {'Torque(Nm)':<12} {'Flow(mL/s)':<12} {'MaxP(bar)':<11} {'Time':<12} {'Score':<10}")
print("-" * 95)

def fmt_time(s):
    if s < 60:
        return f"{s:.1f}s"
    elif s < 3600:
        return f"{s/60:.1f}min"
    elif s < 86400:
        return f"{s/3600:.2f}hr"
    else:
        return f"{s/86400:.1f}days"

for i, r in enumerate(results[:50]):
    print(f"{i+1:<5} {r['r_mm']:<7} {r['power']:<11.2f} {r['rpm']:<7} {r['torque']:<12.4f} {r['flow_rate']*1e6:<12.4f} {r['max_pressure_bar']:<11.1f} {fmt_time(r['time_to_target_s']):<12} {r['score']:<10.4f}")

best = results[0]
print(f"\n--- BEST COMBINATION ---")
print(f"Pipe radius:    {best['r_mm']} mm")
print(f"Motor power:    {best['power']} kW")
print(f"RPM:            {best['rpm']}")
print(f"Torque:         {best['torque']:.4f} Nm")
print(f"Flow rate:      {best['flow_rate']*1e6:.4f} mL/s")
print(f"Max pressure:   {best['max_pressure_bar']:.1f} bar")
print(f"Time to 3 bar:  {fmt_time(best['time_to_target_s'])}")
print(f"Score:          {best['score']:.4f}")