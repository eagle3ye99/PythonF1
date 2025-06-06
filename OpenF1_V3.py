from urllib.request import urlopen
import json
import pandas as pd
from datetime import datetime

# Get all drivers data for the latest session
print("\nGetting drivers data for latest session")
response = urlopen(f'https://api.openf1.org/v1/drivers?session_key=latest')
drivers_data = json.loads(response.read().decode('utf-8'))

# Get session information for the latest session to get race location
print("\nGetting session information for latest session")
session_response = urlopen(f'https://api.openf1.org/v1/sessions?session_key=latest')
session_data = json.loads(session_response.read().decode('utf-8'))
race_location = session_data[0]['location'] if session_data else "Unknown"
print(f"Race location: {race_location}")

# Create DataFrame from drivers data and remove unwanted fields
drivers_df = pd.DataFrame(drivers_data)
fields_to_remove = ['headshot_url', 'team_colour', 'first_name', 'last_name', 'broadcast_name', 'country_code']
for field in fields_to_remove:
    if field in drivers_df.columns:
        drivers_df = drivers_df.drop(field, axis=1)
print("\nDrivers DataFrame:")
print(drivers_df)

# Get lap data for all drivers in the latest session
print("\nGetting lap data for all drivers in latest session")
all_laps_data = []

for driver in drivers_data:
    driver_number = driver['driver_number']
    print(f"Getting laps for driver {driver_number}")
    
    try:
        # Get all laps for this driver in the latest session
        lap_response = urlopen(f'https://api.openf1.org/v1/laps?session_key=latest&driver_number={driver_number}')
        lap_data = json.loads(lap_response.read().decode('utf-8'))
        
        # Add each lap to our collection (remove unwanted fields)
        for lap in lap_data:
            # Keep only desired fields
            lap_cleaned = {
                k: v for k, v in lap.items() 
                if not k.startswith('segments_sector') 
                and not k.startswith('duration_sector')
                and k not in ['i1_speed', 'i2_speed']
            }
            all_laps_data.append(lap_cleaned)
            
    except Exception as e:
        print(f"Error getting laps for driver {driver_number}: {e}")

# Get finishing positions for all drivers in the latest session
print("\nGetting finishing positions for all drivers in latest session")
all_positions_data = []

for driver in drivers_data:
    driver_number = driver['driver_number']
    print(f"Getting final position for driver {driver_number}")
    
    try:
        # Get position data for this driver in the latest session
        position_response = urlopen(f'https://api.openf1.org/v1/position?session_key=latest&driver_number={driver_number}')
        position_data = json.loads(position_response.read().decode('utf-8'))
        
        # Get the last position entry (finishing position)
        if position_data:
            final_position = position_data[-1]  # Last entry is the finishing position
            all_positions_data.append({
                'driver_number': driver_number,
                'final_position': final_position['position'],
                'date': final_position['date']
            })
        else:
            print(f"No position data for driver {driver_number}")
            
    except Exception as e:
        print(f"Error getting position for driver {driver_number}: {e}")

# Create DataFrame from positions data
positions_df = pd.DataFrame(all_positions_data)
# Format date column if it exists
if not positions_df.empty and 'date' in positions_df.columns:
    positions_df['date'] = pd.to_datetime(positions_df['date'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
print(f"\nPositions DataFrame:")
if not positions_df.empty:
    print(positions_df)
else:
    print("No position data available")

# Create DataFrame from all laps data
laps_df = pd.DataFrame(all_laps_data)
# Format date_start column if it exists
if not laps_df.empty and 'date_start' in laps_df.columns:
    laps_df['date_start'] = pd.to_datetime(laps_df['date_start'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
print(f"\nLaps DataFrame ({len(all_laps_data)} total laps):")
if not laps_df.empty:
    print(laps_df.head())
else:
    print("No lap data available")

# Merge/link the data - join drivers info with their laps and positions
if not laps_df.empty:
    # Merge drivers with laps data
    merged_df = pd.merge(laps_df, drivers_df, on='driver_number', how='left')
    
    # Also merge with positions data if available
    if not positions_df.empty:
        merged_df = pd.merge(merged_df, positions_df, on='driver_number', how='left')
    
    # Clean up duplicate columns (session_key_x/y, meeting_key_x/y)
    if 'session_key_x' in merged_df.columns and 'session_key_y' in merged_df.columns:
        # Check if they're the same values
        if merged_df['session_key_x'].equals(merged_df['session_key_y']):
            merged_df = merged_df.drop('session_key_y', axis=1)
            merged_df = merged_df.rename(columns={'session_key_x': 'session_key'})
            print("Removed duplicate session_key column")
    
    if 'meeting_key_x' in merged_df.columns and 'meeting_key_y' in merged_df.columns:
        # Check if they're the same values
        if merged_df['meeting_key_x'].equals(merged_df['meeting_key_y']):
            merged_df = merged_df.drop('meeting_key_y', axis=1)
            merged_df = merged_df.rename(columns={'meeting_key_x': 'meeting_key'})
            print("Removed duplicate meeting_key column")
    
    # Add race location to merged data
    if 'race_location' not in merged_df.columns:
        merged_df['race_location'] = race_location
    
    print(f"\nMerged DataFrame (laps with driver info and positions):")
    print(merged_df.head())
    
    # Show some statistics
    print(f"\nSummary:")
    print(f"Race location: {race_location}")
    print(f"Session: Latest")
    print(f"Total drivers: {len(drivers_df)}")
    print(f"Drivers with lap data: {laps_df['driver_number'].nunique()}")
    if not positions_df.empty:
        print(f"Drivers with position data: {len(positions_df)}")
    
    # Save to CSV files
    drivers_df.to_csv('f1_drivers_session_latest.csv', index=False)
    laps_df.to_csv('f1_laps_session_latest.csv', index=False)
    merged_df.to_csv('f1_merged_data_session_latest.csv', index=False)
    if not positions_df.empty:
        positions_df.to_csv('f1_positions_session_latest.csv', index=False)
    
    file_list = "f1_drivers_session_latest.csv, f1_laps_session_latest.csv, f1_merged_data_session_latest.csv"
    if not positions_df.empty:
        file_list += ", f1_positions_session_latest.csv"
    print(f"CSV files saved: {file_list}")

else:
    print("No lap data available for merging")
    # Still save drivers data if available
    if not drivers_df.empty:
        drivers_df.to_csv('f1_drivers_session_latest.csv', index=False)
        print("Drivers data saved to: f1_drivers_session_latest.csv")
