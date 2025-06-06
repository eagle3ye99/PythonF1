import fastf1
import pandas as pd

def formatear_tiempo_de_vuelta(tiempo):
    if pd.isnull(tiempo):
        return "No válido"
    total_segundos = tiempo.total_seconds()
    minutos = int(total_segundos // 60)
    segundos = total_segundos % 60
    return f"{minutos:02}:{segundos:06.3f}"

def formatear_tiempo_de_carrera(tiempo):
    if pd.isnull(tiempo):
        return "No válido"
    total_segundos = int(tiempo.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = tiempo.total_seconds() % 60
    return f"{horas:02}:{minutos:02}:{segundos:06.3f}"

# Cargar datos de carrera y clasificación
race_results = fastf1.get_session(2025, 'Monaco', 'R').results
race_laps = fastf1.get_session(2025, 'Monaco', 'R').laps
qual_laps = fastf1.get_session(2025, 'Monaco', 'Q').laps
drivers_info = fastf1.get_session(2025, 'Monaco', 'R').results[['DriverNumber', 'FullName']]

# Mostrar mejores vueltas de carrera por piloto
for drv in race_laps['Driver'].unique():
    laps = race_laps[race_laps['Driver'] == drv]
    if not laps.empty:
        best_lap = laps.loc[laps['LapTime'].idxmin()]
        lap_time = best_lap['LapTime']
        lap_time_str = formatear_tiempo_de_vuelta(lap_time)
        full_name = drivers_info[drivers_info['DriverNumber'] == drv]['FullName'].values[0]
        print(f"El mejor tiempo de carrera de: {full_name} fue de: {lap_time_str}")
    else:
        full_name = drivers_info[drivers_info['DriverNumber'] == drv]['FullName'].values[0]
        print(f"{full_name}: No valid lap time")

# Buscar la fila donde Position == 1
winner_row = race_results[race_results['Position'] == 1].iloc[0]
print(f"El ganador de la carrera fue: {winner_row['FullName']} con un tiempo de: {formatear_tiempo_de_carrera(winner_row['Time'])}")

# Mostrar mejores vueltas de clasificación por piloto
for drv in qual_laps['Driver'].unique():
    laps = qual_laps[qual_laps['Driver'] == drv]
    if not laps.empty:
        best_lap = laps.loc[laps['LapTime'].idxmin()]
        lap_time = best_lap['LapTime']
        lap_time_str = formatear_tiempo_de_vuelta(lap_time)
        # Buscar el nombre completo en drivers_info
        if drv in drivers_info['DriverNumber'].values:
            full_name = drivers_info[drivers_info['DriverNumber'] == drv]['FullName'].values[0]
        else:
            full_name = drv
        print(f"El mejor tiempo de clasificacion de: {full_name} fue de: {lap_time_str}")
    else:
        if drv in drivers_info['DriverNumber'].values:
            full_name = drivers_info[drivers_info['DriverNumber'] == drv]['FullName'].values[0]
        else:
            full_name = drv
        print(f"{full_name}: No tuvo un tiempo válido")