## Zegar w HTML z ES6 JS

![Zdjęcie przedstawiające działający zegar](./Zrzut%20ekranu_20260303_152548.png)

## Opis

Zegar rysowany jest przy użyciu kontekstu `2D canvasu`. Skrypt oblicza aktualny czas z uwzględnieniem milisekund, co pozwala na płynny ruch wskazówek. Wskazówka sekundowa posiada dodatkowy efekt śladu, tworzony poprzez zapamiętywanie poprzednich kątów i rysowanie ich z malejącą przezroczystością. Tarcza zegara zawiera indeksy minutowe i godzinowe, a całość jest animowana za pomocą `requestAnimationFrame`.

### Klasa Hand

Reprezentuje pojedynczą wskazówkę zegara.

*Właściwości*:
- `color` - kolor wskazówki (również w formacie RGBA dla sekundnika).
- `length` - długość wskazówki względem promienia zegara.
- `width` - grubość linii.
- `isSecondHand` - flaga określająca, czy wskazówka jest sekundnikiem (umożliwia efekt śladu).

*Metoda*:
- draw(ctx, angle, radius, isTrail) — rysuje wskazówkę pod zadanym kątem. Dla sekundnika obsługuje efekt rozmytego śladu poprzez zmianę przezroczystości i cienia.

### Klasa Clock

Zarządza całym zegarem: rysowaniem tarczy, wskazówek, animacją i obsługą pauzy.

*Właściwości*:
- `canvas, ctx` - odniesienia do elementu canvas i kontekstu 2D.
- `radius` - promień zegara (połowa szerokości canvasu).
- `isPaused` - stan pauzy animacji.
- `secondHistory` - tablica przechowująca poprzednie kąty sekundnika, używana do efektu trail.
- `maxTrailSteps` — maksymalna liczba zapamiętanych pozycji sekundnika.

*Obiekty wskazówek*:
- hourHand
- minuteHand
- secondHand

*Metody*:
- initListeners() — obsługa klawisza spacja do pauzowania animacji.
- drawFace() — rysowanie tarczy zegara:
    - tło,
    - obwód,
    - indeksy minutowe i godzinowe.
- render() — oblicza aktualny czas, wyznacza kąty wskazówek, rysuje ślad sekundnika i aktualne pozycje wskazówek.
- animate() — pętla animacji oparta na requestAnimationFrame.

## Logika działania
1. Po załadowaniu strony tworzony jest obiekt Clock.
2. Zegar pobiera aktualny czas z uwzględnieniem milisekund, co zapewnia płynny ruch sekundnika.
3. Kąty wskazówek są obliczane proporcjonalnie:
    - `godziny`: hr / 12 * 2π,
    - `minuty`: min / 60 * 2π,
    - `sekundy`: sec / 60 * 2π.
4. Sekundnik zapisuje swoje poprzednie pozycje w secondHistory, co pozwala narysować efekt śladu.
5. Każda klatka animacji:
    - czyści canvas,
    - rysuje tarczę,
    - rysuje ślad sekundnika,
    - rysuje aktualne wskazówki,
    - rysuje środkowy punkt zegara.
6. Animacja działa w pętli do momentu wciśnięcia spacji.