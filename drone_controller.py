import math
import time
from pymavlink import mavutil


class DroneController:

  def __init__(self, connection_string="tcp:127.0.0.1:5762"):
    self.connection_string = connection_string
    self.master = None

  def connect(self, timeout=15):
    print(f"[DRONE] Łączenie z autopilotem: {self.connection_string}...")
    self.master = mavutil.mavlink_connection(self.connection_string)
    if self.master.wait_heartbeat(timeout=timeout) is None:
      raise ConnectionError(
          f"Brak heartbeatu w {timeout}s. Sprawdź, czy SITL działa!"
      )
    print(
        "[DRONE] Połączono pomyślnie: system="
        f"{self.master.target_system}, komponent="
        f"{self.master.target_component}"
    )

  def get_position(self, timeout=5):
    msg = self.master.recv_match(
        type="GLOBAL_POSITION_INT", blocking=True, timeout=timeout
    )
    if msg is None:
      return None
    return msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0

  def set_mode(self, mode, timeout=10):
    print(f"[DRONE] Zmiana trybu na: {mode}")
    self.master.set_mode(mode)
    expected = self.master.mode_mapping()[mode]
    end = time.time() + timeout
    while time.time() < end:
      hb = self.master.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
      if hb is not None and hb.custom_mode == expected:
        print(f"[OK] Tryb aktywny: {mode}")
        return
    raise RuntimeError(f"Nie udało się ustawić trybu {mode}")

  def arm(self, timeout=60):
    print("[DRONE] Uzbrajanie silników (oczekiwanie na GPS/EKF)...")
    end = time.time() + timeout
    while time.time() < end:
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
      hb = self.master.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
      if (
          hb is not None
          and hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
      ):
        print("[OK] Silniki uzbrojone!")
        return
      time.sleep(2)
    raise RuntimeError("Nie udało się uzbroić drona. Sprawdź status GPS.")

  def takeoff(self, alt=10.0):
    print(f"[DRONE] Start pionowy na wysokość {alt}m...")
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
        alt,
    )
    while True:
      pos = self.get_position()
      if pos is None:
        continue
      print(f"    Aktualna wysokość: {pos[2]:.1f} m", end="\r")
      if pos[2] >= alt * 0.95:
        print(f"\n[OK] Osiągnięto wysokość docelową: {pos[2]:.1f} m")
        return
      time.sleep(0.5)

  def goto(self, lat, lon, alt):
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

  def fly_to(self, lat, lon, alt, name, timeout=90, radius=2.0):
    print(f"[DRONE] Lot do: {name} ({lat:.6f}, {lon:.6f}, {alt}m)")
    start = time.time()
    while time.time() - start < timeout:
      self.goto(lat, lon, alt)
      pos = self.get_position(timeout=0.5)
      if pos is None:
        continue

      # Oblicz dystans w metrach
      dn = (lat - pos[0]) * 111_320.0
      de = (lon - pos[1]) * 111_320.0 * math.cos(math.radians(pos[0]))
      dist = math.hypot(dn, de)

      print(f"    dystans: {dist:5.1f} m | wysokość: {pos[2]:5.1f} m", end="\r")
      if dist <= radius:
        print(f"\n[OK] Osiągnięto cel: {name}")
        return True
      time.sleep(0.1)
    raise TimeoutError(f"Przekroczono limit czasu lotu do {name}")

  def return_and_land(self):
    self.set_mode("RTL")
    print("[DRONE] Aktywowano powrót do bazy (RTL) i lądowanie...")
    self.master.motors_disarmed_wait()
    print("[OK] Wylądowano i rozbrojono silniki.")