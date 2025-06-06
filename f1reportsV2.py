from urllib.request import urlopen
import json
import csv
import pandas as pd

BASE_URL = "https://api.openf1.org/v1"

def get_latest_session():
    url = f"{BASE_URL}/sessions?session_type=Race"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data:
                latest_session = max(data, key=lambda x: x['date_start'])
                return latest_session
    except Exception as e:
        print(f"Error fetching sessions: {e}")
    return None

def get_drivers_for_session(session_key):
    url = f"{BASE_URL}/drivers?session_key={session_key}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching drivers: {e}")
    return []

def get_lap_times(session_key, limit=500):
    url = f"{BASE_URL}/laps?session_key={session_key}&limit={limit}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching lap times: {e}")
    return []

def save_to_csv(data, filename):
    if not data:
        print(f"❌ No data to save for {filename}")
        return False
    try:
        all_keys = set()
        for record in data:
            all_keys.update(record.keys())
        fieldnames = sorted(list(all_keys))
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"💾 Data saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False

def generate_race_summary_csv(session, drivers, valid_laps):
    if not valid_laps:
        return False
    driver_stats = {}
    for lap in valid_laps:
        driver_num = lap['driver_number']
        if driver_num not in driver_stats:
            driver_stats[driver_num] = {
                'driver_number': driver_num,
                'driver_name': 'Unknown',
                'team': 'Unknown',
                'total_laps': 0,
                'fastest_lap': float('inf'),
                'slowest_lap': 0,
                'average_lap': 0,
                'lap_times': []
            }
        driver_stats[driver_num]['total_laps'] += 1
        duration = lap['lap_duration']
        driver_stats[driver_num]['lap_times'].append(duration)
        if duration < driver_stats[driver_num]['fastest_lap']:
            driver_stats[driver_num]['fastest_lap'] = duration
        if duration > driver_stats[driver_num]['slowest_lap']:
            driver_stats[driver_num]['slowest_lap'] = duration
    driver_lookup = {d['driver_number']: d for d in drivers}
    summary_data = []
    for driver_num, stats in driver_stats.items():
        if driver_num in driver_lookup:
            driver_info = driver_lookup[driver_num]
            stats['driver_name'] = driver_info.get('full_name', 'Unknown')
            stats['team'] = driver_info.get('team_name', 'Unknown')
        if stats['lap_times']:
            stats['average_lap'] = sum(stats['lap_times']) / len(stats['lap_times'])
        del stats['lap_times']
        summary_data.append(stats)
    summary_data.sort(key=lambda x: x['fastest_lap'])
    race_name = session['session_name'].replace(' ', '_')
    date = session['date_start'][:10]
    filename = fr"C:\Users\agust\Desktop\PythonF1\f1_race_summary_{race_name}_{date}.csv"
    return save_to_csv(summary_data, filename)

def generate_report():
    print("🏎️  F1 Data Report Generator")
    print("=" * 50)
    print("Fetching latest race session...")
    session = get_latest_session()
    if not session:
        print("❌ No recent race session found")
        return
    session_key = session['session_key']
    print(f"📅 Race: {session['session_name']}")
    print(f"🏁 Date: {session['date_start']}")
    print(f"🔑 Session Key: {session_key}")
    print()
    race_name = session['session_name'].replace(' ', '_')
    date = session['date_start'][:10]
    print("Fetching drivers...")
    drivers = get_drivers_for_session(session_key)
    print(f"Drivers data: {drivers}")
    if drivers:
        print(f"👥 Total Drivers: {len(drivers)}")
        print("\n📋 Driver List:")
        for driver in drivers[:20]:
            team = driver.get('team_name', 'Unknown Team')
            print(f"  • {driver['full_name']} ({driver['name_acronym']}) - {team}")
        drivers_filename = fr"C:\Users\agust\Desktop\PythonF1\f1_drivers_{race_name}_{date}.csv"
        save_to_csv(drivers, drivers_filename)
    print(f"\nFetching lap times...")
    laps = get_lap_times(session_key)
    print(f"Laps data: {laps}")
    if laps:
        print(f"⏱️  Total Laps Retrieved: {len(laps)}")
        session_filename = fr"C:\Users\agust\Desktop\PythonF1\f1_session_{race_name}_{date}.csv"
        save_to_csv([session], session_filename)
        laps_filename = fr"C:\Users\agust\Desktop\PythonF1\f1_laps_{race_name}_{date}.csv"
        save_to_csv(laps, laps_filename)
        valid_laps = [lap for lap in laps if lap.get('lap_duration') is not None]
        if valid_laps:
            lap_durations = [lap['lap_duration'] for lap in valid_laps]
            print(f"\n📊 Lap Time Analysis:")
            print(f"  • Valid Laps: {len(valid_laps)}")
            print(f"  • Fastest Lap: {min(lap_durations):.3f}s")
            print(f"  • Slowest Lap: {max(lap_durations):.3f}s")
            print(f"  • Average Lap: {sum(lap_durations) / len(lap_durations):.3f}s")
            fastest_laps = sorted(valid_laps, key=lambda x: x['lap_duration'])[:5]
            print(f"\n🏆 Top 5 Fastest Laps:")
            for lap in fastest_laps:
                print(f"  {lap['lap_duration']:.3f}s - Driver #{lap['driver_number']} (Lap {lap['lap_number']})")
            print(f"\n📈 Generating race summary...")
            generate_race_summary_csv(session, drivers, valid_laps)
    print(f"\n✅ Report generated successfully!")
    print(f"📁 CSV Files Created:")
    print(f"  • Session information: f1_session_{race_name}_{date}.csv")
    print(f"  • Driver data: f1_drivers_{race_name}_{date}.csv")
    print(f"  • All lap times: f1_laps_{race_name}_{date}.csv")
    print(f"  • Race summary: f1_race_summary_{race_name}_{date}.csv")
    print(f"\n📝 You can now:")
    print(f"  • Open these files in Excel or Google Sheets")
    print(f"  • Create charts and visualizations")
    print(f"  • Analyze driver performance")
    print(f"  • Compare lap times across drivers")

def main():
    try:
        generate_report()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()