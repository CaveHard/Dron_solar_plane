import math
import random


class SensorMock:
  """Symulacja sensora termowizyjnego do wykrywania hot-spotow"""

  def __init__(self, random_hotspot=True):
    # Losujemy pozycję usterki zeeby testy były za każdym razem inne
    if random_hotspot:
      self.hotspot_offset = (random.randint(10, 25), random.randint(10, 25))
    else:
      self.hotspot_offset = (15, 15)

    print(
        "[SENSOR] Zainicjalizowano sensor. Ukryta anomalia w koordynatach"
        f" lokalnych: {self.hotspot_offset}"
    )

  def scan_area(self, current_pos_m, tolerance=5.0):
    # TODO: dodac tutaj model OpenCV/AI
    # analizujący strumień wideo z kamery zamontowanej na dronie.

    distance = math.hypot(
        current_pos_m[0] - self.hotspot_offset[0],
        current_pos_m[1] - self.hotspot_offset[1],
    )

    if distance <= tolerance:
      return {
          "target_found": True,
          "temperature": random.uniform(68.0, 82.5),
          "description": (
              "UWAGA! Wykryto hot-spot"
          ),
      }

    return {
        "target_found": False,
        "temperature": random.uniform(19.0, 24.0),
        "description": "Temperatura w normie.",
    }