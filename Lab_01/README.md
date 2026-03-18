## Zadanie A: Symulacja Rzutu Ukośnego


![Podgląd skryptów](https://github.com/HyperekDerg/Studia-Labolatoria-Specjalizacji/blob/main/SAK/LAB1/Zrzut%20ekranu%202026-02-24%20203033.png?raw=true)
Zadanie implementuje prosty silnik fizyczny obsługujący ruch pocisku, grawitację oraz odbicia od krawędzi sceny. Logika została podzielona na trzy główne procedury: **Ustaw Domyślne**, **Wystrzel pocisk** oraz **Aktualizuj fizykę**.

### Kluczowe elementy działania

#### **1. Wystrzał pocisku**

Po naciśnięciu klawisza **spacja** uruchamiana jest procedura `Wystrzel pocisk`. Na podstawie wartości suwaków obliczane są składowe prędkości początkowej:
- vx=siła⋅cos(kąt)
- vy=siła⋅sin(kąt)
Następnie pocisk zostaje ustawiony w pozycji startowej (x = –200, y = –150).

#### **2. Grawitacja**

Procedura `Aktualizuj fizykę` w każdej klatce zmniejsza pionową składową prędkości:
`g`(vy=vy−g)
Powoduje to naturalne opadanie pocisku zgodnie z przyjętą wartością grawitacji.

#### **3. Ruch i kolizje ze sceną**

Po aktualizacji prędkości obiekt przesuwa się o:
- `vx` w osi X
- `vy` w osi Y

Następnie sprawdzane są kolizje z granicami sceny:

- dolna krawędź: y < –170
- lewa krawędź: x < –220
- prawa krawędź: x > 230
- 
W przypadku zderzenia:

- pozycja jest korygowana do granicy,
- odpowiednia składowa prędkości zostaje odwrócona i pomnożona przez współczynnik `odbicie` (domyślnie **0.8**), co symuluje utratę energii przy odbiciu.
    

#### **4. Ustawienia początkowe**

Procedura `Ustaw Domyślne` resetuje wartości fizyczne:

- `vx = 0`
- `vy = 0`
- `odbicie = 0.8`
    

Wywoływana jest automatycznie po uruchomieniu projektu.

#### **5. Interfejs użytkownika**

Projekt wykorzystuje suwakowe zmienne Scratch, które pozwalają dynamicznie zmieniać parametry symulacji:

- **grawitacja (g)**
- **siła wystrzału**
- **kąt wystrzału**

## Zadanie B: Animacja Układu Słonecznego

Stworzono hierarchiczny model ruchu planetarnego oparty na współrzędnych biegunowych.

### Struktura obiektów:

1. **Słońce:** Punkt statyczny umieszczony w centrum sceny (współrzędne 0,0).
   
![Podgląd słońca](https://github.com/HyperekDerg/Studia-Labolatoria-Specjalizacji/blob/main/SAK/LAB1/Zrzut%20ekranu%202026-02-24%20203143.png?raw=true)

3. **Ziemia:** Krąży wokół Słońca w odległości **120 jednostek**. Jej pozycja jest aktualizowana w pętli:

![Podgląd ziemii](https://github.com/HyperekDerg/Studia-Labolatoria-Specjalizacji/blob/main/SAK/LAB1/Zrzut%20ekranu%202026-02-24%20203139%201.png?raw=true)

    - x_ziemia=120⋅cos(kąt ziemi)
    - y_ziemia=120⋅sin(kąt ziemi)
    - Kąt zwiększa się o **1 stopień** w każdej iteracji.
        
3. **Księżyc:** Wykorzystuje pozycję Ziemi jako punkt odniesienia, tworząc model hierarchiczny. Krąży w odległości **70 jednostek** od Ziemi:

![Podgląd księżyca](https://github.com/HyperekDerg/Studia-Labolatoria-Specjalizacji/blob/main/SAK/LAB1/Zrzut%20ekranu%202026-02-24%20203148.png?raw=true)

    - x=x_ziemia+70⋅cos(kąt księz˙yca)
    - y=y_ziemia+70⋅sin(kąt księz˙yca)
    - Kąt księżyca zmienia się szybciej (**4 stopnie** na krok), co odzwierciedla różnice w prędkościach orbitalnych.
