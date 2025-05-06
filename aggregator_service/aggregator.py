import time
import re
import json
import logging

# File paths (adjust if needed)
ENGINE_LOG = './logs/engine.log'
TIRE_LOG = './logs/tire.log'
BRAKE_LOG = './logs/brake.log'


# Configure file logging
logging.basicConfig(filename='./logs/aggregator.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Thresholds
ENGINE_OVERHEAT_TEMP = 120
TIRE_LOW_PSI = 24
BRAKE_OVERHEAT_TEMP = 420

# Telemetry state dictionary
telemetry_state = {
    "engine": {"temp": None, "status": "unknown"},
    "tires": {
        "Front-Left": {"psi": None, "status": "unknown"},
        "Front-Right": {"psi": None, "status": "unknown"},
        "Rear-Left": {"psi": None, "status": "unknown"},
        "Rear-Right": {"psi": None, "status": "unknown"}
    },
    "brakes": {
        "Front-Left": {"temp": None, "status": "unknown"},
        "Front-Right": {"temp": None, "status": "unknown"},
        "Rear-Left": {"temp": None, "status": "unknown"},
        "Rear-Right": {"temp": None, "status": "unknown"}
    }
}

# Keep track of last read positions
positions = {
    ENGINE_LOG: 0,
    TIRE_LOG: 0,
    BRAKE_LOG: 0
}

def read_new_lines(filepath):
    """Read new lines from a log file since the last read."""
    lines = []
    with open(filepath, 'r') as file:
        file.seek(positions[filepath])
        lines = file.readlines()
        positions[filepath] = file.tell()
    return lines

def process_engine_logs(lines):
    alerts = []
    for line in lines:
        match = re.search(r'Temp: ([\d.]+)', line)
        if match:
            temp = float(match.group(1))
            telemetry_state["engine"]["temp"] = temp  # Update state

            # Classify status
            if temp > ENGINE_OVERHEAT_TEMP:
                telemetry_state["engine"]["status"] = "red"
                alerts.append(f"⚠️ ALERT: ENGINE Overheat! Temp: {temp}°C")
            elif temp > ENGINE_OVERHEAT_TEMP - 5:
                telemetry_state["engine"]["status"] = "yellow"
            else:
                telemetry_state["engine"]["status"] = "green"
    return alerts

def process_tire_logs(lines):
    alerts = []
    for line in lines:
        match = re.search(r'TIRE \((.*?)\) \| PSI: ([\d.]+)', line)
        if match:
            tire_pos = match.group(1)
            psi = float(match.group(2))
            telemetry_state["tires"][tire_pos]["psi"] = psi  # Update state

            # Classify status
            if psi < TIRE_LOW_PSI:
                telemetry_state["tires"][tire_pos]["status"] = "red"
                alerts.append(f"⚠️ ALERT: {tire_pos} Tire Pressure LOW! PSI: {psi:.2f}")
            elif psi < TIRE_LOW_PSI + 2:
                telemetry_state["tires"][tire_pos]["status"] = "yellow"
            else:
                telemetry_state["tires"][tire_pos]["status"] = "green"
    return alerts

def process_brake_logs(lines):
    alerts = []
    for line in lines:
        match = re.search(r'BRAKE \((.*?)\) \| Temp: ([\d.]+)', line)
        if match:
            brake_pos = match.group(1)
            temp = float(match.group(2))
            telemetry_state["brakes"][brake_pos]["temp"] = temp  # Update state

            # Classify status
            if temp > BRAKE_OVERHEAT_TEMP:
                telemetry_state["brakes"][brake_pos]["status"] = "red"
                alerts.append(f"⚠️ ALERT: {brake_pos} Brake Overheat! Temp: {temp}°C")
            elif temp > BRAKE_OVERHEAT_TEMP - 20:
                telemetry_state["brakes"][brake_pos]["status"] = "yellow"
            else:
                telemetry_state["brakes"][brake_pos]["status"] = "green"
    return alerts

def write_telemetry_state():
    with open('./logs/telemetry_state.json', 'w') as f:
        json.dump(telemetry_state, f, indent=4)

def main():
    logging.info("🚦 Aggregator service running with time series-aware logic...")
    while True:
        engine_lines = read_new_lines(ENGINE_LOG)
        tire_lines = read_new_lines(TIRE_LOG)
        brake_lines = read_new_lines(BRAKE_LOG)

        logging.info(f"Engine log lines: {engine_lines}")
        logging.info(f"Tire log lines: {tire_lines}")
        logging.info(f"Brake log lines: {brake_lines}")

        alerts = []
        alerts += process_engine_logs(engine_lines)
        alerts += process_tire_logs(tire_lines)
        alerts += process_brake_logs(brake_lines)

        if not alerts:
            logging.info("✅ All systems normal.")
        else:
            for alert in alerts:
                logging.info(alert)

        write_telemetry_state()

        time.sleep(3)


if __name__ == "__main__":
    main()
