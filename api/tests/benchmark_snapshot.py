
import asyncio
import time
import statistics
import os
import tempfile
from unittest.mock import patch

# Setup environment for app import
_tmp_dir = tempfile.mkdtemp()
_tmp_db = os.path.join(_tmp_dir, "benchmark.db")
os.environ["DB_PATH"] = _tmp_db
os.environ["CLIPS_DIR"] = os.path.join(_tmp_dir, "clips")

import httpx

async def measure_heartbeat(stop_event, results):
    interval = 0.001
    lags = []
    while not stop_event.is_set():
        t0 = asyncio.get_event_loop().time()
        await asyncio.sleep(interval)
        t1 = asyncio.get_event_loop().time()
        lags.append(t1 - t0 - interval)
    results['heartbeat_lags'] = lags

async def run_benchmark():
    from app.main import app as fastapi_app, Camera, engine
    import app.main
    from sqlmodel import Session, SQLModel

    # Initialize DB
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(Camera(id=1, name="Bench Cam", ip="127.0.0.1", enabled=True))
        s.commit()

    # Mock _fetch_camera_snapshot to be near-instant
    async def mock_fetch(cam):
        await asyncio.sleep(0.01)
        return b"fake-jpeg"

    with patch('app.main._fetch_camera_snapshot', side_effect=mock_fetch):
        stop_event = asyncio.Event()
        heartbeat_results = {}
        heartbeat_task = asyncio.create_task(measure_heartbeat(stop_event, heartbeat_results))

        transport = httpx.ASGITransport(app=fastapi_app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            print("Starting benchmark (50 concurrent requests)...")
            start_time = time.perf_counter()

            # Launch 50 concurrent requests
            tasks = [client.get("/cameras/1/snapshot.jpg") for _ in range(50)]
            responses = await asyncio.gather(*tasks)

            end_time = time.perf_counter()
            total_time = end_time - start_time

            stop_event.set()
            await heartbeat_task

            lags = heartbeat_results['heartbeat_lags']
            avg_lag = statistics.mean(lags) if lags else 0
            max_lag = max(lags) if lags else 0

            print(f"Total time for 50 requests: {total_time:.4f}s")
            print(f"Average response time: {total_time/50:.4f}s")
            print(f"Average event loop lag: {avg_lag*1000:.4f}ms")
            print(f"Max event loop lag: {max_lag*1000:.4f}ms")

            for r in responses:
                assert r.status_code == 200

if __name__ == "__main__":
    asyncio.run(run_benchmark())
