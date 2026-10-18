from sensor_mock import SensorMock


def test_sensor_mock_detection():
  sensor = SensorMock(hotspot_offset=(30, 30))

  # Test 1: Pozycja blisko hot-spotu (powinna nastąpić detekcja)
  result_positive = sensor.scan_point(
      current_pos=(30, 30), target_pos=(30, 30), tolerance=5.0
  )
  assert result_positive["target_found"] is True
  assert result_positive["temperature"] > 60.0

  # Test 2: Pozycja z dala od hot-spotu (brak detekcji)
  result_negative = sensor.scan_point(
      current_pos=(0, 0), target_pos=(30, 30), tolerance=5.0
  )
  assert result_negative["target_found"] is False