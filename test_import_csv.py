import urllib.request
import json
from f1reportsV2 import F1Reporter

def test_import_drivers_to_csv():
    # Descarga todos los pilotos
    url = "https://api.openf1.org/v1/drivers"
    try:
        with urllib.request.urlopen(url) as response:
            drivers = json.loads(response.read().decode())
            print(f"Total drivers fetched: {len(drivers)}")
    except Exception as e:
        print(f"Error fetching drivers: {e}")
        return

    # Descarga resultados de 2024
    url_results = "https://api.openf1.org/v1/results?session_key>=11000"  # Ajusta el session_key según la docu
    try:
        with urllib.request.urlopen(url_results) as response:
            results = json.loads(response.read().decode())
            print(f"Total results fetched: {len(results)}")
    except Exception as e:
        print(f"Error fetching results: {e}")
        return

    # Obtén los driver_numbers que participaron en 2024
    drivers_2024 = set(r['driver_number'] for r in results if 'driver_number' in r)

    # Filtra los pilotos y quita la foto
    filtered = []
    for d in drivers:
        if d.get('driver_number') in drivers_2024:
            d = dict(d)
            d.pop("headshot_url", None)
            filtered.append(d)
    print(f"Filtered drivers (2024, no photo): {len(filtered)}")

    reporter = F1Reporter()
    filename = r"C:\Users\agust\Desktop\PythonF1\test_drivers.csv"
    result = reporter.save_to_csv(filtered, filename)
    print("CSV saved:", result)

if __name__ == "__main__":
    test_import_drivers_to_csv()