from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
import joblib
import threading
import time
import random
from datetime import datetime, timedelta

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

# Lock for thread synchronization
results_lock = threading.Lock()

# Mapping between ENUM values and full status descriptions
status_mapping = {
    'green': '🟢 GREEN (Normal)',
    'amber': '🟠 AMBER (Warning)',
    'red': '🔴 RED (Anomaly)'
}

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

    timestamp = datetime.now()
    timestamp += timedelta(milliseconds=random.randint(1, 500))

    df = pd.DataFrame({"ds": [timestamp]})
    forecast = model.predict(df)

    yhat = forecast["yhat"].values[0]
    lower = forecast["yhat_lower"].values[0]
    upper = forecast["yhat_upper"].values[0]

    sensor_value = data[sensor_column]

    # Adjusted thresholds to reduce red flags
    amber_lower_start, amber_lower_end = lower - 20, lower + 20  # Increased the range for amber
    amber_upper_start, amber_upper_end = upper - 20, upper + 20
    red_lower, red_upper = amber_lower_start - 10, amber_upper_end + 10  # Expanded red range slightly

    # Status checking
    if sensor_value < red_lower or sensor_value > red_upper:
        status = "red"
    elif (amber_lower_start <= sensor_value < amber_lower_end) or (amber_upper_start < sensor_value <= amber_upper_end):
        status = "amber"
    else:
        status = "green"
    
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    insert_query = """
        INSERT INTO sensor_flags (line_number, sensor_id, status, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    values = (line_number, sensor_column, status, timestamp_str)
    try:
        cursor.execute(insert_query, values)
        conn.commit()
        print(f"Successfully inserted into sensor_flags: {line_number}, {sensor_column}, {status}, {timestamp_str}")
    except Exception as e:
        print(f"Error inserting into database: {e}")

    return f"Line {line_number} Sensor {sensor_column.upper()} Value: {sensor_value:.2f}, Status: {status_mapping.get(status)}"

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

                timestamp = latest_data["timestamp"]
                for sensor_id in range(1, sensor_count + 1):
                    message = check_anomalies(latest_data, sensor_id, line)
                    temp_results.append({
                        "timestamp": timestamp,
                        "message": message
                    })

        with results_lock:
            results = temp_results
        print("✅ Updated results:", temp_results)
        time.sleep(30)

# Start background thread
thread = threading.Thread(target=monitor_sensors, daemon=True)
thread.start()

@app.route('/')
def index():
    print("🌐 Serving results:", results)
    return render_template('index.html', results=results)

@app.route('/charts', methods=['GET', 'POST'])
def charts():
    cursor.execute("""SELECT DISTINCT timestamp FROM sensor_flags WHERE line_number = 4 ORDER BY timestamp DESC""")
    line4_timestamps = [row[0] for row in cursor.fetchall()]

    cursor.execute("""SELECT DISTINCT timestamp FROM sensor_flags WHERE line_number = 5 ORDER BY timestamp DESC""")
    line5_timestamps = [row[0] for row in cursor.fetchall()]

    selected_timestamp = line4_timestamps[0] if line4_timestamps else None

    if request.method == 'POST':
        selected_timestamp = request.form['timestamp']

    cursor.execute("""SELECT status FROM sensor_flags WHERE line_number = 4 AND timestamp = %s""", (selected_timestamp,))
    line4_data = [status_mapping.get(row[0], row[0]) for row in cursor.fetchall()]  # Mapping ENUM to full text

    cursor.execute("""SELECT status FROM sensor_flags WHERE line_number = 5 AND timestamp = %s""", (selected_timestamp,))
    line5_data = [status_mapping.get(row[0], row[0]) for row in cursor.fetchall()]  # Mapping ENUM to full text

    # Count green, amber, and red statuses for line 4 and line 5
    line4_data_green = len([x for x in line4_data if x == '🟢 GREEN (Normal)'])
    line4_data_amber = len([x for x in line4_data if x == '🟠 AMBER (Warning)'])
    line4_data_red = len([x for x in line4_data if x == '🔴 RED (Anomaly)'])

    line5_data_green = len([x for x in line5_data if x == '🟢 GREEN (Normal)'])
    line5_data_amber = len([x for x in line5_data if x == '🟠 AMBER (Warning)'])
    line5_data_red = len([x for x in line5_data if x == '🔴 RED (Anomaly)'])

    # If no data for the selected timestamp, assign empty arrays
    if not line4_data:
        line4_data = [""] * 8  # Adjust length if needed
    if not line5_data:
        line5_data = [""] * 17  # Adjust length if needed

    return render_template('charts.html', 
                           line4_data=line4_data, 
                           line5_data=line5_data, 
                           line4_data_green=line4_data_green,
                           line4_data_amber=line4_data_amber,
                           line4_data_red=line4_data_red,
                           line5_data_green=line5_data_green,
                           line5_data_amber=line5_data_amber,
                           line5_data_red=line5_data_red,
                           line4_timestamps=line4_timestamps, 
                           line5_timestamps=line5_timestamps,
                           selected_timestamp=selected_timestamp)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
