# IPstreetmap
Quick and easy world map of IPV4 addresses

## Install
Just clone and run the backend, open `localhost:8000` in browser. 

## Dependencies
You need GeoLite2 City and ASN mmdb in same folder, or adjust path in backend.py

## Run
```bash
$ python3 backend.py
--- Initializing IP Map Viewer ---
Loading and merging City and ASN databases for IPv4...
--- Database processing complete. Found 2607235 IPv4 locations. ---
Creating a random sample of 75000 points for the initial map view.
Starting the Uvicorn server...
INFO:     Started server process [14931]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:32721 - "GET / HTTP/1.1" 200 OK
API request: Serving initial sample of 75000 points.
INFO:     127.0.0.1:32744 - "GET /api/ip-data-initial HTTP/1.1" 200 OK
INFO:     127.0.0.1:32744 - "GET /favicon.ico HTTP/1.1" 404 Not Found
API bounds request: Found and serving 9408 points for the detailed view.
INFO:     127.0.0.1:32817 - "GET /api/ip-data-by-bounds?north=48.977751194284686&south=47.60918539110019&east=13.265317999713854&west=9.21273621260448 HTTP/1.1" 200 OK
```

