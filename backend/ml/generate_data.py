import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ================================
# CONFIGURATION
# ================================
ROWS = 10000
START_TIME = datetime(2025, 1, 1, 0, 0, 0)
OUTPUT_FILE = "power_line_sensor_data.csv"

np.random.seed(42)

# ================================
# DATA GENERATION
# ================================

street_ids = np.random.randint(100, 200, ROWS)
line_ids = np.random.randint(1, 50, ROWS)

voltage = np.random.normal(230, 10, ROWS).round(2)

current_in = np.random.normal(10, 2, ROWS).round(2)
current_out = (current_in - np.random.normal(0.2, 0.5, ROWS)).round(2)

leakage_current = np.abs((current_in - current_out)).round(2)

load_kw = (voltage * current_out / 1000).round(2)

power_factor = np.random.uniform(0.7, 1.0, ROWS).round(2)

temperature_c = np.random.normal(45, 15, ROWS).round(2)
humidity = np.random.uniform(30, 90, ROWS).round(2)

time_slot = [START_TIME + timedelta(minutes=5 * i) for i in range(ROWS)]

# ================================
# FAULT LOGIC (VERY IMPORTANT)
# ================================

fault = []

for i in range(ROWS):
    if leakage_current[i] > 1.5 and temperature_c[i] > 70:
        fault.append("CRITICAL_LEAKAGE")
    elif leakage_current[i] > 1.0:
        fault.append("LEAKAGE_WARNING")
    elif voltage[i] < 200 or voltage[i] > 260:
        fault.append("VOLTAGE_FAULT")
    elif current_in[i] - current_out[i] > 1.0:
        fault.append("CURRENT_IMBALANCE")
    elif temperature_c[i] > 80:
        fault.append("OVERHEAT")
    else:
        fault.append("NORMAL")

# ================================
# CREATE DATAFRAME
# ================================

df = pd.DataFrame({
    "street_id": street_ids,
    "line_id": line_ids,
    "voltage": voltage,
    "current_in": current_in,
    "current_out": current_out,
    "leakage_current": leakage_current,
    "load_kw": load_kw,
    "power_factor": power_factor,
    "temperature_c": temperature_c,
    "humidity": humidity,
    "time_slot": time_slot,
    "fault": fault
})

# ================================
# SAVE FILE
# ================================

df.to_csv(OUTPUT_FILE, index=False)

print("✅ Dataset generated successfully!")
print(f"📄 File saved as: {OUTPUT_FILE}")
print(f"📊 Total rows: {len(df)}")
