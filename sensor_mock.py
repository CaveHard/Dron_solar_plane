import math
import random


class SensorMock:
  """Symulator czujnika termowizyjnego

  """

  def __init__(self, random_hotspot=True):
    # Losowanie pozycji anomalii hot-spotu do testów
    if random_hotspot:
      # Losowe przesunięcie w metrach (N, E)
      self.hotspot_offset = (random.randint(10, 30), random.randint(10, 30))
    else:
      self.hotspot_offset = (20, 20)

    print(
        "[SENSOR_INIT] Zainicjalizowano sensor termowizyjny."
        f" Ukryta anomalia w offsetach: {self.hotspot_offset}"
    )

  def scan_area(self, current_pos_m, tolerance=5.0):
    """Skanuje otoczenie w poszukiwaniu anomalii temperaturowych

    TODO :
    - Podpięcie  AI / biblioteki OpenCV do analizy klatek wideo z kamery
    - Klasyfikacja ciężaru uszkodzenia (lekka czy krytyczny hot-spot).
    """
    distance = math.hypot(
        current_pos_m[0] - self.hotspot_offset[0],
        current_pos_m[1] - self.hotspot_offset[1],
    )

    if distance <= tolerance:
      return {
          "target_found": True,
          "temperature": random.uniform(65.0, 85.0),
          "description": (
              "WYKRYTO ANOMALIĘ! (Hot-spot na panelu PV lub wyciek ciepła z"
              " dachu budynku)"
          ),
      }

    return {
      "target_found": False,
      "temperature": random.uniform(18.0, 25.0),
      "description": "Norma termiczna. Brak strat ciepła.",
    }