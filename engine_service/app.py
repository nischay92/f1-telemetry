from flask import Flask, jsonify
import threading
import time
import random
import logging
import math

app = Flask(__name__)

logging.basicConfig(filename='./logs/engine.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Time counter for sinusoidal pattern
time_counter = 0

def simulate_engine_temp(t):
    base = 100 + 10 * math.sin(0.05 * t)  # Reduced swing (90-110°C)
    noise = random.uniform(-1, 1)
    return round(base + noise, 2)

def simulate_engine_rpm(t):
    base = 6000 + 1500 * math.sin(0.1 * t)  # RPM 4500-7500
    noise = random.uniform(-100, 100)
    return round(base + noise)

def generate_engine_logs():
    global time_counter
    while True:
        temp = simulate_engine_temp(time_counter)
        rpm = simulate_engine_rpm(time_counter)
        log_message = f"ENGINE | Temp: {temp} | RPM: {rpm}"
        logging.info(log_message)
        time.sleep(5)
        time_counter += 1

threading.Thread(target=generate_engine_logs, daemon=True).start()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Engine service running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
