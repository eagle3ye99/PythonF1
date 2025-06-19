import json
import pandas as pd
from urllib.request import urlopen

# Obtener todos los meetings
response = urlopen("https://api.openf1.org/v1/meetings")
meetings = json.loads(response.read().decode('utf-8'))

# Filtrar por años 2023-2025 y extraer country_name únicos
years = {2023, 2024, 2025}
countries = sorted({m['country_name'] for m in meetings if int(m['year']) in years})

# Guardar a un CSV
df_countries = pd.DataFrame({'country': countries})
df_countries.to_csv('countries.csv', index=False)

print("Countries saved to 'Countries.csv'.")