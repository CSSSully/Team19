# Team 19

# Simulate real time data

# Import necessary libraries
import mysql.connector
from datetime import datetime
import numpy as np
import time

# Connect to MySQL database use XAMPP but create the database before using my code
conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="",  
    database="rakusens"
)

# Check if connected or not

if conn.is_connected():
    print('Connected to database')
else:
    print('Failed to connect')

# Commit changes to database
cursor = conn.cursor()
conn.commit()

# Insert sensor data to database
def simulate_and_insert():
    while True:
        # Simulate Line 4 sensor data with 8 sensors using random numbers between 0-500 after checking values in the provided cvs file (max around 400)
        line4_data = {f"r{str(i).zfill(2)}": np.random.randint(0, 500) for i in range(1, 9)}
        # Simulate line 5 sensor data 17 sensors between 0-390 using random numbers provided cvs file had a max around 390
        line5_data = {f"r{str(i).zfill(2)}": np.random.randint(0, 390) for i in range(1, 18)}
        
        # Get current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert data into Line 4 table
        query_line4 = """
            INSERT INTO line4_sensors (timestamp, r01, r02, r03, r04, r05, r06, r07, r08)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values_line4 = (current_time, *line4_data.values())
        cursor.execute(query_line4, values_line4)

        # Insert data into Line 5 table
        query_line5 = """
            INSERT INTO line5_sensors (timestamp, r01, r02, r03, r04, r05, r06, r07, r08, r09, r10, r11, r12, r13, r14, r15, r16, r17)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values_line5 = (current_time, *line5_data.values())
        cursor.execute(query_line5, values_line5)

        conn.commit()

        print(f"Inserted data at {current_time} for Line 4: {line4_data}")
        print(f"Inserted data at {current_time} for Line 5: {line5_data}")
        # Repeat every 30sec

        time.sleep(30)  

# Call function
simulate_and_insert()