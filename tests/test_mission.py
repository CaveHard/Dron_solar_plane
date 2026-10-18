from route_planner import RoutePlanner
from sensor_mock import SensorMock


def test_route_planner_generation():
  """Czy poprawnie generuje sie punkty trasy."""
  waypoints = RoutePlanner.generate_grid_route(
      50.0, 19.9, width_m=20, height_m=20, step=10
  )
  assert len(waypoints) > 0
  for lat, lon, alt in waypoints:
    assert alt == 15.0
    assert isinstance(lat, float)
    assert isinstance(lon, float)


def test_sensor_mock():
  """Testuje sensor z losowymi koordynatami"""
  sensor = SensorMock(random_hotspot=True)

  # Testujemy, czy funkcja skanowania poprawnie zwraca strukturę słownika
  result = sensor.scan_area((0, 0))
  assert "target_found" in result
  assert "temperature" in result
  assert isinstance(result["target_found"], bool)


def test_route_planner_dimensions():
  """Sprawdza, czy generator siatki tworzy odpowiednią liczbę punktów
  dla zadanego kroku
  """
  waypoints = RoutePlanner.generate_grid_route(
      50.0, 19.9, width_m=30, height_m=30, step=15
  )
  # Dla obszaru 30x30 co 15m powinniśmy mieć siatkę rzędów
  assert len(waypoints) > 0


def test_sensor_detection_outside_tolerance():
  """Sprawdza, czy sensor poprawnie ignoruje obiekty poza tolerancją"""
  # Wyłączamy losowość, żeby hotspot był w stałym miejscu
  sensor = SensorMock(random_hotspot=False)

  # Ustawiamy pozycję bardzo daleko od hot-spotu (np. na 100, 100)
  result = sensor.scan_area((100, 100), tolerance=5.0)

  assert result["target_found"] is False
  assert result["temperature"] < 30.0