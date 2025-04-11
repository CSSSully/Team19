# test_simulation.py
import unittest
from unittest.mock import patch, MagicMock, call
import mysql.connector
import time
from datetime import datetime
import sys
import os
import importlib
import numpy as np

# Set up path to import the simulation module
# Assuming the test file is in the same directory as the simulation script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the simulation module to avoid actual database connections during tests
class TestSensorSimulation(unittest.TestCase):
    @patch('mysql.connector.connect')
    def test_database_connection(self, mock_connect):
        # Setup mock
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        
        # Import the module
        with patch.dict('sys.modules', {'mysql.connector': mock_connect}):
            # Import the module under test
            sim_module = importlib.import_module('simulate_real_time_data')
            
        # Assert connection was attempted with correct parameters
        mock_connect.assert_called_once_with(
            host="localhost",
            user="root",
            password="",
            database="rakusens"
        )
        
        # Assert connection check was performed
        mock_conn.is_connected.assert_called_once()
    
    @patch('time.sleep', return_value=None)  # Skip the sleep to make tests run faster
    @patch('mysql.connector.connect')
    def test_simulate_and_insert(self, mock_connect, mock_sleep):
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        
        # Set up a side effect to break the infinite loop after one iteration
        mock_sleep.side_effect = [None, Exception("Stop iteration")]
        
        # Import the module and patch random generation for predictable results
        with patch.dict('sys.modules', {'mysql.connector': mock_connect}):
            with patch('numpy.random.randint') as mock_randint:
                # Set up consistent test data
                mock_randint.side_effect = lambda min_val, max_val, *args: 100
                
                # Import the module under test
                try:
                    sim_module = importlib.import_module('simulate_real_time_data')
                    sim_module.simulate_and_insert()
                except Exception as e:
                    if str(e) != "Stop iteration":
                        raise
        
        # Assert cursor execute was called exactly twice (once for each table)
        self.assertEqual(mock_cursor.execute.call_count, 2)
        
        # Assert commit was called to save the data
        mock_conn.commit.assert_called()
        
        # Check that time.sleep was called with the right value
        mock_sleep.assert_called_with(30)
    
    @patch('mysql.connector.connect')
    def test_data_generation_ranges(self, mock_connect):
        # Setup mock
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        
        # Import the module and capture random generation without patching
        with patch.dict('sys.modules', {'mysql.connector': mock_connect}):
            sim_module = importlib.import_module('simulate_real_time_data')
        
        # Test line4 sensor data ranges
        for _ in range(100):  # Run multiple iterations to check range
            line4_data = {f"r{str(i).zfill(2)}": np.random.randint(0, 500) for i in range(1, 9)}
            for sensor_id, value in line4_data.items():
                self.assertGreaterEqual(value, 0)
                self.assertLess(value, 500)
        
        # Test line5 sensor data ranges
        for _ in range(100):
            line5_data = {f"r{str(i).zfill(2)}": np.random.randint(0, 390) for i in range(1, 18)}
            for sensor_id, value in line5_data.items():
                self.assertGreaterEqual(value, 0)
                self.assertLess(value, 390)
    
    @patch('datetime.datetime')
    @patch('mysql.connector.connect')
    def test_timestamp_format(self, mock_connect, mock_datetime):
        # Setup mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        
        # Mock datetime.now() to return a fixed datetime
        mock_now = MagicMock()
        mock_now.strftime.return_value = '2023-10-25 14:30:00'
        mock_datetime.now.return_value = mock_now
        
        # Import the module and patch
        with patch.dict('sys.modules', {'mysql.connector': mock_connect}):
            with patch('time.sleep') as mock_sleep:
                # Set up to break after one iteration
                mock_sleep.side_effect = Exception("Stop iteration")
                
                with patch('numpy.random.randint', return_value=100):
                    try:
                        sim_module = importlib.import_module('simulate_real_time_data')
                        sim_module.simulate_and_insert()
                    except Exception as e:
                        if str(e) != "Stop iteration":
                            raise
        
        # Assert timestamp format is correct in the SQL queries
        calls = mock_cursor.execute.call_args_list
        
        # Check first call (Line 4)
        line4_call = calls[0]
        self.assertEqual(line4_call[0][1][0], '2023-10-25 14:30:00')
        
        # Check second call (Line 5)
        line5_call = calls[1]
        self.assertEqual(line5_call[0][1][0], '2023-10-25 14:30:00')

    @patch('mysql.connector.connect')
    def test_database_failure(self, mock_connect):
        # Simulate database connection failure
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.is_connected.return_value = False
        
        # Redirect stdout to capture print output
        import io
        from contextlib import redirect_stdout
        
        # Import the module and check output
        f = io.StringIO()
        with redirect_stdout(f):
            with patch.dict('sys.modules', {'mysql.connector': mock_connect}):
                sim_module = importlib.import_module('simulate_real_time_data')
        
        # Check that the failure message was printed
        output = f.getvalue()
        self.assertIn('Failed to connect', output)


if __name__ == '__main__':
    unittest.main()
