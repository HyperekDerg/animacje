# Lab 11 – Animowanie rośliny poprzez skrypt

## Co zostało zrealizowane

Zrealizowano hybrydowe podejście do animacji: asset rośliny stworzony w Lab 07 (GUI) został ożywiony proceduralnie za pomocą skryptu Python (`roslina_animacja_geometrii.py`) uruchomionego przez Blender Python API (`bpy`).

Skrypt realizuje następujące zadania:

- **Import rośliny** – wczytanie kolekcji `Roslina_Hero` z pliku `.blend` (Lab 07) za pomocą `bpy.ops.wm.append()`
- **Animacja liści** – sinusoidalne kołysanie każdego liścia (oś Y rotacji) z indywidualną fazą, wstawiane klatka po klatce przez `keyframe_insert()`
- **Animacja pąka** – skalowanie obiektu `Roslina_Pak` od wartości minimalnej do maksymalnej w klatkach 30–90
- **Konfiguracja sceny** – ustawienie zakresu animacji (klatki 1–125) oraz liczby klatek na sekundę (25 FPS)
- **Dodanie oświetlenia i kamery** – scena uzupełniona przez skrypt o kamerę oraz układ oświetlenia

## Render wynikowy

Render animacji zapisano w pliku `.mp4`.
