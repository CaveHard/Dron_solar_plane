import sys
import time
from drone_controller import DroneController
from route_planner import RoutePlanner
from sensor_mock import SensorMock

# Port dla SITL w Mission Plannerze
CONNECTION_STR = "tcp:127.0.0.1:5762"


def main():
  print("=== START MISJI: SPRAWDZENIE USTEREK TERMICZNYCH W ROZNYCH SEKTORACH ===")

  drone = DroneController(CONNECTION_STR)
  sensor = SensorMock(random_hotspot=True)

  drone.connect()

  print("[INFO] Czekam na złapanie pozycji GPS (Home)...")
  home_pos = None
  while home_pos is None:
    home_pos = drone.get_position()
  home_lat, home_lon, _ = home_pos
  print(f"[OK] Pozycja bazowa ustalona: {home_lat:.6f}, {home_lon:.6f}")

  drone.arm_and_takeoff(target_alt=15.0)

  # Definiujemy kilka różnych obszarów do zbadania w trakcie jednego lotu
  sectors_to_inspect = [
      {
          "name": "Sektor A",
          "offset_n": 15,
          "offset_e": 0,
      },
      {"name": "Sektor B", "offset_n": 45, "offset_e": 30},
  ]

  anomaly_spotted = False

  # Pętla po wszystkich zaplanowanych sektorach
  for sector in sectors_to_inspect:
    print(f"\n--------------------------------------------------")
    print(f"[LOT] Przelot do nowego obiektu: {sector['name']}")
    print(f"--------------------------------------------------")

    # Generujemy siatkę dla bieżącego sektora
    waypoints = RoutePlanner.generate_grid_route(
        home_lat,
        home_lon,
        offset_n=sector["offset_n"],
        offset_e=sector["offset_e"],
        width_m=20,
        height_m=20,
        step=10,
    )

    # Lecimy po punktach siatki
    for idx, (lat, lon, alt) in enumerate(waypoints, start=1):
      drone.fly_to(lat, lon, alt, f"{sector['name']} - pkt {idx}")

      # Symulacja skanowania w tym punkcie
      # przekazujemy przyblirzone metry do sensora
      scan_res = sensor.scan_area((sector["offset_n"] + idx, sector["offset_e"]))
      print(f"    [KAMERA] {scan_res['description']}")

      # Reakcja systemu na wykrycie hotspotu
      if scan_res["target_found"] and not anomaly_spotted:
        anomaly_spotted = True
        print(
            "\n[REAKCJA] Znaleziono hot-spot! Przerywam skanowanie i robię"
            " dokładny zawis inspekcyjny..."
        )
        drone.fly_to(lat, lon, 8.0, "Zawis nad anomalia")
        time.sleep(3)
        print("[REAKCJA] Wznawiam plan misji...\n")

    print(f"[OK] Sektor oblatany: {sector['name']}")
    time.sleep(1)

  # Koniec misji - powrót
  print("\n[INFO] Wszystkie sektory sprawdzone. Wracam do bazy")
  drone.return_and_land()
  print("=== MISJA ZAKOŃCZONA SUKCESEM ===")


if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"\n[BŁĄD] Coś poszło nie tak: {e}")
    sys.exit(1)