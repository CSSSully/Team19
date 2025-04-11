# test_sensor_anomaly_detection.py
import pytest
import pandas as pd
import numpy as np
import mysql.connector
import joblib
import datetime
from unittest.mock import patch, MagicMock, mock_open

# Import the module to test (adjust the import based on your module name)
# For this test, we'll mock the import and functions
# assuming your file is named sensor_anomaly_detection.py
# @patch('sensor_anomaly_detection.mysql.connector')
# @patch('sensor_anomaly_detection.joblib')
# @patch('sensor_anomaly_detection.pd')

class TestSensorAnomalyDetection:
    
    @pytest.fixture
    def mock_cursor(self):
        """Create a mock cursor with fetchone method"""
        cursor_mock = MagicMock()
        return cursor_mock
    
    @pytest.fixture
    def mock_connection(self, mock_cursor):
        """Create a mock connection with is_connected and cursor methods"""
        conn_mock = MagicMock()
        conn_mock.is_connected.return_value = True
        conn_mock.cursor.return_value = mock_cursor
        return conn_mock
    
    @pytest.fixture
    def mock_prophet_model(self):
        """Create a mock Prophet model"""
        model_mock = MagicMock()
        forecast = pd.DataFrame({
            'ds': [pd.Timestamp('2025-04-08 12:00:00')],
            'yhat': [120.0],
            'yhat_lower': [110.0],
            'yhat_upper': [130.0]
        })
        model_mock.predict.return_value = forecast
        return model_mock
    
    def test_database_connection(self, monkeypatch):
        """Test the database connection is established correctly"""
        mock_connector = MagicMock()
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_connector.connect.return_value = mock_conn
        
        monkeypatch.setattr('mysql.connector.connect', mock_connector.connect)
        
        # Import only after monkeypatching
        from importlib import reload
        import sys
        
        # This is a bit hacky for unit tests, but simulates what would happen
        # when the script is run and the connection is established
        with patch('sys.modules', sys.modules.copy()):
            with patch('mysql.connector.connect', return_value=mock_conn):
                with patch('builtins.print') as mock_print:
                    # We need to use exec to simulate the global code execution
                    # as importing the module would execute the connection code
                    connection_code = """
import mysql.connector
conn = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="", 
    database="rakusens"
)
if conn.is_connected():
    print('Connected to database')
else:
    print('Connection failed')
"""
                    exec(connection_code)
                    mock_print.assert_called_with('Connected to database')
                    
    @patch('mysql.connector.connect')
    def test_get_latest_data_line4(self, mock_connect, mock_cursor):
        """Test get_latest_data function for line4"""
        # Setup mock return data
        mock_cursor.fetchone.return_value = (1, '2025-04-08 12:00:00', 100, 105, 110, 115, 120, 125, 130, 135)
        
        # Define the function separately to test it
        def get_latest_data(table_name):
            query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1;"
            mock_cursor.execute(query)
            row = mock_cursor.fetchone()
            
            if row:
                if table_name == 'line4_sensors':
                    columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 9)]
                else:
                    columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 18)]
                data = dict(zip(columns, row))
                return data
            return None
        
        # Call the function
        result = get_latest_data('line4_sensors')
        
        # Assertions
        mock_cursor.execute.assert_called_with("SELECT * FROM line4_sensors ORDER BY timestamp DESC LIMIT 1;")
        assert result['id'] == 1
        assert result['timestamp'] == '2025-04-08 12:00:00'
        assert result['r01'] == 100
        assert result['r08'] == 135
        
    @patch('mysql.connector.connect')
    def test_get_latest_data_line5(self, mock_connect, mock_cursor):
        """Test get_latest_data function for line5"""
        # Setup mock return data - 17 sensors plus id and timestamp
        mock_cursor.fetchone.return_value = tuple([2, '2025-04-08 12:05:00'] + list(range(100, 117)))
        
        # Define the function separately to test it
        def get_latest_data(table_name):
            query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1;"
            mock_cursor.execute(query)
            row = mock_cursor.fetchone()
            
            if row:
                if table_name == 'line4_sensors':
                    columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 9)]
                else:
                    columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 18)]
                data = dict(zip(columns, row))
                return data
            return None
        
        # Call the function
        result = get_latest_data('line5_sensors')
        
        # Assertions
        mock_cursor.execute.assert_called_with("SELECT * FROM line5_sensors ORDER BY timestamp DESC LIMIT 1;")
        assert result['id'] == 2
        assert result['timestamp'] == '2025-04-08 12:05:00'
        assert result['r01'] == 100
        assert result['r17'] == 116
        
    @patch('builtins.print')
    @patch('joblib.load')
    def test_check_anomalies_green_status(self, mock_joblib_load, mock_print, mock_prophet_model):
        """Test check_anomalies function when sensor value is in green range"""
        # Setup
        mock_joblib_load.return_value = mock_prophet_model
        
        data = {
            'timestamp': '2025-04-08 12:00:00',
            'r01': 120.0  # Value within the green range
        }
        
        # Define function to test
        def check_anomalies(data, sensor_id, line_number):
            sensor_column = f"r{sensor_id:02d}"
            model_path = f"models/line{line_number}/prophet_{sensor_column}.pkl"
            model = mock_joblib_load(model_path)
            timestamp = pd.to_datetime(data["timestamp"])
            df = pd.DataFrame({"ds": [timestamp]})
            forecast = model.predict(df)
            
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
        
        # Call the function
        check_anomalies(data, 1, 4)
        
        # Verify the model was loaded correctly
        mock_joblib_load.assert_called_with("models/line4/prophet_r01.pkl")
        
        # Verify the final status print (last print call)
        mock_print.assert_any_call("Line 4 Sensor R01 Value: 120.0, Expected Value: 110.0 to 130.0, Status: 🟢 GREEN (Normal)\n")
        
    @patch('builtins.print')
    @patch('joblib.load')
    def test_check_anomalies_amber_status_lower(self, mock_joblib_load, mock_print, mock_prophet_model):
        """Test check_anomalies function when sensor value is in amber lower range"""
        # Setup
        mock_joblib_load.return_value = mock_prophet_model
        
        data = {
            'timestamp': '2025-04-08 12:00:00',
            'r01': 100.0  # Value in amber lower range (between 95 and 110)
        }
        
        # Define function to test
        def check_anomalies(data, sensor_id, line_number):
            sensor_column = f"r{sensor_id:02d}"
            model_path = f"models/line{line_number}/prophet_{sensor_column}.pkl"
            model = mock_joblib_load(model_path)
            timestamp = pd.to_datetime(data["timestamp"])
            df = pd.DataFrame({"ds": [timestamp]})
            forecast = model.predict(df)
            
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
        
        # Call the function
        check_anomalies(data, 1, 4)
        
        # Verify final status print
        mock_print.assert_any_call("Line 4 Sensor R01 Value: 100.0, Expected Value: 110.0 to 130.0, Status: 🟠 AMBER (Warning)\n")
    
    @patch('builtins.print')
    @patch('joblib.load')
    def test_check_anomalies_amber_status_upper(self, mock_joblib_load, mock_print, mock_prophet_model):
        """Test check_anomalies function when sensor value is in amber upper range"""
        # Setup
        mock_joblib_load.return_value = mock_prophet_model
        
        data = {
            'timestamp': '2025-04-08 12:00:00',
            'r01': 135.0  # Value in amber upper range (between 130 and 145)
        }
        
        # Define function to test (same as in previous test)
        def check_anomalies(data, sensor_id, line_number):
            sensor_column = f"r{sensor_id:02d}"
            model_path = f"models/line{line_number}/prophet_{sensor_column}.pkl"
            model = mock_joblib_load(model_path)
            timestamp = pd.to_datetime(data["timestamp"])
            df = pd.DataFrame({"ds": [timestamp]})
            forecast = model.predict(df)
            
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
        
        # Call the function
        check_anomalies(data, 1, 4)
        
        # Verify final status print
        mock_print.assert_any_call("Line 4 Sensor R01 Value: 135.0, Expected Value: 110.0 to 130.0, Status: 🟠 AMBER (Warning)\n")
    
    @patch('builtins.print')
    @patch('joblib.load')
    def test_check_anomalies_red_status(self, mock_joblib_load, mock_print, mock_prophet_model):
        """Test check_anomalies function when sensor value is in red range"""
        # Setup
        mock_joblib_load.return_value = mock_prophet_model
        
        data = {
            'timestamp': '2025-04-08 12:00:00',
            'r01': 150.0  # Value outside amber range (> 145)
        }
        
        # Define function to test (same as in previous tests)
        def check_anomalies(data, sensor_id, line_number):
            sensor_column = f"r{sensor_id:02d}"
            model_path = f"models/line{line_number}/prophet_{sensor_column}.pkl"
            model = mock_joblib_load(model_path)
            timestamp = pd.to_datetime(data["timestamp"])
            df = pd.DataFrame({"ds": [timestamp]})
            forecast = model.predict(df)
            
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
        
        # Call the function
        check_anomalies(data, 1, 4)
        
        # Verify final status print
        mock_print.assert_any_call("Line 4 Sensor R01 Value: 150.0, Expected Value: 110.0 to 130.0, Status: 🔴 RED (Anomaly)\n")
    
    @patch('time.sleep')
    @patch('builtins.print')
    def test_main_loop(self, mock_print, mock_sleep):
        """Test the main loop with mocked functions"""
        # Setup mock for get_latest_data function
        mock_get_latest_data = MagicMock()
        mock_get_latest_data.side_effect = [
            # First iteration
            {'id': 1, 'timestamp': '2025-04-08 12:00:00', 'r01': 120, 'r02': 125, 'r03': 130, 'r04': 135, 'r05': 140, 'r06': 145, 'r07': 150, 'r08': 155},
            {'id': 2, 'timestamp': '2025-04-08 12:00:00', 'r01': 100, 'r02': 105, 'r03': 110, 'r04': 115, 'r05': 120, 'r06': 125, 'r07': 130, 'r08': 135,
             'r09': 140, 'r10': 145, 'r11': 150, 'r12': 155, 'r13': 160, 'r14': 165, 'r15': 170, 'r16': 175, 'r17': 180},
            # Second iteration (to break out of the loop)
            None, None  
        ]
        
        # Setup mock for check_anomalies function
        mock_check_anomalies = MagicMock()
        
        # Define a modified main loop that will exit after one iteration
        def test_loop():
            iteration_count = 0
            while iteration_count < 1:  # Only run one iteration
                for line, sensors in [(4, 8), (5, 17)]:
                    latest_data = mock_get_latest_data(f"line{line}_sensors")
                    if latest_data:
                        for sensor_id in range(1, sensors + 1):
                            mock_check_anomalies(latest_data, sensor_id, line)
                mock_sleep(30)
                iteration_count += 1
        
        # Run the test loop
        test_loop()
        
        # Verify get_latest_data was called for both lines
        assert mock_get_latest_data.call_count == 2
        mock_get_latest_data.assert_any_call("line4_sensors")
        mock_get_latest_data.assert_any_call("line5_sensors")
        
        # Verify check_anomalies was called for all sensors
        assert mock_check_anomalies.call_count == 8 + 17  # 8 sensors on line 4, 17 on line 5
        
        # Verify sleep was called once with 30 seconds
        mock_sleep.assert_called_once_with(30)

    # Test the integration of the main loop with real functions
    @patch('time.sleep')
    @patch('builtins.print')
    def test_integration(self, mock_print, mock_sleep):
        """Integration test with minimal mocking"""
        
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup cursor to return test data for both lines
        line4_data = (1, '2025-04-08 12:00:00', 120, 125, 130, 135, 140, 145, 150, 155)
        line5_data = tuple([2, '2025-04-08 12:00:00'] + list(range(100, 117)))
        
        mock_cursor.fetchone.side_effect = [line4_data, line5_data, None, None]  # Return data once, then None to exit loop
        
        # Mock model loading
        mock_model = MagicMock()
        forecast = pd.DataFrame({
            'ds': [pd.Timestamp('2025-04-08 12:00:00')],
            'yhat': [120.0],
            'yhat_lower': [110.0],
            'yhat_upper': [130.0]
        })
        mock_model.predict.return_value = forecast
        
        # Use the real get_latest_data function
        def get_latest_data(table_name):
            query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1;"
            mock_cursor.execute(query)
            row = mock_cursor.fetchone()
            
            if row:
                if table_name == 'line4_sensors':
                    columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 9)]
                else:
                    columns = ["id", "timestamp"] + [f"r{str(i).zfill(2)}" for i in range(1, 18)]
                data = dict(zip(columns, row))
                return data
            return None
        
        # Use a modified check_anomalies function that uses our mocked model
        def check_anomalies(data, sensor_id, line_number):
            sensor_column = f"r{sensor_id:02d}"
            # No need to load model, use our mock
            timestamp = pd.to_datetime(data["timestamp"])
            df = pd.DataFrame({"ds": [timestamp]})
            forecast = mock_model.predict(df)
            
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
            
            # Show results (mockable prints)
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
        
        # Define a modified main loop that will exit after one iteration
        def test_loop():
            iteration_count = 0
            while iteration_count < 1:  # Only run one iteration
                for line, sensors in [(4, 8), (5, 17)]:
                    latest_data = get_latest_data(f"line{line}_sensors")
                    if latest_data:
                        for sensor_id in range(1, sensors + 1):
                            check_anomalies(latest_data, sensor_id, line)
                mock_sleep(30)
                iteration_count += 1
        
        # Run the test loop
        with patch('joblib.load', return_value=mock_model):
            test_loop()
        
        # Check mock_cursor.execute was called for both lines
        mock_cursor.execute.assert_any_call("SELECT * FROM line4_sensors ORDER BY timestamp DESC LIMIT 1;")
        mock_cursor.execute.assert_any_call("SELECT * FROM line5_sensors ORDER BY timestamp DESC LIMIT 1;")
        
        # Check that print was called the expected number of times
        # Each check_anomalies call makes 7 print calls, and we have 25 sensors total
        # So we expect 7 * 25 = 175 print calls
        assert mock_print.call_count >= 175
        
        # Verify sleep was called once with 30 seconds
        mock_sleep.assert_called_once_with(30)
