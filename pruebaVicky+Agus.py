from urllib.request import urlopen
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Como obtener cualquier clave de sesión de acuerdo a país, tipo de sesión y año (Escalable a cualquier carrera si se añade ingresar por teclado)
print("Getting session key for specific country, session type, and year")
country = "Monaco"  # Se puede cambiar a cualquier país que tenga carreras de F1
session = "Race"
year = 2025
url = f"https://api.openf1.org/v1/sessions?country_name={country}&session_name={session}&year={year}"
initial_response = urlopen(url)
data = json.loads(initial_response.read().decode('utf-8'))

if data:
    session_key = data[0]['session_key']
    print(f"Session key for {country} {session} {year}: {session_key}")
else:
    print("No session found for the given parameters.")

# Get session information for the latest session to get race location
print("\nGetting session information for latest session")
session_response = urlopen(f'https://api.openf1.org/v1/sessions?session_key={session_key}')
session_data = json.loads(session_response.read().decode('utf-8'))
race_location = session_data[0]['location'] if session_data else "Unknown"
print(f"Race location: {race_location}") #Revisar si es repetitivo con el bloque que averigua la session_key a partir de país, tipo de sesión y año

# Get all drivers data for the latest session
print("\nGetting drivers data for latest session")
response = urlopen(f'https://api.openf1.org/v1/drivers?session_key={session_key}') 
drivers_data = json.loads(response.read().decode('utf-8'))
print("Raw drivers JSON data:") #opcional debug print?
print(drivers_data)

# Create DataFrame from drivers data and remove unwanted fields
drivers_df = pd.DataFrame(drivers_data)
fields_to_remove = ['headshot_url', 'first_name', 'last_name', 'broadcast_name', 'country_code'] #Dejo 'team_colour' para usarlo en el gráfico
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
        lap_response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver_number}')
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
        position_response = urlopen(f'https://api.openf1.org/v1/position?session_key={session_key}&driver_number={driver_number}')
        position_data = json.loads(position_response.read().decode('utf-8'))
        
        # Get the last position entry (finishing position)
        if position_data:
            final_position = position_data[-1]  # Last entry is the finishing position
            all_positions_data.append({
                'driver_number': driver_number,
                'final_position': final_position['position'],
                'date': final_position['date']
            })
            # Si este piloto terminó primero, el número de vueltas que relizó es el total de vueltas de la carrera
            if final_position['position'] == 1:
                lap_response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver_number}')
                lap_data = json.loads(lap_response.read().decode('utf-8'))
                num_laps = len(lap_data)
        else:
            print(f"No position data for driver {driver_number}")
            
    except Exception as e:
        print(f"Error getting position for driver {driver_number}: {e}")

print(f"Número de vueltas de la carrera: {num_laps}")

# Create DataFrame from positions data
positions_df = pd.DataFrame(all_positions_data)
# Format date column if it exists
if not positions_df.empty and 'date' in positions_df.columns:
    positions_df['date'] = pd.to_datetime(positions_df['date'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
print(f"\nPositions DataFrame:")
if not positions_df.empty: #Revisa si hay datos de posiciones
    print(positions_df)
    if 'final_position' in positions_df.columns:
        print(f"Total drivers with position data: {len(positions_df['driver_number'].unique())}")
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
    
    # Crear gráfico simple de velocidades por vuelta con promedio cada 5 vueltas
    print("\nCreating simple speed vs lap visualization (5-lap averages)")

    # Asegura que todos los colores tengan el prefijo '#' para evitar problemas de formato a la hora de graficar
    merged_df['team_colour'] = merged_df['team_colour'].apply(
        lambda x: f'#{x}' if pd.notna(x) and not str(x).startswith('#') else x
    )
    
    # Filtrar datos válidos
    speed_data = merged_df[merged_df['st_speed'].notna() & merged_df['lap_number'].notna()]
    
    if not speed_data.empty:
        plt.figure(figsize=(12, 6))
        
        # Incluir TODOS los pilotos
        for piloto in speed_data['full_name'].unique():
            datos_piloto = speed_data[speed_data['full_name'] == piloto].copy()
            color_equipo = datos_piloto['team_colour'].iloc[0]  # Color del equipo adecado al piloto
            
            # Crear grupos de 5 vueltas
            datos_piloto['lap_group'] = ((datos_piloto['lap_number'] - 1) // 5) * 5 + 1
            
            # Calcular promedio de velocidad por grupo de 5 vueltas
            speed_avg = datos_piloto.groupby('lap_group')['st_speed'].mean().reset_index()
            
            # Solo mostrar si tiene datos suficientes
            if len(speed_avg) > 0:
                # Usar solo el apellido para la leyenda
                apellido = piloto.split()[-1]
                plt.plot(
                    speed_avg['lap_group'],
                    speed_avg['st_speed'], 
                    marker='o',
                    label=apellido,
                    markersize=4,
                    linewidth=1.3,
                    color=color_equipo  # Usar color del equipo
                )
        
        plt.xlabel("Vuelta (inicio de grupo de 5)")
        plt.ylabel("Velocidad promedio (km/h)")
        plt.title(f"Velocidades promedio cada 5 vueltas - {race_location}")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        # Guardar gráfico
        filename = f'f1_speed_5lap_avg_{race_location.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"5-lap average speed chart saved as: {filename}")
    else:
        print("No valid speed data for simple chart")

else:
    print("No lap data available for merging")
    # Still save drivers data if available
    if not drivers_df.empty:
        drivers_df.to_csv('f1_drivers_session_latest.csv', index=False)
        print("Drivers data saved to: f1_drivers_session_latest.csv")