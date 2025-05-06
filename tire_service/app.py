from flask import Flask, jsonify
import threading
import time
import random
import logging
import math

app = Flask(__name__)

logging.basicConfig(filename='./logs/tire.log', level=logging.INFO, format='%(asctime)s %(message)s')

tires = ['Front-Left', 'Front-Right', 'Rear-Left', 'Rear-Right']
psi_values = {tire: 30.0 for tire in tires}  # Initial PSI
# Simulated PSI values for each tire
# Ornstein-Uhlenbeck process for PSI
def simulate_tire_psi(prev, mu=30, theta=0.1, sigma=1):
    return prev + theta * (mu - prev) + sigma * random.gauss(0, 1)

def simulate_tire_wear(t):
    base = 20 + 10 * math.sin(0.03 * t)  # Wear cycles between 10-30%
    noise = random.uniform(-1, 1)
    return round(base + noise, 2)

time_counter = 0

def generate_tire_logs():
    global time_counter
    while True:
        for tire in tires:
            psi_values[tire] = simulate_tire_psi(psi_values[tire])
            wear = simulate_tire_wear(time_counter)
            log_message = f"TIRE ({tire}) | PSI: {psi_values[tire]:.2f} | Wear: {wear:.2f}%"
            logging.info(log_message)
        time.sleep(5)
        time_counter += 1

threading.Thread(target=generate_tire_logs, daemon=True).start()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Tire service running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
