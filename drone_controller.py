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
      raise ConnectionError("Brak heartbeatu. Sprawdź czy SITL działa.")
    print("[DRONE] Połączono pomyślnie z symulatorem.")

  def get_position(self, timeout=5):
    """TODO :

    - Rozbudowa o odczyt poziom baterii, prędkość wiatru itp
    """
    msg = self.master.recv_match(
        type="GLOBAL_POSITION_INT", blocking=True, timeout=timeout
    )
    if msg is None:
      return None
    return msg.lat / 1e7, msg.lon / 1e7, msg.relative_alt / 1000.0

  def set_mode(self, mode, timeout=10):
    self.master.set_mode(mode)
    expected = self.master.mode_mapping()[mode]
    end = time.time() + timeout
    while time.time() < end:
      hb = self.master.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
      if hb is not None and hb.custom_mode == expected:
        return
    raise RuntimeError(f"Nie udało się zmienić trybu na {mode}")

  def arm_and_takeoff(self, alt=15.0):
    print("[DRONE] Uzbrajanie i start...")
    self.set_mode("GUIDED")

    # Uzbrojenie
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
    time.sleep(3)

    # Start
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
    time.sleep(6)
    print(f"[OK] Osiągnięto wysokość startową: {alt}m")

  def fly_to(self, lat, lon, alt, name, timeout=60, radius=2.0):
    print(f"[DRONE] Lot do: {name}")
    start = time.time()
    while time.time() - start < timeout:
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

      dn = (lat - pos[0]) * 111_320.0
      de = (lon - pos[1]) * 111_320.0 * math.cos(math.radians(pos[0]))
      dist = math.hypot(dn, de)

      print(f"    dystans: {dist:5.1f} m", end="\r")
      if dist <= radius:
        print(f"\n[OK] Dotarto do: {name}")
        return True
      time.sleep(0.1)
    raise TimeoutError(f"Nie dotarto do celu: {name}")

  def return_and_land(self):
    print("[DRONE] Powrót do bazy (RTL)...")
    self.set_mode("RTL")