#  Misja Inspekcyjna Drona 

Projekt w ramach zadania rekrutacyjnego do Solar Plane AGH z wykorzystaniem Pythona, biblioteki pymavlink oraz symulatora ArduPilot SITL w Mission Plannerze.

---

## 1. Koncepcja misji
Dron ma przygotowane obszary, nad którymi sprawdza kamera termowizyją czy nie dochodzi do jakiś anomali (straty ciepła w budynku, w fatowotalice hotspoty). Jeśli wykryje anomalię doknuje inspekcji/zawisu nad celem.

---

## 2. Przebieg prawidłowego scenariusza
1. **Inicjalizacja i połączenie:** Nawiązanie bezpiecznego połączenia TCP z symulatorem ArduPilot SITL oraz oczekiwanie na stabilną pozycję GPS (`Home`).
2. **Start i wznoszenie:** Automatyczne uzbrojenie silników w trybie `GUIDED` i start pionowy na zadaną wysokość operacyjną (15 m).
3. **Wielosektorowe skanowanie (Siatka trasy):** Dron przelatuje kolejno przez zdefiniowane sektory, wykonując plan trasy metodą „koszenia trawnika” (*lawnmower pattern* / zygzak).
4. **Detekcja i reakcja:** W trakcie przelotu moduł sensorów (`SensorMock`) stale monitoruje otoczenie. W przypadku wykrycia anomalii termicznej (przekroczenia normy temperaturowej):
   * System rejestruje problem.
   * Dron przerywa standardowy przelot, obniża wysokość i wykonuje precyzyjny zawis inspekcyjny nad celem.
5. **Powrót i lądowanie:** Po ukończeniu inspekcji wszystkich sektorów system aktywuje tryb powrotu do bazy, a dron bezpiecznie ląduje i rozbraja silniki.

---

## 3. Architektura rozwiązania i komponenty
Projekt opiera się na czystej architekturze modułowej:
* **`drone_controller.py`** – Obsługa protokołu MAVLink (`pymavlink`), zarządzanie trybami lotu, uzbrajaniem, startem i sterowaniem pozycji (`GUIDED`).
* **`route_planner.py`** – Generator tras obliczający siatkę przelotu dla wielu niezależnych sektorów na podstawie przesunięć metrowych względem bazy.
* **`sensor_mock.py`** – Symulator kamery termowizyjnej obsługujący losowe rozmieszczanie hot-spotów w celach testowych.
* **`main.py`** – Integrująca wszystkie komponenty i zarządzająca przebiegiem misji.
* **`test_mission.py`** – Automatyczne testy jednostkowe (`pytest`) weryfikujące poprawność generatora tras i logiki sensora.

---

## 4. Wymagania wstępne
* System operacyjny: Windows 10 / 11
* Środowisko: Python 3.10 +
* Oprogramowanie symulacyjne: Mission Planner z zainstalowanym symulatorem ArduPilot SITL (Multirotor).

---

## 5. Instrukcja uruchomienia symulacji (SITL)
1. Uruchom program Mission Planner.
2. Przejdź do zakładki Simulation, wybierz ikonę z dronę (Multirotor*) i kliknij i urucha symulacje
3. Poczekaj, aż symulator załaduje model, upewnij się, że port TCP ( 5762 )jest dostępny.

---

## 6. Instrukcja uruchomienia programu
1. Sklonuj repozytorium lub otwórz folder projektu w środowisku (np. PyCharm).
2. W terminalu utwórz i zainstaluj wymagane biblioteki:
   ```bash
   pip install pymavlink pytest
3. Upewnij się, że symulacja w ArduPilot SITL w Mission Plannerze jest uruchomiony nastepnie uruchą głwóny skrypt misji 
    ```bash
    python main.py
---
## 7.Sposób uruchomienia testów jednostkowych
Projekt posiada automatyczne testy weryfikujące poprawność matematyczną generatora tras oraz logikę detekcji anomalii.
Aby wykonać testy, wpisz w terminalu aktywnego środowiska:
     ```bash
    python -m pytest
---
## 8. Przygotowane scenariusze testowe i ich oczekiwane wyniki
W pliku `test_mission.py` zaimplementowano następujące testy jednostkowe:
* **Test generatora tras (`test_route_planner_generation`):** Weryfikuje, czy algorytm poprawnie generuje punkty nawigacyjne siatki dla zadanego obszaru i czy wysokość jest stała (15 m). *Oczekiwany wynik:* Wszystkie punkty zostają wygenerowane poprawnie, test kończy się statusem `PASSED`.
* **Test stochastyczny sensora (`test_sensor_mock_stochastic`):** Sprawdza, czy mock sensora losuje pozycję anomalii i poprawnie zwraca strukturę słownika z polem decyzyjnym oraz temperaturą. *Oczekiwany wynik:* Prawidłowa struktura danych, test ze statusem `PASSED`.
* **Test wymiarów siatki (`test_route_planner_dimensions`):** Sprawdza, czy generator tworzy odpowiednią liczbę rzędów i punktów dla zadanego kroku. *Oczekiwany wynik:* `PASSED`.
* **Test tolerancji odległości (`test_sensor_detection_outside_tolerance`):** Weryfikuje, czy system poprawnie ignoruje obiekty znajdujące się poza zadaną tolerancją czujnika. *Oczekiwany wynik:* `target_found` zwraca `False`, test ze statusem `PASSED`.

---

## 9. Przyjęte uproszczenia i elementy, których nie udało się zasymulować
* **Mockowanie czujnika termowizyjnego:** Zamiast rzeczywistego strumienia wideo z kamery termowizyjnej oraz modeli uczenia maszynowego (AI/OpenCV), zastosowano klasę `SensorMock`, która symuluje detekcję na podstawie odległości metrowej od ukrytej anomalii.
* **Uproszczona konwersja współrzędnych:** Do przeliczania metrowych przesunięć na stopnie geograficzne zastosowano przybliżenia (uwzględniające szerokość geograficzną i cosinus), co w zupełności występuje dla lokalnych misji inspekcyjnych.

---

## 10. Pomysły na dalszy rozwój (TODO)
* **Obsługa nieregularnych powieszchni:** Rozbudowa planisty trasy RoutePlanner o algorytmy docinające siatkę przelotu do rzeczywistych, nieregularnych kształtów dachów budynków.
* **Integracja z komputerem pokładowym i AI:** Zastąpienie SensorMock faktycznym skryptem analizującym strumień z kamery za pomocą OpenCV i sieci neuronowych uruchamianych np. malince
* **Optymalizacja kolejności odwiedzania sektorów:** Wprowadzenie algorytmów optymalizacyjnych do wyznaczenia najlepszej trasy do skanowania sektorów