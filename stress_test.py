import httpx
import time
import concurrent.futures

API_URL = "http://127.0.0.1:8000/ingest/detection"

def trigger_alert(i):
    payload = {
        "camera_snapshot_url": f"http://192.168.1.10{i}/test.jpg",
        "camera_id": 1,
        "label": "motion",
        "conf": 0.85,
        "snapshot_b64": "dummy",
        "extra_metadata": {"stress": True}
    }
    try:
        r = httpx.post(API_URL, json=payload, timeout=5.0)
        return r.status_code
    except Exception as e:
        return str(e)

print("Starting stress test: 50 concurrent alerts...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(trigger_alert, range(50)))

success = results.count(200)
print(f"Stress test complete. Success: {success}/50")
