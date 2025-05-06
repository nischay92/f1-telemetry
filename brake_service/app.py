from flask import Flask, jsonify
import threading
import time
import random
import logging
import math

app = Flask(__name__)

logging.basicConfig(filename='./logs/brake.log', level=logging.INFO, format='%(asctime)s %(message)s')

brakes = ['Front-Left', 'Front-Right', 'Rear-Left', 'Rear-Right']
temp_values = {brake: 300.0 for brake in brakes}  # Initial brake temp

# Ornstein-Uhlenbeck process for Temp
def simulate_brake_temp(prev, mu=350, theta=0.1, sigma=10):
    return prev + theta * (mu - prev) + sigma * random.gauss(0, 1)

def simulate_brake_slip(t):
    base = 5 + 2 * math.sin(0.05 * t)  # Slip cycles between 3-7%
    noise = random.uniform(-0.5, 0.5)
    return round(base + noise, 2)

time_counter = 0

def generate_brake_logs():
    global time_counter
    while True:
        for brake in brakes:
            temp_values[brake] = simulate_brake_temp(temp_values[brake])
            slip = simulate_brake_slip(time_counter)
            log_message = f"BRAKE ({brake}) | Temp: {temp_values[brake]:.2f}°C | Slip: {slip:.2f}%"
            logging.info(log_message)
        time.sleep(5)
        time_counter += 1

threading.Thread(target=generate_brake_logs, daemon=True).start()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Brake service running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
