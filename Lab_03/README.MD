## Pokaz Fajerwerków

![Zdjęcie przedstawiające działający pokaz fajerwerków](./Zrzut%20ekranu_20260312_092237.png)

## Opis

Pokaz fajerwerków rysowany jest przy użyciu kontekstu `2D canvasu`. Rakiety wylatują z dołu ekranu i lecą w kierunku celu, gdzie eksplodują na dziesiątki kolorowych cząstek. Cząstki podlegają grawitacji i oporowi powietrza, stopniowo zanikając. Efekt smugi uzyskiwany jest poprzez rysowanie półprzezroczystego tła zamiast czyszczenia klatki. Animacja działa w pętli przy użyciu `requestAnimationFrame`, a interfejs pozwala kontrolować liczbę cząstek, grawitację i tryb zarządzania pamięcią.

### Klasa Particle

Reprezentuje pojedynczą cząstkę eksplozji.

*Właściwości*:
- `x, y` – pozycja cząstki na kanwie.
- `vx, vy` – składowe prędkości.
- `hue` – odcień koloru w modelu HSL.
- `alpha` – przezroczystość (od 1 do 0).
- `decay` – szybkość zanikania.
- `size` – promień cząstki.
- `active` – flaga określająca, czy cząstka jest aktywna.

*Metody*:
- `reset(x, y, vx, vy, hue)` — inicjalizuje cząstkę z podanymi parametrami.
- `update(gravity, canvasHeight)` — aktualizuje pozycję, prędkość, zanikanie i kolizję z ziemią.
- `draw(ctx)` — rysuje cząstkę na kanwie z odpowiednim kolorem i przezroczystością.

### Klasa Firework

Reprezentuje pojedynczą rakietę, która leci do celu i eksploduje.

*Właściwości*:
- `x, y` – aktualna pozycja rakiety.
- `targetX, targetY` – cel lotu.
- `hue` – kolor rakiety i jej eksplozji.
- `active` – czy rakieta jest jeszcze w locie.
- `exploded, explodedHandled` – flagi zarządzające momentem eksplozji.

*Metody*:
- `update()` — przesuwa rakietę w kierunku celu i wykrywa dotarcie do niego.
- `draw(ctx)` — rysuje rakietę jako mały punkt świetlny.
- `explode()` — tworzy cząstki eksplozji bez użycia puli obiektów.
- `explodeFromPool(pool)` — tworzy cząstki eksplozji z puli obiektów `ParticlePool`.

### Klasa ParticlePool

Zarządza pulą obiektów `Particle`, umożliwiając ich ponowne wykorzystanie zamiast ciągłego tworzenia nowych instancji.

*Właściwości*:
- `pool` – tablica prealokowanych cząstek.
- `index` – wskaźnik na kolejną cząstkę do pobrania (cykliczny).

*Metody*:
- `acquire()` — zwraca kolejną cząstkę z puli (nadpisując ją przy potrzebie).
- `getActive()` — zwraca listę aktualnie aktywnych cząstek.

### Klasa FireworkShow

Główna klasa zarządzająca całym pokazem: rakietami, cząstkami, interfejsem i renderowaniem.

*Właściwości*:
- `canvas, ctx` – odniesienia do elementu canvas i kontekstu 2D.
- `gravity` – siła grawitacji działająca na cząstki.
- `particleCount` – liczba cząstek generowanych przez każdą eksplozję.
- `usePooling` – flaga trybu zarządzania pamięcią (pula vs. standardowy).
- `rockets` – lista aktywnych rakiet.
- `particles` – lista aktywnych cząstek (w trybie standardowym).
- `pool` – instancja `ParticlePool` (w trybie poolingu).
- `fps` – aktualny licznik klatek na sekundę.

*Metody*:
- `_setupCanvas()` — ustawia rozmiar kanwy na pełny ekran i reaguje na zmianę rozmiaru okna.
- `_setupEvents()` — obsługuje kliknięcie na kanwę, wystrzeliwując rakietę w klikane miejsce.
- `_fireRandomRocket()` — cyklicznie wystrzeliwuje rakiety w losowe miejsca z losowym opóźnieniem.
- `_setupUI()` — podłącza suwaki i przycisk do kontroli parametrów pokazu.
- `_loop()` — główna pętla animacji: aktualizuje FPS, czyści kanwę, przetwarza rakiety i cząstki.
- `_clearCanvas()` — rysuje półprzezroczysty czarny prostokąt, tworząc efekt zanikających smug.
- `_updateRockets()` — aktualizuje i rysuje rakiety, obsługuje eksplozje.
- `_updateParticles()` — aktualizuje i rysuje aktywne cząstki, usuwa nieaktywne.
- `_updateStats()` — odświeża statystyki FPS, liczby rakiet, cząstek i aktywnego trybu.

## Logika działania

1. Po załadowaniu strony tworzony jest obiekt `FireworkShow`.
2. Co losowy czas (0,5–2,5 s) wystrzeliwana jest kolejna rakieta w losowe miejsce w górnej części ekranu.
3. Użytkownik może kliknąć na ekran, aby wystrzelić rakietę dokładnie w wybrane miejsce.
4. Rakieta leci w kierunku celu ze stałą prędkością. Po dotarciu do niego eksploduje na `particleCount` cząstek.
5. Każda cząstka ma losowy kierunek, prędkość i odcień koloru zbliżony do koloru rakiety.
6. W każdej klatce animacji:
   - rysowany jest półprzezroczysty czarny prostokąt (efekt smug),
   - rakiety są przesuwane i sprawdzane pod kątem eksplozji,
   - cząstki są aktualizowane (grawitacja, opór, zanikanie, odbicie od ziemi) i rysowane,
   - odświeżane są statystyki na ekranie.
7. Tryb **poolingu** pozwala wielokrotnie wykorzystywać pulę 4000 prealokowanych cząstek, unikając presji na garbage collector — przydatne przy dużej liczbie eksplozji.