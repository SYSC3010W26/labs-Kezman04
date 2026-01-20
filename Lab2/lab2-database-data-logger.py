import sqlite3
from sense_hat import SenseHat
from datetime import datetime
import time

# Initialize Sense HAT
sense = SenseHat()

# Connect to SQLite database
conn = sqlite3.connect("sensorDB.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensordata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    temperature REAL,
    humidity REAL,
    pressure REAL
)
""")

conn.commit()

print("Logging sensor data... Press CTRL+C to stop.")

try:
    while True:
        temperature = sense.get_temperature()
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO sensordata (datetime, temperature, humidity, pressure) VALUES (?, ?, ?, ?)",
            (timestamp, temperature, humidity, pressure)
        )

        conn.commit()

        print(timestamp, temperature, humidity, pressure)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping logger...")

finally:
    conn.close()
