from urllib.request import urlopen
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def create_fastest_lap_visualization(fastest_lap_data, race_location):
    """Create visualization comparing drivers' fastest laps, speeds, and positions"""
    
    # Remove drivers with missing data
    clean_data = fastest_lap_data.dropna(subset=['lap_duration', 'st_speed', 'final_position'])
    
    if clean_data.empty:
        print("No complete data available for visualization")
        return
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'F1 Driver Performance Analysis - {race_location}', fontsize=16, fontweight='bold')
    
    # Sort by fastest lap time for consistent ordering
    clean_data = clean_data.sort_values('lap_duration')
    
    # Colors based on final position (podium finishers get special colors)
    colors = []
    for pos in clean_data['final_position']:
        if pos == 1:
            colors.append('gold')
        elif pos == 2:
            colors.append('silver')
        elif pos == 3:
            colors.append('#CD7F32')  # bronze
        else:
            colors.append('lightblue')
    
    # 1. Fastest Lap Times
    bars1 = ax1.bar(range(len(clean_data)), clean_data['lap_duration'], color=colors)
    ax1.set_title('Fastest Lap Times', fontweight='bold')
    ax1.set_xlabel('Drivers')
    ax1.set_ylabel('Lap Duration (seconds)')
    ax1.set_xticks(range(len(clean_data)))
    ax1.set_xticklabels([name.split()[-1] for name in clean_data['full_name']], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, duration) in enumerate(zip(bars1, clean_data['lap_duration'])):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{duration:.3f}', ha='center', va='bottom', fontsize=8)
    
    # 2. Speed Trap Speeds
    bars2 = ax2.bar(range(len(clean_data)), clean_data['st_speed'], color=colors)
    ax2.set_title('Speed Trap Speeds (Fastest Lap)', fontweight='bold')
    ax2.set_xlabel('Drivers')
    ax2.set_ylabel('Speed (km/h)')
    ax2.set_xticks(range(len(clean_data)))
    ax2.set_xticklabels([name.split()[-1] for name in clean_data['full_name']], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, speed) in enumerate(zip(bars2, clean_data['st_speed'])):
        if pd.notna(speed):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{speed:.0f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Final Positions
    position_data = clean_data.sort_values('final_position')
    pos_colors = []
    for pos in position_data['final_position']:
        if pos == 1:
            pos_colors.append('gold')
        elif pos == 2:
            pos_colors.append('silver')
        elif pos == 3:
            pos_colors.append('#CD7F32')
        else:
            pos_colors.append('lightcoral')
    
    bars3 = ax3.bar(range(len(position_data)), position_data['final_position'], color=pos_colors)
    ax3.set_title('Final Race Positions', fontweight='bold')
    ax3.set_xlabel('Drivers')
    ax3.set_ylabel('Position')
    ax3.set_xticks(range(len(position_data)))
    ax3.set_xticklabels([name.split()[-1] for name in position_data['full_name']], rotation=45, ha='right')
    ax3.invert_yaxis()  # Lower position numbers at top
    
    # Add value labels on bars
    for i, (bar, pos) in enumerate(zip(bars3, position_data['final_position'])):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.3, 
                f'{int(pos)}', ha='center', va='top', fontsize=10, fontweight='bold')
    
    # 4. Scatter: Lap Time vs Speed (colored by position)
    scatter_colors = []
    for pos in clean_data['final_position']:
        if pos <= 3:
            scatter_colors.append('red')
        elif pos <= 10:
            scatter_colors.append('orange')
        else:
            scatter_colors.append('blue')
    
    ax4.scatter(clean_data['lap_duration'], clean_data['st_speed'], 
               c=scatter_colors, s=100, alpha=0.7)
    ax4.set_title('Lap Time vs Speed Trap Speed', fontweight='bold')
    ax4.set_xlabel('Fastest Lap Duration (seconds)')
    ax4.set_ylabel('Speed Trap Speed (km/h)')
    
    # Add driver names to scatter points
    for i, row in clean_data.iterrows():
        if pd.notna(row['st_speed']):
            ax4.annotate(row['full_name'].split()[-1], 
                        (row['lap_duration'], row['st_speed']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Add legend for scatter plot
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Podium (1-3)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Points (4-10)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='No Points (11+)')
    ]
    ax4.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'f1_performance_analysis_{race_location.replace(" ", "_")}.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Visualization saved as: f1_performance_analysis_{race_location.replace(' ', '_')}.png")

# Get all drivers data for the latest session
print("\nGetting drivers data for latest session")
response = urlopen(f'https://api.openf1.org/v1/drivers?session_key=latest')
drivers_data = json.loads(response.read().decode('utf-8'))
print("Raw drivers JSON data:")
print(drivers_data)

# Get session information for the latest session to get race location
print("\nGetting session information for latest session")
session_response = urlopen(f'https://api.openf1.org/v1/sessions?session_key=latest')
session_data = json.loads(session_response.read().decode('utf-8'))
race_location = session_data[0]['location'] if session_data else "Unknown"
print(f"Race location: {race_location}")

# Create DataFrame from drivers data and remove unwanted fields
drivers_df = pd.DataFrame(drivers_data)
fields_to_remove = ['headshot_url', 'team_colour', 'first_name', 'last_name', 'broadcast_name']
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
    print(f"Total laps: {len(laps_df)}")
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
    
    # Get fastest lap for each driver
    print("\nAnalyzing fastest laps for each driver")
    
    # Filter out laps with null duration and get fastest lap per driver
    valid_laps = merged_df[merged_df['lap_duration'].notna() & (merged_df['lap_duration'] > 0)]
    fastest_laps = valid_laps.loc[valid_laps.groupby('driver_number')['lap_duration'].idxmin()]
    
    # Create summary DataFrame with fastest lap info
    fastest_lap_summary = fastest_laps[['driver_number', 'full_name', 'team_name', 'lap_duration', 'st_speed', 'final_position']].copy()
    fastest_lap_summary = fastest_lap_summary.sort_values('lap_duration')
    
    print("\nFastest lap summary:")
    print(fastest_lap_summary)
    
    # Save fastest lap summary
    fastest_lap_summary.to_csv('f1_fastest_laps_summary.csv', index=False)
    print("Fastest lap summary saved to: f1_fastest_laps_summary.csv")
    
    # Create visualization
    create_fastest_lap_visualization(fastest_lap_summary, race_location)

else:
    print("No lap data available for merging")
    # Still save drivers data if available
    if not drivers_df.empty:
        drivers_df.to_csv('f1_drivers_session_latest.csv', index=False)
        print("Drivers data saved to: f1_drivers_session_latest.csv")