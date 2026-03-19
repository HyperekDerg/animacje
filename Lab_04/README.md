# Lab 04 – Proceduralna roślina biomechaniczna (bpy)

## Co zostało zrealizowane

Roślina generowana jest w całości kodem Pythona przez Blender API. Łodyga to mesh oparty na krzywej Béziera z losowym zagięciem - zwęża się ku górze i ma losowe węzły (wcięcia i garby) dla organicznego wyglądu.

Liście rozłożone są wzdłuż łodygi według kąta złotego (137.5°), każdy to spłaszczony, ostry kształt skalowany zależnie od wysokości na łodydze. Korzenie rozchodzą się od podstawy i zbiegają w czubku. Materiały w stylu biomechanicznym: metaliczna miedź na łodydze i korzeniach, świecąca zieleń lub cyan na liściach. Scena zawiera trzy rośliny różnej wielkości, render Eevee 800×600.

Zrealizowano zadania dodatkowe: rozmieszczenie korzeni i liści przy użyciu `math.sin()` / `math.cos()`.

[Roslina](./roslinabio.png)

## Trudności / refleksja

Generowanie korzeni i liści wymaga dopracowania — przy małej liczbie wyglądają sztucznie, przy dużej nachodzą na siebie. Przydałoby się scalanie wierzchołków leżących zbyt blisko siebie, co wyeliminowałoby artefakty cieniowania.
