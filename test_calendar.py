import os
import sys
from datetime import datetime, timedelta

# Add the app directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from calendar_connector import GoogleCalendarConnector

try:
    print("Testing Calendar authentication...")
    connector = GoogleCalendarConnector()
    print("Calendar authentication successful")
    
    time_min = datetime.now()
    time_max = time_min + timedelta(days=5)
    
    busy_periods = connector.get_busy_periods(time_min, time_max)
    print("Calendar API: SUCCESS")
    print(f"Busy periods found: {len(busy_periods)}")
    print(f"Busy periods: {busy_periods}")
    
except Exception as e:
    print(f"Calendar API error: {e}")
