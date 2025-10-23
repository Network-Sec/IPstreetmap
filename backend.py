#!/usr/bin/env python3

import ipaddress
import maxminddb
import os
import sys
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
from termcolor import colored

# --- Constants ---
FOLDER_PATH = "./"    # You need to add the path to GeoLite DB
CITY_DB_PATH = os.path.join(FOLDER_PATH, "GeoLite2-City.mmdb")
ASN_DB_PATH = os.path.join(FOLDER_PATH, "GeoLite2-ASN.mmdb")
INITIAL_SAMPLE_SIZE = 75000 

# --- FastAPI App Initialization ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- Helper Functions ---
def load_and_merge_data(city_path, asn_path):
    for path in [city_path, asn_path]:
        if not os.path.exists(path):
            print(colored(f"FATAL ERROR: Database file not found at: {path}", 'red'))
            sys.exit(1)
    print(colored("Loading and merging City and ASN databases for IPv4...", "cyan"))
    
    locations = []
    with maxminddb.open_database(city_path) as city_reader, \
         maxminddb.open_database(asn_path) as asn_reader:
        for network, data in city_reader:
            if network.version != 4:
                continue
            if data and 'location' in data and 'latitude' in data['location'] and 'longitude' in data['location']:
                asn_data = asn_reader.get(network.network_address)
                org = asn_data.get('autonomous_system_organization', 'N/A') if asn_data else 'N/A'
                locations.append({
                    "network": str(network), "latitude": data['location']['latitude'],
                    "longitude": data['location']['longitude'], "country": data.get('country', {}).get('names', {}).get('en', 'N/A'),
                    "city": data.get('city', {}).get('names', {}).get('en', 'N/A'), "org": org
                })
    print(colored(f"--- Database processing complete. Found {len(locations)} IPv4 locations. ---", "green"))
    return locations

# --- Pre-load all data and create the initial sample ---
print("--- Initializing IP Map Viewer ---")
ip_locations_cache = load_and_merge_data(CITY_DB_PATH, ASN_DB_PATH)
print(colored(f"Creating a random sample of {INITIAL_SAMPLE_SIZE} points for the initial map view.", "magenta"))
ip_initial_sample = random.sample(ip_locations_cache, min(INITIAL_SAMPLE_SIZE, len(ip_locations_cache)))

# --- API Endpoints ---
@app.get("/api/ip-data-initial")
async def get_initial_sample():
    """ Serves the smaller, random sample for the fast initial overview. """
    print(colored(f"API request: Serving initial sample of {len(ip_initial_sample)} points.", "blue"))
    return JSONResponse(content=ip_initial_sample)

@app.get("/api/ip-data-by-bounds")
async def get_data_by_bounds(north: float, south: float, east: float, west: float):
    """ Serves full, detailed data for a specific geographic area on demand. """
    bounded_data = [
        loc for loc in ip_locations_cache 
        if south <= loc['latitude'] <= north and west <= loc['longitude'] <= east
    ]
    print(colored(f"API bounds request: Found and serving {len(bounded_data)} points for the detailed view.", "blue"))
    # Still cap to prevent a single view from being too overwhelming
    if len(bounded_data) > 200:
        return JSONResponse(content=random.sample(bounded_data, 200))
    return JSONResponse(content=bounded_data)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Main Execution ---
if __name__ == "__main__":
    print(colored("Starting the Uvicorn server...", "green"))
    uvicorn.run(app, host="127.0.0.1", port=8000)
