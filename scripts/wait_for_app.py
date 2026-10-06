import time

import httpx

for attempt in range(60):
    try:
        if httpx.get("http://127.0.0.1:8000/api/health", timeout=1).status_code == 200:
            break
    except httpx.HTTPError:
        pass
    time.sleep(0.5)
else:
    raise SystemExit("Local app did not start within 30 seconds")
