import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("sensorDB.db")

df = pd.read_sql_query(
    "SELECT datetime, temperature, humidity, pressure FROM sensordata",
    conn
)

df["datetime"] = pd.to_datetime(df["datetime"])

plt.figure()
plt.plot(df["datetime"], df["temperature"], label="Temperature (C)")
plt.plot(df["datetime"], df["humidity"], label="Humidity (%)")
plt.plot(df["datetime"], df["pressure"], label="Pressure (hPa)")
plt.legend()
plt.xlabel("Time")
plt.ylabel("Sensor Values")
plt.title("Sensor Data Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

