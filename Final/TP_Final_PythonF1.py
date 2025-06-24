from urllib.request import urlopen
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import time

circuits_df = pd.read_csv('Circuits.csv')  # Asegurarse de que este archivo esté en el mismo directorio
print(circuits_df.columns)
# Definir los años disponibles (2023-2025, la API contiene datos para estos años)
years = [2023, 2024, 2025]
# Definir los tipos de sesión disponibles (la API contiene datos para estos tipos)
session_types = ['Practice', 'Qualifying', 'Race', 'Sprint']

# Generar una lista numerada de circuitos
print("Circuitos disponibles:")
for i, circuit in enumerate(circuits_df['Circuit'], 1):
    print(f"{i}. {circuit}")

# Pedir al usuario hasta que elija un circuito válido
while True:
    try:
        circuit_choice = int(input("Selecciona un circuito por número: ")) - 1
        if 0 <= circuit_choice < len(circuits_df):
            selected_circuit_legible = circuits_df.iloc[circuit_choice]['Circuit']
            selected_circuit_url = circuits_df.iloc[circuit_choice]['circuit_for_URL']
            break
        else:
            print("Opción inválida. Ingresa un número entre 1 y", len(circuits_df))
    except ValueError:
        print("Por favor ingresa un número válido.")

print("\nAños disponibles (2023-2025):")
for i, year in enumerate(years, 1):
    print(f"{i}. {year}")

# Pedir al usuario hasta que elija un año válido
while True:
    try:
        year_choice = int(input("Selecciona un año por número: ")) - 1
        if 0 <= year_choice < len(years):
            selected_year = years[year_choice]
            break
        else:
            print("Opción inválida. Ingresa un número entre 1 y", len(years))
    except ValueError:
        print("Por favor ingresa un número válido.")

print("\nTipos de sesión disponibles:")
for i, session_type in enumerate(session_types, 1):
    print(f"{i}. {session_type}")

# Pedir al usuario hasta que elija un tipo de sesión válido
while True:
    try:
        session_choice = int(input("Selecciona un tipo de sesión por número: ")) - 1
        if 0 <= session_choice < len(session_types):
            selected_session = session_types[session_choice]
            break
        else:
            print("Opción inválida. Ingresa un número entre 1 y", len(session_types))
    except ValueError:
        print("Por favor ingresa un número válido.")

print(f"\nCircuito seleccionado: {selected_circuit_legible}, Año: {selected_year}, Tipo de sesión: {selected_session}")
print(f"\nObteniendo clave de sesión para el circuito, tipo de sesión y año seleccionados")
url = f"https://api.openf1.org/v1/sessions?circuit_short_name={selected_circuit_url}&session_name={selected_session}&year={selected_year}"
initial_response = urlopen(url)
sessions_data = json.loads(initial_response.read().decode('utf-8'))

if sessions_data:
    session_key = sessions_data[0]['session_key']
    print(f"Clave de sesión encontrada: {session_key}")
    # Ahora se puede usar session_key con seguridad
    session_response = urlopen(f'https://api.openf1.org/v1/sessions?session_key={session_key}')
    session_data = json.loads(session_response.read().decode('utf-8'))
    race_location = session_data[0]['location'] if session_data else "Desconocido"
    print(f"Ubicación de la carrera: {race_location}")

    # Obtener datos de todos los pilotos para la sesión seleccionada
    print("\nObteniendo datos de pilotos para la sesión seleccionada")
    response = urlopen(f'https://api.openf1.org/v1/drivers?session_key={session_key}') 
    drivers_data = json.loads(response.read().decode('utf-8'))
    print("Datos JSON de pilotos sin procesar:")  # Print opcional para depuración
    print(drivers_data)

    # Crear DataFrame a partir de los datos de pilotos y eliminar campos no deseados
    drivers_df = pd.DataFrame(drivers_data)
    fields_to_remove = ['headshot_url', 'first_name', 'last_name', 'broadcast_name', 'country_code']  # Mantener 'team_colour' para usarlo en el gráfico
    for field in fields_to_remove:
        if field in drivers_df.columns:
            drivers_df = drivers_df.drop(field, axis=1)
    print("\nDataFrame de pilotos:")
    print(drivers_df)
    print("\nInformación del DataFrame de pilotos:")
    print(drivers_df.info())

    # Obtener datos de vueltas para todos los pilotos en la sesión seleccionada
    print("\nObteniendo datos de vueltas para todos los pilotos en la sesión seleccionada")
    all_laps_data = []

    for driver in drivers_data:
        driver_number = driver['driver_number']
        print(f"Obteniendo vueltas para el piloto {driver_number}")
        
        try:
            # Obtener todas las vueltas para este piloto en la sesión seleccionada
            lap_response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver_number}')
            lap_data = json.loads(lap_response.read().decode('utf-8'))
            
            # Agregar cada vuelta a nuestra colección (eliminar campos no deseados)
            for lap in lap_data:
                # Mantener solo los campos deseados
                lap_cleaned = {
                    k: v for k, v in lap.items() 
                    if not k.startswith('segments_sector') 
                    and not k.startswith('duration_sector')
                    and k not in ['i1_speed', 'i2_speed']
                }
                all_laps_data.append(lap_cleaned)
                
        except Exception as e:
            print(f"Error obteniendo vueltas para el piloto {driver_number}: {e}")

    # Obtener todas las posiciones para todos los pilotos en la sesión seleccionada
    all_positions_data = []

    for driver in drivers_data:
        driver_number = driver['driver_number']
        print(f"Obteniendo todas las posiciones para el piloto {driver_number}") #Print opcional para depuración
        try:
            # Obtener datos de posición para este piloto en la sesión seleccionada
            position_response = urlopen(f'https://api.openf1.org/v1/position?session_key={session_key}&driver_number={driver_number}')
            position_data = json.loads(position_response.read().decode('utf-8'))
            for pos in position_data:
                all_positions_data.append({
                    'driver_number': driver_number,
                    'position': pos['position'],
                    'date': pos['date']
                })
            # Si ese piloto terminó primero, el número de vueltas que completó es el número de vueltas de la carrera
            if position_data and position_data[-1]['position'] == 1:
                lap_response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}&driver_number={driver_number}')
                lap_data = json.loads(lap_response.read().decode('utf-8'))
                num_laps = len(lap_data)
        except Exception as e:
            print(f"Error obteniendo posición para el piloto {driver_number}: {e}")
        time.sleep(0.5)  # Esperar medio segundo entre solicitudes para evitar sobrecarga del servidor

    print(f"Número de vueltas de la carrera: {num_laps}") # Print opcional para depuración

    # Crear DataFrame a partir de los datos de posiciones
    positions_df = pd.DataFrame(all_positions_data)
    # Formatear la columna de fecha si existe
    if not positions_df.empty and 'date' in positions_df.columns:
        positions_df['date'] = pd.to_datetime(positions_df['date'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
    print(f"\nDataFrame de posiciones:")
    if not positions_df.empty:  # Revisar si hay datos de posiciones
        print(positions_df)
        print("\nInformación del DataFrame de posiciones:")
        print(positions_df.info())
        if 'final_position' in positions_df.columns:
            print(f"Total de pilotos con datos de posición: {(positions_df['driver_number'].unique())}")
    else:
        print("No hay datos de posición disponibles")
    
    # Crear columna 'final_position' para cada piloto (última posición registrada)
    if not positions_df.empty and 'driver_number' in positions_df.columns and 'position' in positions_df.columns:
        final_positions = positions_df.sort_values(['driver_number', 'date']).groupby('driver_number').last().reset_index()
        final_positions = final_positions[['driver_number', 'position']].rename(columns={'position': 'final_position'})
        # Unir la posición final al positions_df
        positions_df = pd.merge(positions_df, final_positions, on='driver_number', how='left')

    # Crear DataFrame a partir de todos los datos de vueltas
    laps_df = pd.DataFrame(all_laps_data)
    # Formatear la columna date_start si existe
    if not laps_df.empty and 'date_start' in laps_df.columns:
        laps_df['date_start'] = pd.to_datetime(laps_df['date_start'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
    print(f"\nDataFrame de vueltas ({len(all_laps_data)} vueltas totales):")
    if not laps_df.empty:
        print(laps_df.head())
    else:
        print("No hay datos de vueltas disponibles")
    
    if not laps_df.empty and 'lap_number' in laps_df.columns:
        completed_all = laps_df.groupby('driver_number')['lap_number'].max() == num_laps
        drivers_completed_all = completed_all[completed_all].index.tolist()
        print(f"Pilotos que completaron todas las vueltas: {len(drivers_completed_all)}")
    else:
        print("No hay datos de vueltas para determinar qué pilotos completaron todas las vueltas.")

    # Combinar/vincular los datos - unir información de pilotos con sus vueltas y posiciones
    if not laps_df.empty:
        # Combinar pilotos con datos de vueltas
        merged_df = pd.merge(laps_df, drivers_df, on='driver_number', how='left')
        
        # También combinar con datos de posiciones si están disponibles
        if not positions_df.empty:
            merged_df = pd.merge(merged_df, positions_df, on='driver_number', how='left')
        
        # Limpiar columnas duplicadas (session_key_x/y, meeting_key_x/y)
        if 'session_key_x' in merged_df.columns and 'session_key_y' in merged_df.columns:
            # Verificar si tienen los mismos valores
            if merged_df['session_key_x'].equals(merged_df['session_key_y']):
                merged_df = merged_df.drop('session_key_y', axis=1)
                merged_df = merged_df.rename(columns={'session_key_x': 'session_key'})
                print("Columna session_key duplicada eliminada")
        
        if 'meeting_key_x' in merged_df.columns and 'meeting_key_y' in merged_df.columns:
            # Verificar si tienen los mismos valores
            if merged_df['meeting_key_x'].equals(merged_df['meeting_key_y']):
                merged_df = merged_df.drop('meeting_key_y', axis=1)
                merged_df = merged_df.rename(columns={'meeting_key_x': 'meeting_key'})
                print("Columna meeting_key duplicada eliminada")
        
        # Agregar ubicación de la carrera a los datos combinados
        if 'race_location' not in merged_df.columns:
            merged_df['race_location'] = race_location
        
        print(f"\nDataFrame combinado (vueltas con información de pilotos y posiciones):")
        print(merged_df.head())
        print("\nInformación del DataFrame combinado:")
        print(merged_df.info())
        
        # Mostrar algunas estadísticas
        print(f"\nResumen:")
        print(f"Ubicación de la carrera: {race_location}")
        print(f"Sesión: {selected_session}")
        print(f"Total de pilotos: {len(drivers_df)}")
        print(f"Total de vueltas de carrera: {num_laps}")
        print(f"Pilotos con datos de vueltas: {laps_df['driver_number'].nunique()}")
        if not positions_df.empty:
            print(f"Pilotos con datos de posición: {positions_df['driver_number'].nunique()}")
        
        # Guardar en archivos CSV
        drivers_df.to_csv('f1_drivers_session_latest.csv', index=False)
        laps_df.to_csv('f1_laps_session_latest.csv', index=False)
        merged_df.to_csv('f1_merged_data_session_latest.csv', index=False)
        if not positions_df.empty:
            positions_df.to_csv('f1_positions_session_latest.csv', index=False)
        
        file_list = "f1_drivers_session_latest.csv, f1_laps_session_latest.csv, f1_merged_data_session_latest.csv"
        if not positions_df.empty:
            file_list += ", f1_positions_session_latest.csv"
        print(f"Archivos CSV guardados: {file_list}")
        
        # Obtener la vuelta más rápida para cada piloto
        print("\nAnalizando vueltas más rápidas para cada piloto")
        
        # Filtrar vueltas con duración nula y obtener la vuelta más rápida por piloto
        valid_laps = merged_df[merged_df['lap_duration'].notna() & (merged_df['lap_duration'] > 0)]
        fastest_laps = valid_laps.loc[valid_laps.groupby('driver_number')['lap_duration'].idxmin()]
        
        # Crear DataFrame resumen con información de vuelta más rápida
        columns_needed = ['driver_number', 'full_name', 'team_name', 'lap_duration', 'st_speed', 'final_position']
        if 'team_colour' in merged_df.columns:
            columns_needed.append('team_colour')

        fastest_lap_summary = fastest_laps[columns_needed].copy()
        fastest_lap_summary = fastest_lap_summary.sort_values('lap_duration')
        
        print("\nResumen de vueltas más rápidas:")
        print(fastest_lap_summary)
        
        # Guardar resumen de vueltas más rápidas
        fastest_lap_summary.to_csv('f1_fastest_laps_summary.csv', index=False)
        print("Resumen de vueltas más rápidas guardado en: f1_fastest_laps_summary.csv")
        
        # Asegurar que todos los colores tengan el prefijo '#' para evitar problemas de formato al graficar
        merged_df['team_colour'] = merged_df['team_colour'].apply(
            lambda x: f'#{x}' if pd.notna(x) and not str(x).startswith('#') else x
        )
        
        # Crear gráfico de barras de la vuelta más rápida de cada piloto
        print("\nCreando gráfico de barras de vueltas más rápidas (relativo al piloto más rápido)")

        # Asegurar que todos los colores tengan el prefijo '#'
        fastest_lap_summary['team_colour'] = fastest_lap_summary['team_colour'].apply(
            lambda x: f'#{x}' if pd.notna(x) and not str(x).startswith('#') else x
        )

        # Calcular la diferencia respecto al más rápido
        min_lap = fastest_lap_summary['lap_duration'].min()
        fastest_lap_summary['delta'] = fastest_lap_summary['lap_duration'] - min_lap

        # Ordenar para que el más rápido esté arriba
        fastest_lap_summary = fastest_lap_summary.sort_values('delta')

        plt.figure(figsize=(10, 7))
        bars = plt.barh(
            fastest_lap_summary['full_name'],
            fastest_lap_summary['delta'],
            color=fastest_lap_summary['team_colour']
        )
        plt.xlabel("Diferencia respecto al más rápido (s)")
        plt.ylabel("Piloto")
        plt.title(f"Vuelta más rápida de cada piloto - {race_location} ({selected_session} {selected_year})\n(referencia: más rápido = 0.0 s)")
        plt.gca().invert_yaxis()  # El más rápido arriba
        plt.tight_layout()
        plt.grid(axis='x', linestyle='--', alpha=0.5)

        # Cambiar la escala del eje x cada 0.1 segundos (100 milisegundos)
        max_delta = fastest_lap_summary['delta'].max()
        plt.xticks(np.arange(0, max_delta + 0.11, 0.1))

        # Agregar el tiempo de vuelta del más rápido al margen de la barra superior, con unidades
        fastest_driver = fastest_lap_summary.iloc[0]
        fastest_time = fastest_driver['lap_duration']
        # Formatear a min:seg:miliseg
        mins = int(fastest_time // 60)
        secs = int(fastest_time % 60)
        millis = int((fastest_time - int(fastest_time)) * 1000)
        formatted_time = f"{mins}:{secs:02d}.{millis:03d} min"

        plt.text(
            x=fastest_driver['delta'] + 0.02,  # Un poco a la derecha de la barra
            y=0,  # Primer piloto (más rápido, arriba)
            s=f"{formatted_time}",
            va='center',
            ha='left',
            fontsize=11,
            fontweight='bold',
            color=fastest_driver['team_colour']
        )

        plt.savefig('f1_fastest_lap_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Gráfico de barras de vueltas más rápidas guardado como: f1_fastest_lap_bar_chart.png")
    else:
        print("No hay datos de vueltas disponibles para combinar")
        # Aún así guardar datos de pilotos si están disponibles
        if not drivers_df.empty:
            drivers_df.to_csv('f1_drivers_session_latest.csv', index=False)
            print("Datos de pilotos guardados en: f1_drivers_session_latest.csv")
    
    # Crear gráfico de posición inicial vs final para cada piloto 
    if not positions_df.empty and 'final_position' in positions_df.columns and 'driver_number' in positions_df.columns:
        # Si no existe 'starting_position', obtenerla como la primera posición registrada para cada piloto
        if 'starting_position' not in positions_df.columns:
            # Asegurar que positions_df tenga las columnas 'position' y 'driver_number'
            if not positions_df.empty and 'driver_number' in positions_df.columns and 'position' in positions_df.columns:
                # Ordenar por fecha para asegurar que la primera posición sea la inicial
                positions_sorted = positions_df.sort_values(['driver_number', 'date'])
                # Obtener la posición inicial de cada piloto (primer registro)
                initial_positions = positions_sorted.groupby('driver_number').first().reset_index()
                # Renombrar la columna para claridad
                initial_positions = initial_positions.rename(columns={'position': 'initial_position'})
                # Unir la posición inicial al drivers_df
                drivers_df = pd.merge(drivers_df, initial_positions[['driver_number', 'initial_position']], on='driver_number', how='left')
            else:
                print("No hay datos de posición disponibles para determinar posiciones iniciales.")
                drivers_df['initial_position'] = np.nan  # Asignar NaN si no hay datos de posición inicial

        # Unir drivers_df (que ahora tiene initial_position) con positions_df (que tiene final_position)
        start_finish_df = pd.merge(
            drivers_df[['driver_number', 'full_name', 'team_colour', 'team_name', 'initial_position']],
            positions_df[['driver_number', 'final_position']],
            on='driver_number',
            how='left'
        )
        start_finish_df['position_change'] = start_finish_df['initial_position'] - start_finish_df['final_position']

        # Asegurar que todos los colores tengan el prefijo '#'
        start_finish_df['team_colour'] = start_finish_df['team_colour'].apply(
            lambda x: f'#{x}' if pd.notna(x) and not str(x).startswith('#') else x
        )
        
        # GRÁFICO 
        plt.figure(figsize=(10, 7)) 
        
        for i, row in start_finish_df.iterrows():
            start_pos = row['initial_position']
            finish_pos = row['final_position']
            driver_name = row['full_name'].split()[-1]  # Solo apellido
            team_colour = row['team_colour']
            
            # Línea
            plt.plot([0, 1], [start_pos, finish_pos], 
                    color=team_colour, linewidth=1, alpha=0.8)
            
            # Texto del piloto
            plt.text(1.02, finish_pos, driver_name, 
                    va='center', ha='left', fontsize=9, 
                    color=team_colour, fontweight='normal')
            
            # Número de posición inicial
            plt.text(-0.02, start_pos, f'P{int(start_pos)}', 
                    ha='right', va='center', fontsize=8, 
                    color='black', fontweight='normal')

        # Configuración del gráfico
        plt.xlim(-0.1, 1.3)
        plt.xticks([0, 1], ['Posición de Largada', 'Posición Final'], fontsize=12)
        plt.ylabel('Posición', fontsize=12)
        plt.title(f'Posiciones Inicial vs Final - {race_location}\n{selected_session} {selected_year}', 
                 fontsize=13, pad=15)
        
        # Invertir eje Y para que P1 esté arriba
        plt.gca().invert_yaxis()
        
        # Configurar ticks del eje Y 
        max_position = max(start_finish_df['initial_position'].max(), 
                          start_finish_df['final_position'].max())
        plt.yticks(range(1, int(max_position) + 1))
        
        # Grid simple
        plt.grid(True, alpha=0.3, axis='y')
        
        from matplotlib.lines import Line2D
        unique_teams = start_finish_df[['team_name', 'team_colour']].drop_duplicates()
        legend_elements = [
            Line2D([0], [0], color=row['team_colour'], lw=3, label=row['team_name'])
            for _, row in unique_teams.iterrows()
        ]
        
        plt.legend(handles=legend_elements, 
                  loc='center left', 
                  bbox_to_anchor=(1.05, 0.5), 
                  fontsize=8)
        
        plt.tight_layout()

        # Guardar con mayor calidad
        filename = f'f1_start_finish_positions_{race_location.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', 
                   format='png')
        plt.show()
        print(f"Gráfico de posiciones inicial vs final guardado como: {filename}")

        # Guardar datos
        start_finish_df.to_csv('f1_start_finish_positions.csv', index=False)
        print("Datos de posiciones inicial-final guardados en: f1_start_finish_positions.csv")

        if len(start_finish_df) > 0:
            biggest_gainer = start_finish_df.loc[start_finish_df['position_change'].idxmax()]
            biggest_loser = start_finish_df.loc[start_finish_df['position_change'].idxmin()]
            print(f"\nMayor ganador: {biggest_gainer['full_name']} (+{biggest_gainer['position_change']} posiciones)")
            print(f"Mayor perdedor: {biggest_loser['full_name']} ({biggest_loser['position_change']} posiciones)")
    else:
        print("No hay datos de posiciones inicial-final disponibles para crear el gráfico")
else:
    print("No se encontró sesión para los parámetros dados.")
