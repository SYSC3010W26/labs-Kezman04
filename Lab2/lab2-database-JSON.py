import sqlite3
import requests
from datetime import datetime

# Paste your OpenWeatherMap API key here (keep the quotes)
API_KEY = "4f9a8677068e2cc616435dfbf4db21c9"

# Cities to test (you can add more)
CITIES = ["Ottawa", "Toronto", "Montreal"]

DB_NAME = "sensorDB.db"

def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Winds table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Winds (
        City TEXT,
        Date TEXT,
        WindSpeed REAL
    )
    """)
    conn.commit()

    for city in CITIES:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        try:
            response = requests.get(url, timeout=10)
            data = response.json()
        except Exception as e:
            print(f"{city}: request failed -> {e}")
            continue

        # If API returns an error, it won't have "wind"
        if "wind" not in data or "speed" not in data["wind"]:
            # Print full error response so you can see what happened (401, 429, etc.)
            print(f"{city}: API error -> {data}")
            continue

        wind_speed = float(data["wind"]["speed"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get most recent wind speed for this city
        cursor.execute("""
            SELECT WindSpeed FROM Winds
            WHERE City = ?
            ORDER BY Date DESC
            LIMIT 1
        """, (city,))
        prev = cursor.fetchone()

        if prev is None:
            print(f"{city}: first wind entry ({wind_speed} m/s)")
        else:
            prev_speed = float(prev[0])
            if wind_speed > prev_speed:
                print(f"{city}: wind speed increased ({prev_speed} -> {wind_speed} m/s)")
            elif wind_speed < prev_speed:
                print(f"{city}: wind speed decreased ({prev_speed} -> {wind_speed} m/s)")
            else:
                print(f"{city}: wind speed unchanged ({wind_speed} m/s)")

        # Insert new row
        cursor.execute(
            "INSERT INTO Winds (City, Date, WindSpeed) VALUES (?, ?, ?)",
            (city, timestamp, wind_speed)
        )
        conn.commit()

    conn.close()

if __name__ == "__main__":
    main()

