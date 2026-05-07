# Lab 10 - Rigging Biomechanicznego Stworzenia (Armature, IK, Animacja Chodu)

## Co zostało zrealizowane

Wykonano model pająka w formie Low Poly z 4 parami odnóży. Do pająka dodano tekstury oraz Armature. W Armature utworzono dla każdego odnóża IK, dodano odpowiednie blokady rotacji do kości. Utworzono dwie grupy IK *A* i *B*, w których podpięto odpowiednie odnóża, tworząc narzędzie do szybkiej animacji chodu.

Końcowo utworzono animację chodu zgodną z instrukcją, wykorzystując wcześniej utworzone punkty IK i szkielet. Animacja objęła odnóża, głowę oraz odwłok pająka. Utworzono bardzo prostą scenę składającą się z płaskiej, teksturowanej powierzchni oraz światła typu *sun*.

## Render wynikowy

Render wynikowy zapisano w pliku `.mp4`.

## Co można poprawić

Rigging postaci nie jest najlepiej wykonany — lepsze efekty można by uzyskać stosując lepszą maskę wagi, lepiej rozmieszczając kości i poprawiając ich orientację (główny problem wynikał z sytuacji, gdy próbowałem ograniczyć rotację w X dla korpusu — pająk zaczął się niekontrolowanie obracać mimo blokady 0–0). Poprawić można by również sposób grupowania IK: zamiast tworzyć dwie nowe kości IK *grupaA*, *grupaB*, można by to wykonać w bardziej zaawansowany sposób.

Można również poprawić całość animacji, czyniąc ją płynniejszą i bardziej naturalną, co wymaga zapoznania się z wzorcem poruszania się pająków w biologii.
