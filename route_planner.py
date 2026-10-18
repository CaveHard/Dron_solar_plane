import math


class RoutePlanner:
  """Modul odpowiedzialny za planowanie trasy np. siatka inspekcyjna dla farm PV

  lub dachów budynków.
  """

  @staticmethod
  def generate_grid_route(home_lat, home_lon, width_m=40, height_m=40, step=20):
    """Generuje siatkę punktów (grid) do przeszukania obszaru.

    TODO:
    - Dodanie algorytmów optymalizacji trasy (Travelling Salesperson Problem).
    - Obsługa nieregularnych wielokątów (poligonów wyznaczających dach budynku).
    """
    waypoints = []
    print(
        f"[PLANNER] Generowanie siatki trasy: {width_m}x{height_m}m co {step}m"
    )

    for n in range(0, height_m + 1, step):
      # Przykładowy wzór zygzaka (lawnmower pattern)
      if (n // step) % 2 == 0:
        row = [(n, 0), (n, width_m)]
      else:
        row = [(n, width_m), (n, 0)]

      for n_off, e_off in row:
        dlat = n_off / 111_320.0
        dlon = e_off / (111_320.0 * math.cos(math.radians(home_lat)))
        waypoints.append((home_lat + dlat, home_lon + dlon, 15.0))

    return waypoints