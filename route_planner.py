import math


class RoutePlanner:
  """Generator tras (siatek inspekcyjnych) dla drona."""

  @staticmethod
  def generate_grid_route(
      home_lat,
      home_lon,
      offset_n=0,
      offset_e=0,
      width_m=30,
      height_m=30,
      step=15,
  ):
    """Generuje punkty w formie zygzaka (lawnmower) dla wybranego sektora

    Przesunięty o offset_n (północ) i offset_e (wschód) względem bazy.
    """
    waypoints = []
    print(
        f"[PLANNER] Generuję siatkę przelotu (offset N:{offset_n}m,"
        f" E:{offset_e}m)..."
    )

    # Przeliczamy przesunięcia w metrach na stopnie geograficzne
    base_dlat = offset_n / 111_320.0
    base_dlon = offset_e / (111_320.0 * math.cos(math.radians(home_lat)))
    sector_lat = home_lat + base_dlat
    sector_lon = home_lon + base_dlon

    # TODO: można tu dodac algorytm obsługujący
    # nieregularne wielokąty (do dachow) zamiast prostych prostokątów

    for n in range(0, height_m + 1, step):
      # Zygzak: raz w lewo, raz w prawo
      if (n // step) % 2 == 0:
        row = [(n, 0), (n, width_m)]
      else:
        row = [(n, width_m), (n, 0)]

      for n_off, e_off in row:
        dlat = n_off / 111_320.0
        dlon = e_off / (111_320.0 * math.cos(math.radians(sector_lat)))
        waypoints.append((sector_lat + dlat, sector_lon + dlon, 15.0))

    return waypoints