import math
import time
from pymavlink import mavutil


class DroneController:
  """Klasa do sterowania dronem przez MAVLink

  Obsługuje połączenie, uzbrajanie, start i lot po punktach.
  """

  def __init__(self, connection_string="tcp:127.0.0.1:5762"):
    self.connection_string = connection_string
    self.master = None

  def connect(self, timeout=15):
    print(f"[DRONE] Próbuję połączyć się z: {self.connection_string}...")
    self.master = mavutil.mavlink_connection(self.connection_string)

    # Czekamy na pierwszy pakiet heartbeat od SITL
    hb = self.master.wait_heartbeat(timeout=timeout)
    if hb is None:
      raise ConnectionError(
          "Nie udało się połączyć! Sprawdź czy SITL w Mission Plannerze działa."
      )
    print("[DRONE] Połączenie z autopilotem nawiązane pomyślnie.")

  def get_position(self, timeout=5):
    # TODO: w przyszłości warto tu wrzucić odczyt z innych sensorów
    # (np. stan baterii, prędkość wiatru z telemetrii)
    msg = self.master.recv_match(
        type="GLOBAL_POSITION_INT", blocking=True, timeout=timeout
    )
    if msg is None:
      return None
    return msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0

  def set_mode(self, mode_name, timeout=10):
    self.master.set_mode(mode_name)
    target_mode = self.master.mode_mapping()[mode_name]

    end_time = time.time() + timeout
    while time.time() < end_time:
      hb = self.master.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
      if hb and hb.custom_mode == target_mode:
        return
    raise RuntimeError(f"Nie udało się zmienić trybu na {mode_name}")

  def arm_and_takeoff(self, target_alt=15.0):
    print("[DRONE] Zmieniam tryb na GUIDED i uzbrajam silniki...")
    self.set_mode("GUIDED")

    # Komenda uzbrojenia
    self.master.mav.command_long_send(
        self.master.target_system,
        self.master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
    )
    time.sleep(2)

    print(f"[DRONE] Startuję na wysokość {target_alt}m...")
    self.master.mav.command_long_send(
        self.master.target_system,
        self.master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        target_alt,
    )
    time.sleep(5)
    print("[OK] Wznoszenie zakończone.")

  def fly_to(self, lat, lon, alt, waypoint_name, timeout=60, radius=2.0):
    print(f"[DRONE] Lecę do: {waypoint_name}")
    start_time = time.time()

    while time.time() - start_time < timeout:
      # Wysyłamy pozycję docelową (ArduPilot w GUIDED tego wymaga ciągle !!!)
      self.master.mav.set_position_target_global_int_send(
          0,
          self.master.target_system,
          self.master.target_component,
          mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
          0b0000111111111000,
          int(lat * 1e7),
          int(lon * 1e7),
          alt,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
      )

      pos = self.get_position(timeout=0.5)
      if pos is None:
        continue

      # Liczymy prosty dystans w metraach do celu
      d_north = (lat - pos[0]) * 111_320.0
      d_east = (lon - pos[1]) * 111_320.0 * math.cos(math.radians(pos[0]))
      distance = math.hypot(d_north, d_east)

      print(f"    dystans do celu: {distance:5.1f} m", end="\r")

      if distance <= radius:
        print(f"\n[OK] Osiągnięto punkt: {waypoint_name}")
        return True

      time.sleep(0.1)

    raise TimeoutError(f"Minął limit czasu na dolot do {waypoint_name}")

  def return_and_land(self):
    print("[DRONE] Aktywuję powrót do bazy (RTL)...")
    self.set_mode("RTL")