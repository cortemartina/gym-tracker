# Gym Tracker — Instrucciones de instalación

## Estructura del proyecto
```
gym-tracker/
├── credentials.json     ← TU archivo de credenciales (no compartir)
├── app.py
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

---

## 1. Verificar que tenés Python instalado
```bash
python --version
```
Necesitás Python 3.8 o mayor.

---

## 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 3. Colocar el archivo de credenciales
Pegá tu archivo `credentials.json` (el de Google Cloud Service Account)
en la raíz del proyecto, junto a `app.py`.

---

## 4. Verificar el nombre del Google Sheet
En `app.py`, línea 17, asegurate de que el nombre coincida exactamente
con el de tu Google Sheet:
```python
SPREADSHEET_NAME = "Gym Tracker"  # ← cambiá si es necesario
```

---

## 5. Correr la app
```bash
python app.py
```
Deberías ver algo como:
```
 * Running on http://0.0.0.0:5000
```

---

## 6. Acceder desde el celular
1. Asegurate de que la PC y el celular estén en la **misma red WiFi**
2. Encontrá la IP local de tu PC:
   - Windows: `ipconfig` → buscá "Dirección IPv4"
   - Mac/Linux: `ifconfig` o `ip a`
3. En el celular, abrí el navegador y entrá a: `http://[TU-IP]:5000`
   Ejemplo: `http://192.168.1.105:5000`

**Tip:** Podés agregar la página a la pantalla de inicio del celular
para que funcione como una app.

---

## Estructura de Google Sheets
La app crea automáticamente dos hojas:

### Hoja `Templates`
| dia | seccion | ejercicio | sets | reps |
|-----|---------|-----------|------|------|
| 1   | activacion | Banda escapular | 3 | 15 |
| 1   | A | Sentadilla | 4 | 8 |
| ... | ... | ... | ... | ... |

### Hoja `Log`
| session_id | fecha | semana | dia | seccion | ejercicio | sets | reps | peso |
|------------|-------|--------|-----|---------|-----------|------|------|------|
| 1748000000 | 20/5/2025 | 1 | 1 | A | Sentadilla | 4 | 8 | 80 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Flujo de uso
1. **Primera vez:** ir a "Rutinas" y cargar los 4 días de entrenamiento
2. **Cada día de entreno:**
   - Elegir la semana (1-4)
   - Elegir el día (1-4)
   - Cargar los pesos usados
   - Tocar "Guardar entrenamiento"
3. **Historial:** ver y editar entrenamientos pasados en la pestaña "Historial"
