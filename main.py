from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import threading
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

last_known = {
    "price": "---",
    "lower_pivot": "---",
    "lower_conf": "",
    "upper_pivot": "---",
    "upper_conf": ""
}

lock = threading.Lock()

@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

@app.get("/pivot")
def get_data():
    global last_known
    try:
        with lock:
            # Ensure this works on Render and locally
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "pivot_data.json")

            with open(json_path, "r") as f:
                data = json.load(f)

            price = data.get("price") or last_known["price"]
            lower_pivot = data.get("lower_pivot") or last_known["lower_pivot"]
            upper_pivot = data.get("upper_pivot") or last_known["upper_pivot"]

            lower_conf = data.get("lower_conf") if lower_pivot not in [None, "", "NONE", "None", "---"] else ""
            upper_conf = data.get("upper_conf") if upper_pivot not in [None, "", "NONE", "None", "---"] else ""

            last_known = {
                "price": price,
                "lower_pivot": lower_pivot,
                "lower_conf": lower_conf,
                "upper_pivot": upper_pivot,
                "upper_conf": upper_conf
            }

    except Exception as e:
        print("Failed to read JSON file:", e)

    return last_known
