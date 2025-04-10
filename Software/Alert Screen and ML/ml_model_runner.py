from flask import Flask, render_template
import mysql.connector
import pandas as pd
import joblib
import threading
import time
import random  # For simulation

simulate_changes = True

app = Flask(__name__, template_folder='templates')

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rakusens"
)

if conn.is_connected():
    print('✅ Connected to database')
else:
    print('❌ Connection failed')

cursor = conn.cursor()

# Store processed results
results = []

def get_latest_data(table_name):
    query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1;"
    cursor.execute(query)
    row = cursor.fetchone()

    if row:
        if table_name == 'line4_sensors':
            columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 9)]
        else:
            columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 18)]
        
        data = dict(zip(columns, row))
        print(f"🔍 Fetched latest row from {table_name}: {data['timestamp']}")
        return data
    return None

def check_anomalies(data, sensor_id, line_number):
    sensor_column = f"r{sensor_id:02d}"
    model_path = f"models/line{line_number}/prophet_{sensor_column}.pkl"

    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        return f"⚠️ Model for Line {line_number} Sensor {sensor_column.upper()} not found."

    timestamp = pd.to_datetime(data["timestamp"])
    df = pd.DataFrame({"ds": [timestamp]})
    forecast = model.predict(df)

    yhat = forecast["yhat"].values[0]
    lower = forecast["yhat_lower"].values[0]
    upper = forecast["yhat_upper"].values[0]

    sensor_value = data[sensor_column]

    print(f"📊 Sensor {sensor_column} on Line {line_number}:")
    print(f"   - Timestamp: {data['timestamp']}")
    print(f"   - Actual Value: {sensor_value}")
    print(f"   - Predicted: {yhat} (Bounds: {lower}, {upper})")

    amber_lower_start, amber_lower_end = lower - 15, lower
    amber_upper_start, amber_upper_end = upper, upper + 15
    red_lower, red_upper = amber_lower_start, amber_upper_end

    if sensor_value < red_lower or sensor_value > red_upper:
        status = "🔴 RED (Anomaly)"
    elif (amber_lower_start <= sensor_value < amber_lower_end) or (amber_upper_start < sensor_value <= amber_upper_end):
        status = "🟠 AMBER (Warning)"
    else:
        status = "🟢 GREEN (Normal)"
      #Extract the flag from the status string
    flag = status.split()[1]
    #Insert the colour into the database
    insert_query = """ INSERT INTO sensor_flags (timestamp, line_number, sensor_id, sensor_value, flag)
    VALUES (%s, %s, %s, %s, %s) """
    values = (timestamp.strftime('%y-%m-%d %H:%M:%S'), line_number, sensor_id, sensor_value, flag)
    cursor.execute(insert_query, values)
    conn.commit
    
    
    return f"Line {line_number} Sensor {sensor_column.upper()} Value: {sensor_value:.2f}, Status: {status}"

# ✅ UPDATED: now stores timestamp and message per result
def monitor_sensors():
    global results
    while True:
        temp_results = []
        print("\n⏳ Checking sensors...")

        for line, sensor_count in [(4, 8), (5, 17)]:
            latest_data = get_latest_data(f"line{line}_sensors")
            if latest_data:
                if simulate_changes:
                    for sensor_id in range(1, sensor_count + 1):
                        sensor_column = f"r{str(sensor_id).zfill(2)}"
                        try:
                            original_val = float(latest_data[sensor_column])
                        except (ValueError, TypeError):
                            original_val = 0.0

                        if line == 4:
                            noise = random.gauss(0, 4)
                            if random.random() < 0.3:
                                noise += random.uniform(-10, 10)
                            new_value = original_val + noise
                            print(f"Simulating Line {line} Sensor {sensor_column}: original={original_val:.2f}, noise={noise:.2f}, new={new_value:.2f}")
                            latest_data[sensor_column] = new_value
                        elif line == 5:
                            model_path = f"models/line{line}/prophet_{sensor_column}.pkl"
                            try:
                                model = joblib.load(model_path)
                                timestamp = pd.to_datetime(latest_data["timestamp"])
                                df = pd.DataFrame({"ds": [timestamp]})
                                forecast = model.predict(df)
                                yhat = forecast["yhat"].values[0]
                            except FileNotFoundError:
                                yhat = original_val
                            noise = random.gauss(0, 2)
                            if random.random() < 0.3:
                                noise += random.uniform(-6, 6)
                            simulated_val = yhat + noise
                            print(f"Simulating Line {line} Sensor {sensor_column}: yhat={yhat:.2f}, noise={noise:.2f}, simulated={simulated_val:.2f}")
                            latest_data[sensor_column] = simulated_val

                # ✅ Collect timestamp + message per sensor
                timestamp = latest_data["timestamp"]
                for sensor_id in range(1, sensor_count + 1):
                    message = check_anomalies(latest_data, sensor_id, line)
                    temp_results.append({
                        "timestamp": timestamp,
                        "message": message
                    })

        print("✅ Updated results:", temp_results)
        results = temp_results
        time.sleep(30)

# Start background thread
thread = threading.Thread(target=monitor_sensors, daemon=True)
thread.start()

@app.route('/')
def index():
    print("🌐 Serving results:", results)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
