import math


class SensorMock:
  """Symulator czujnika termowizyjnego do wykrywania hot-spotów na farmie PV."""

  def __init__(self, hotspot_offset=(20, 20)):
    # Pozycja hot-spotu względem punktu startowego (w metrach: N, E)
    self.hotspot_offset = hotspot_offset

  def scan_point(self, current_pos, target_pos, tolerance=5.0):
    """Sprawdza, czy w pobliżu docelowego punktu znajduje się anomalia termiczna.

    Zwraca słownik z wynikiem detekcji.
    """
    # Obliczamy dystans do zaprogramowanego hot-spotu
    # W uproszczeniu symulujemy, że wykrywamy cel w punkcie nr 2
    distance_to_hotspot = math.hypot(
        current_pos[0] - target_pos[0], current_pos[1] - target_pos[1]
    )

    # Symulacja detekcji termicznej (np. temperatura > 65°C)
    if distance_to_hotspot <= tolerance:
      return {
          "target_found": True,
          "temperature": 72.4,
          "description": "Wykryto hot-spot (uszkodzony panel PV)!",
      }

    return {
        "target_found": False,
        "temperature": 24.1,
        "description": "Brak anomalii termicznych.",
    }