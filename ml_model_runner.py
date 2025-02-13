# Import necessary libraries
import mysql.connector
import pandas as pd
import joblib
import time

# Connect to database
conn = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="", 
    database="rakusens"
)

# Check if connected

if conn.is_connected():
    print('Connected to database')
else:
    print('Connection failed')

cursor = conn.cursor()

# Get the newest data from the tables

def get_latest_data(table_name):
    query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1;"
    cursor.execute(query)
    row = cursor.fetchone()
    
    # Line 4 has 8 Sensors, Line 5 has 17
    if row:
        if table_name == 'line4_sensors':
            columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 9)]
        else:
            columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 18)]
        data = dict(zip(columns, row))
        return data
    return None

# Flag sensor using provided ml models for each sensor specific model provided

def check_anomalies(data, sensor_id, line_number):
    sensor_column = f"r{sensor_id:02d}"
    model_path = f"models/line{line_number}/prophet_{sensor_column}.pkl" # Path to models 
    model = joblib.load(model_path) # Load model

    timestamp = pd.to_datetime(data["timestamp"]) # Convert datetime needed for the model
    df = pd.DataFrame({"ds": [timestamp]})
    forecast = model.predict(df) # Prediction

    # Get predicted values

    yhat = forecast["yhat"].values[0]
    lower = forecast["yhat_lower"].values[0]
    upper = forecast["yhat_upper"].values[0]

    # Get real sensor value
    sensor_value = data[sensor_column]

    # Traffic light system boundaries
    green_lower, green_upper = lower, upper
    amber_lower_start, amber_lower_end = lower - 15, lower
    amber_upper_start, amber_upper_end = upper, upper + 15
    red_lower, red_upper = amber_lower_start, amber_upper_end

    # Show results
    print(f"Predicted Value (yhat): {yhat}")
    print(f"Lower Bound (yhat_lower): {lower}")
    print(f"Upper Bound (yhat_upper): {upper}")
    print("Temperature Ranges:")
    print(f"  - 🟢 Green: {green_lower} to {green_upper}")
    print(f"  - 🟠 Amber: {amber_lower_start} to {amber_lower_end} and {amber_upper_start} to {amber_upper_end}")
    print(f"  - 🔴 Red: Less than {red_lower} or more than {red_upper}")

    # Give a colour to the sensor based on result
    if sensor_value < red_lower or sensor_value > red_upper:
        status = "🔴 RED (Anomaly)"
    elif (amber_lower_start <= sensor_value < amber_lower_end) or (amber_upper_start < sensor_value <= amber_upper_end):
        status = "🟠 AMBER (Warning)"
    else:
        status = "🟢 GREEN (Normal)"
    
    # Show which sensor has been analysed
    print(f"Line {line_number} Sensor {sensor_column.upper()} Value: {sensor_value}, Expected Value: {green_lower} to {green_upper}, Status: {status}\n")

# Loop to repeat flagging every 30 seconds 
while True:
    for line, sensors in [(4, 8), (5, 17)]: 
        latest_data = get_latest_data(f"line{line}_sensors")
        if latest_data:
            for sensor_id in range(1, sensors + 1):
                check_anomalies(latest_data, sensor_id, line)
    time.sleep(30)