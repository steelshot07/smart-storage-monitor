from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
import joblib
import numpy as np
import subprocess
import json
import os
import shutil

def find_smartctl():
    path = shutil.which("smartctl")
    if path:
        return path
    
    # Windows fallback — check common install location
    fallback = r'C:\Program Files\smartmontools\bin\smartctl.exe'
    if os.path.exists(fallback):
        return fallback
    
    # Linux/Mac fallback
    unix_fallback = '/usr/bin/smartctl'
    if os.path.exists(unix_fallback):
        return unix_fallback
        
    raise FileNotFoundError("smartctl not found. Please install smartmontools.")

SMARTCTL = find_smartctl()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load('model.pkl')
features = joblib.load('features.pkl')

# CHANGED: now handles both NVMe and SATA/USB drives
def get_smart_data(device_path):
    try:
        result = subprocess.run(
            [SMARTCTL, '-a', device_path, '-j'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        nvme = data.get('nvme_smart_health_information_log', {})
        ata = data.get('ata_smart_attributes', {}).get('table', [])

        def get_ata(attr_id):
            for a in ata:
                if a['id'] == attr_id:
                    return a['raw']['value']
            return 0

        if nvme:
            return {
                'type': 'NVMe',
                'temperature': data.get('temperature', {}).get('current', 40),
                'available_spare': nvme.get('available_spare', 100),
                'percentage_used': nvme.get('percentage_used', 0),
                'power_on_hours': nvme.get('power_on_hours', 0),
                'unsafe_shutdowns': nvme.get('unsafe_shutdowns', 0),
                'media_errors': nvme.get('media_errors', 0),
            }
        else:
            return {
                'type': 'SATA',
                'temperature': data.get('temperature', {}).get('current', 40),
                'available_spare': 100,
                'percentage_used': 0,
                'power_on_hours': get_ata(9),
                'unsafe_shutdowns': 0,
                'media_errors': get_ata(187),
                'reallocated_sectors': get_ata(5),
                'pending_sectors': get_ata(197),
            }
    except Exception as e:
        print(f"smartctl error for {device_path}: {e}")
        return None

# CHANGED: scans all connected drives automatically
def scan_drives():
    try:
        result = subprocess.run(
            [SMARTCTL, '--scan', '-j'],
            capture_output=True, text=True, timeout=10
        )
        print("SCAN OUTPUT:", result.stdout)  # ← add this
        print("SCAN ERROR:", result.stderr)   # ← and this
        data = json.loads(result.stdout)
        return [d['name'] for d in data.get('devices', [])]
    except Exception as e:
        print(f"smartctl scan error: {e}")
        return ['/dev/sda']

# CHANGED: uses real NVMe metrics instead of old SMART attributes
def predict_failure_nvme(smart):
    if not smart:
        return {
            "riskPercent": 0,
            "riskLabel": "Unknown",
            "riskMessage": "Could not read drive data"
        }

    risk = 0
    risk += smart['percentage_used'] * 0.5

    if smart['available_spare'] < 50:
        risk += 30
    elif smart['available_spare'] < 80:
        risk += 10

    risk += min(smart['media_errors'] * 10, 40)
    risk += min(smart['unsafe_shutdowns'] * 0.1, 10)
    risk = round(min(risk, 100), 1)

    if risk >= 70:
        label = "Critical"
        message = "Back up immediately — similar drives fail within 1-4 weeks"
    elif risk >= 50:
        label = "High risk"
        message = "Back up your data soon — failure possible within 1-8 weeks"
    elif risk >= 20:
        label = "Moderate risk"
        message = "Keep an eye on this drive — no immediate action needed"
    else:
        label = "Low risk"
        message = "Your drive looks healthy"

    return {"riskPercent": risk, "riskLabel": label, "riskMessage": message}

def predict_failure_sata(smart):
    if not smart:
        return {
            "riskPercent": 0,
            "riskLabel": "Unknown", 
            "riskMessage": "Could not read drive data"
        }

    # feed real SMART attributes into the ML model
    smart_values = [
        smart.get('reallocated_sectors', 0),  # smart_5
        smart.get('power_on_hours', 0),        # smart_9
        smart.get('media_errors', 0),          # smart_187
        0,                                      # smart_188 (not always available)
        smart.get('temperature', 40),          # smart_190
        smart.get('pending_sectors', 0),       # smart_197
        0,                                      # smart_198
    ]

    X = np.array(smart_values).reshape(1, -1)
    prob = model.predict_proba(X)[0][1]
    risk = round(prob * 100, 1)

    if risk >= 70:
        label = "Critical"
        message = "Back up immediately — similar drives fail within 1-4 weeks"
    elif risk >= 50:
        label = "High risk"
        message = "Back up your data soon — failure possible within 1-8 weeks"
    elif risk >= 20:
        label = "Moderate risk"
        message = "Keep an eye on this drive — no immediate action needed"
    else:
        label = "Low risk"
        message = "Your drive looks healthy"

    return {"riskPercent": risk, "riskLabel": label, "riskMessage": message}

# CHANGED: loops over real drives from smartctl scan, not just partitions
@app.get("/devices")
def get_devices():
    devices = []
    drive_paths = scan_drives()
    partitions = list(psutil.disk_partitions())

    for i, drive_path in enumerate(drive_paths):
        try:
            if i >= len(partitions):
                break

            partition = partitions[i]
            usage = psutil.disk_usage(partition.mountpoint)
            smart = get_smart_data(drive_path)   
            if smart['type'] == 'NVMe':
                prediction = predict_failure_nvme(smart)
            else:
                prediction = predict_failure_sata(smart)

            devices.append({
                "id": i + 1,
                "name": partition.device.replace("\\", "") + " Drive",
                "type": smart['type'] if smart else "Unknown",
                "temperature": smart['temperature'] if smart else 40,
                "usedGB": round(usage.used / (1024**3)),
                "totalGB": round(usage.total / (1024**3)),
                "lifespan": 100 - smart['percentage_used'] if smart else 80,
                "powerOnHours": smart['power_on_hours'] if smart else 0,
                "mediaErrors": smart['media_errors'] if smart else 0,
                "availableSpare": smart['available_spare'] if smart else 100,
                "riskPercent": prediction["riskPercent"],
                "riskLabel": prediction["riskLabel"],
                "riskMessage": prediction["riskMessage"],
            })
        except Exception as e:
            print(f"Error processing {drive_path}: {e}")
            continue

    return devices


@app.get("/health")
def health_check():
    drive_paths = scan_drives()
    smart_ok = []
    smart_failed = []

    for path in drive_paths:
        smart = get_smart_data(path)
        if smart:
            smart_ok.append(path)
        else:
            smart_failed.append(path)

    return {
        "status": "ok",
        "smartctl_available": SMARTCTL is not None,
        "drives_detected": len(drive_paths),
        "drives_readable": len(smart_ok),
        "drives_failed": len(smart_failed),
        "failed_paths": smart_failed,
    }