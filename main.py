import sys
import time
from drone_controller import DroneController
from route_planner import RoutePlanner
from sensor_mock import SensorMock

CONNECTION = "tcp:127.0.0.1:5762"


def main():
  print("=== ROZPOCZĘCIE MISJI: TERMOCHMICZNA INSPEKCJA (PV / DACHY BUDYNKÓW) ===")

  drone = DroneController(CONNECTION)
  sensor = SensorMock(random_hotspot=True)  # Losowanie miejsca anomalii w teście

  drone.connect()

  print("[INFO] Oczekiwanie na pozycję Home GPS...")
  home = None
  while home is None:
    home = drone.get_position()
  home_lat, home_lon, _ = home
  print(f"[OK] Start w bazie: {home_lat:.6f}, {home_lon:.6f}")

  drone.arm_and_takeoff(alt=15.0)

  # Faza 1: Generowanie trasy przez RoutePlanner
  mission_waypoints = RoutePlanner.generate_grid_route(
      home_lat, home_lon, width_m=30, height_m=30, step=15
  )

  anomaly_detected = False

  # Faza 2: Przelot po zaplanowanej trasa i skanowanie
  for idx, (lat, lon, alt) in enumerate(mission_waypoints, start=1):
    drone.fly_to(lat, lon, alt, f"Punkt Trasy {idx}")

    # Symulacja pozycji w metrach względem bazy do testu sensora
    current_m = (idx * 10, idx * 5)
    scan_result = sensor.scan_area(current_m)

    print(f"[SENSOR STATUS] {scan_result['description']}")

    # Faza 3: Reakcja systemu na wykrycie  hot-spot
    if scan_result["target_found"] and not anomaly_detected:
      anomaly_detected = True
      print(
          "[REAKCJA SYSTEMU] Wykryto hot-spot! Wykonuję"
      )
      print(
          "[REAKCJA SYSTEMU] Manewr inspekcyjny (zmniejszenie wysokości i"
          " zawis nad celem)..."
      )

      # Zmniejszenie wysokości nad celem dla lepszej rozdzielczości termowizyjnej
      drone.fly_to(lat, lon, 8.0, "Zawis inspekcyjny nad anomalią")
      time.sleep(3)

  # Faza 4: Powrót i lądowanie
  print("[INFO] Misja zakończona. Powrót do bazy...")
  drone.return_and_land()
  print("=== MISJA ZAKOŃCZENIA SUKCESEM ===")


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"\n[BŁĄD] {e}")
    sys.exit(1)