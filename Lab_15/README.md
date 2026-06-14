# Lab 15 – Projekt Końcowy – Miasto Nocą

## Co zostało zrealizowane

Stworzono animację POV przejścia przez deszczowe i zamglone, mroczne miasto nocą. Kamera symuluje chód z kołysaniem bocznym i pionowym, oddechem oraz organicznym drganiem generowanym przez sumę sinusoid (smooth noise). Scena zawiera ulicę z chodnikiem otoczoną budynkami z neonami, samochody jadące z włączonymi reflektorami, system cząsteczkowy deszczu oraz mokrą nawierzchnię z odbiciami świateł.

Modele neonów i samochodów pobrano z BlenderKit (licencja Royalty-free, plan Free). Oświetlenie otoczenia zrealizowano przez teksturę i model chmur pobranych z BlenderKit (licencja Royalty-free, plan Free). Tekstura mokrego asfaltu wygenerowana proceduralnie przez skrypt Python.

Projekt podzielono na osobne skrypty odpowiadające kolejnym elementom sceny: droga, miasto, kamera, obiekty uliczne (latarnie, ławki). Każdy skrypt posiada sekcję parametrów na początku pliku.

## Render wynikowy

Render animacji zapisano w pliku `render.mp4` (250 klatek, 25 fps, Cycles).

## Opis skryptu `03_kamera.py`

Skrypt generuje animację kamery POV symulującą chód człowieka.

Parametry sterujące na początku pliku:

| Parametr | Opis | Domyślnie |
|---|---|---|
| `PREDKOSC_KROKU` | Częstotliwość cyklu kroku | `0.18` |
| `WYSOKOSC_KROKU` | Amplituda pionowego uderzenia stopy | `0.2` |
| `SZEROKOSC_KOLYSANIA` | Amplituda bocznego kołysania bioder | `0.04` |
| `SILA_DRGAN` | Siła organicznego szumu kamery | `0.14` |
| `DRGANIE_ROTACJI` | Amplituda losowego drżenia obrotu | `0.004` |
| `WYSOKOSC_ODDECHU` | Amplituda unoszenia od oddechu | `0.09` |
| `PREDKOSC_ODDECHU` | Częstotliwość cyklu oddechu | `0.025` |

Kamera przesuwa się z `POZYCJA_START` do `POZYCJA_KONIEC` z wygładzeniem (`smooth step`). Na każdej klatce wstawiane są keyframe'y dla `location`, `rotation_euler` i `lens`. Interpolacja krzywych ustawiana jest na `LINEAR` przez iterację po `action.layers`.

## Assety zewnętrzne

| Asset | Źródło | Licencja |
|---|---|---|
| [Asset 1](https://www.blenderkit.com/asset-gallery-detail/be6a33b9-158a-4a7c-baa9-835514c4c672) | BlenderKit | Royalty-free |
| [Asset 2](https://www.blenderkit.com/asset-gallery-detail/f770f579-098a-4732-b635-9eb74002399d) | BlenderKit | Royalty-free |
| [Asset 3](https://www.blenderkit.com/asset-gallery-detail/6178cb81-126a-461f-9be8-581a6b997488) | BlenderKit | Royalty-free |
| [Asset 4](https://www.blenderkit.com/asset-gallery-detail/0c61dada-698b-44aa-8594-d6c8b3e314df) | BlenderKit | Royalty-free |
| [Asset 5](https://www.blenderkit.com/asset-gallery-detail/2c90272b-9e8b-4dcf-8473-7e4694efa546) | BlenderKit | Royalty-free |
| [Asset 6](https://www.blenderkit.com/asset-gallery-detail/214a94ee-1d4a-4039-8e42-b5ec3368abee) | BlenderKit | Royalty-free |
| [Asset 7](https://www.blenderkit.com/asset-gallery-detail/ef8c611f-d74a-437b-bf32-30182c0d8dbc) | BlenderKit | Royalty-free |

## Uruchomienie i renderowanie

1. Uruchom Blender 4.x
2. Otwórz `Projekt.blend`
4. Render → Render Animation (`Ctrl+F12`)
