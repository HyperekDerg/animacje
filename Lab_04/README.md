# Lab 05 – Generator Lasu z Typami Roślin i Biomami

## Co zostało zrealizowane

Zdefiniowano słownik TYPY_ROSLIN zawierający predefiniowane zakresy (wysokość, liczba liści, promień, kolory) dla trzech gatunków: Drzewo, Krzew oraz Paproć.

Parametry są losowane z zakresów przy użyciu random.uniform() i random.randint(), co zapewnia unikalność każdego obiektu.

Zaimplementowano funkcję wybierz_typ_biomu(x, z), która różnicuje roślinność w zależności od odległości od centrum pola:
- Centrum: Dominacja wysokich drzew.
- Półperyferia: Mieszanka drzew i krzewów (z przewagą krzewów – ok. 70%).
- Peryferia (Brzeg lasu): Niska roślinność – paprocie i pojedyncze krzewy.

Wszystkie wygenerowane obiekty są automatycznie grupowane w kolekcji Las.

Funkcja generuj_las() przyjmuje parametr seed, co pozwala na odtworzenie tego samego układu roślin przy tych samych ustawieniach.

Zachowano biomechaniczny styl (metaliczne łodygi, emisyjne liście).

Rozmieszczenie liści i korzeni oparte na funkcjach trygonometrycznych i złotym kącie.

Render wykonany w silniku Eevee w rozdzielczości 1200×800.


![las](https://raw.githubusercontent.com/HyperekDerg/animacje/main/Lab_05/las_05.png)

## Trudności / refleksja

Generowanie proceduralne nie zawsze idealnie generuje rośliny na powierzhni co jest spowodowane tym że generator według polecenia zadania przyjmuje wartości XY bez znajomości geometrii terenu. 
