import json
import pandas as pd
from urllib.request import urlopen
from urllib.parse import quote

# Obtener todos los meetings
response = urlopen("https://api.openf1.org/v1/meetings")
meetings = json.loads(response.read().decode('utf-8'))

# Filtrar por años 2023-2025 y extraer circuit_short_name y country únicos
years = {2023, 2024, 2025}
circuit_set = {
    (m['circuit_short_name'], m['country_name'])
    for m in meetings if int(m['year']) in years
}

# Crear DataFrame con nombre legible y codificado para URL
df_circuits = pd.DataFrame(
    sorted(list(circuit_set)),
    columns=['Circuit', 'Country']
)
df_circuits['circuit_for_URL'] = df_circuits['Circuit'].apply(lambda x: quote(str(x))) # Codificar para URL

# Guardar el CSV final
df_circuits.to_csv('Circuits.csv', index=False)

print("Circuits.csv generado con columnas:")