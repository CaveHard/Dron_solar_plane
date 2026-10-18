import math
import sys
import time
from drone_controller import DroneController
from sensor_mock import SensorMock

# Konfiguracja misji
CONNECTION = "tcp:127.0.0.1:5762"
TAKEOFF_ALT = 15.0

# Trasa inspekcyjna farmy PV (przesunięcia N, E w metrach)
MISSION_GRID = [
    (30, 0, 15),  # Punkt 1: początek sektora
    (30, 30, 15),  # Punkt 2: przelot nad sektorem (tu symulujemy hot-spot)
    (0, 30, 15),  # Punkt 3: powrót korytarzem
]


def offset_to_latlon(lat, lon, north_m, east_m):
  dlat = north_m / 111_320.0
  dlon = east_m / (111_320.0 * math.cos(math.radians(lat)))
  return lat + dlat, lon + dlon


def main():
  print("=== ROZPOCZĘCIE MISJI: INSPEKCJA TERMOCHMICZNA FARMY PV ===")
  drone = DroneController(CONNECTION)
  sensor = SensorMock()

  drone.connect()

  # Czekam na pozycję bazową GPS
  print("[INFO] Oczekiwanie na sygnał GPS i pozycję Home...")
  home = None
  while home is None:
    home = drone.get_position()
  home_lat, home_lon, _ = home
  print(f"[OK] Pozycja Startowa (Home): {home_lat:.6f}, {home_lon:.6f}")

  # Procedura startowa
  drone.set_mode("GUIDED")
  drone.arm()
  drone.takeoff(TAKEOFF_ALT)

  hotspot_detected = False
  target_lat, target_lon = 0.0, 0.0

  # Faza 2: Przelot po wyznaczonej trasie (skanowanie)
  for i, (north, east, alt) in enumerate(MISSION_GRID, start=1):
    lat, lon = offset_to_latlon(home_lat, home_lon, north, east)
    drone.fly_to(lat, lon, alt, f"Sektor {i}")

    # Faza 3 & 4: Użycie sensora i reakcja systemu
    # Sprawdzamy na drugim punkcie trasy, czy sensor wykrył anomalię
    current_pos_m = (north, east)
    scan_result = sensor.scan_point(current_pos_m, target_pos=(30, 30))

    print(f"\n[SENSOR] Status: {scan_result['description']}")

    if scan_result["target_found"] and not hotspot_detected:
      hotspot_detected = True
      target_lat, target_lon = lat, lon
      print(
          "[REAKCJA SYSTEMU] Wykryto uszkodzenie ogniwa! Przerywam standardowe"
          " skanowanie i rozpoczynam manewr inspekcyjny (orbitę)..."
      )

      # Faza 4 cd.: Manewr wokół hot-spotu (krążenie 360 stopni - 4 punkty wokół celu)
      radius = 10.0  # promień 10 metrów
      for angle_deg in [0, 90, 180, 270]:
        rad = math.radians(angle_deg)
        n_off = 30 + radius * math.cos(rad)
        e_off = 30 + radius * math.sin(rad)
        h_lat, h_lon = offset_to_latlon(home_lat, home_lon, n_off, e_off)
        drone.fly_to(
            h_lat, h_lon, alt, f"Punkt inspekcyjny {angle_deg}° wokół hot-spotu"
        )

    time.sleep(1)

  # Faza 5: Powrót i lądowanie
  print("[INFO] Misja zakończona. Powrót do bazy (RTL)...")
  drone.return_and_land()
  print("=== MISJA ZAKOŃCZONA PEŁNYM SUKCESEM ===")


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("\n[STOP] Przerwano przez użytkownika.")
    sys.exit(1)
  except Exception as exc:
    print(f"\n[BŁĄD KRYTYCZNY] {exc}")
    sys.exit(1)