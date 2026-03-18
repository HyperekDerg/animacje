// Skrypt odpowiedzialny za rysowanie zegara i jego animację

// Klasa reprezentująca wskazówkę zegara
class Hand {
  constructor(color, length, width, isSecondHand = false) {
    // Konstruktor przyjmujący kolor, długość, szerokość i informację czy to wskazówka sekundowa
    this.color = color;
    this.length = length;
    this.width = width;
    this.isSecondHand = isSecondHand;
  }

  draw(ctx, angle, radius, isTrail = false) {
    // Metoda rysująca wskazówkę na podstawie kąta, promienia i informacji czy ma być rysowany ślad
    ctx.save();
    ctx.rotate(angle);

    ctx.beginPath();
    ctx.lineWidth = this.width;
    ctx.lineCap = "round";

    if (this.isSecondHand) {
      // Jeśli to wskazówka sekundowa, rysujemy ją z efektem śladu
      const startY = isTrail ? -radius * 0.7 : radius * 0.2; // Ustalanie punktu początkowego wskazówki w zależności od tego, czy rysujemy ślad
      ctx.strokeStyle = isTrail
        ? this.color.replace("1)", "0.15)")
        : this.color;

      // Dodanie efektu rozmycia dla śladu wskazówki sekundowej, aby uzyskać bardziej dynamiczny wygląd
      if (!isTrail) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = this.color;
      }

      ctx.moveTo(0, startY);
      ctx.lineTo(0, -radius * this.length);
    } else {
      // Dla wskazówek godzinowej i minutowej rysujemy je normalnie
      ctx.strokeStyle = this.color;
      ctx.moveTo(0, radius * 0.1);
      ctx.lineTo(0, -radius * this.length);
    }

    ctx.stroke();
    ctx.restore();
  }
}

// Klasa reprezentująca zegar, zarządzająca jego rysowaniem i animacją
class Clock {
  constructor(canvasId) {
    // Konstruktor przyjmujący ID elementu canvas, na którym będzie rysowany zegar
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.radius = this.canvas.width / 2; // Promień zegara, ustawiany na połowę szerokości canvasu
    this.isPaused = false;

    // Tablica przechowująca historię kątów wskazówki sekundowej, aby umożliwić rysowanie efektu śladu
    this.secondHistory = [];
    this.maxTrailSteps = 15;

    // Inicjalizacja wskazówek zegara z różnymi kolorami, długościami i szerokościami
    this.hourHand = new Hand("#ffffff", 0.5, 10);
    this.minuteHand = new Hand("#eeeeee", 0.8, 6);
    this.secondHand = new Hand("rgba(255, 59, 48, 1)", 0.92, 2, true);

    this.initListeners();
    this.animate();
  }

  // Metoda inicjalizująca nasłuchiwanie zdarzeń klawiatury, pozwalająca na pauzowanie i wznawianie animacji zegara za pomocą spacji
  initListeners() {
    window.addEventListener("keydown", (e) => {
      if (e.code === "Space") {
        this.isPaused = !this.isPaused;
        console.log(this.isPaused ? "Clock paused" : "Clock resumed"); // Logowanie stanu pauzy do konsoli dla łatwiejszego debugowania
      }
    });
  }

  // Metoda rysująca tarczę zegara, w tym obwód, indeksy godzinowe i minutowe
  drawFace() {
    const { ctx, radius } = this;
    ctx.save();
    ctx.translate(radius, radius);

    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.98, 0, Math.PI * 2);
    ctx.fillStyle = "#1a1a1a";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.92, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255, 59, 48, 0.3)";
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = "white";
    for (let i = 0; i < 60; i++) {
      ctx.save();
      ctx.rotate((i * Math.PI) / 30);
      const isHour = i % 5 === 0;
      ctx.beginPath();
      ctx.fillStyle = isHour ? "#fff" : "#666";
      ctx.rect(-1, -radius + 20, isHour ? 3 : 1, isHour ? 15 : 8);
      ctx.fill();
      ctx.restore();
    }
    ctx.restore();
  }

  // Metoda rysująca zegar, obliczająca aktualny czas i kąty wskazówek, a także zarządzająca historią kątów wskazówki sekundowej dla efektu śladu
  render() {
    if (this.isPaused) return; // Jeśli zegar jest w stanie pauzy, nie wykonujemy żadnych operacji rysowania

    const { ctx, radius, canvas } = this; // Skrócone odwołania do kontekstu, promienia i canvasu dla wygody
    const now = new Date(); // Pobieranie aktualnego czasu

    // Przypisanie wartości czasu do zmiennych, z uwzględnieniem milisekund dla płynniejszego ruchu wskazówki sekundowej
    const ms = now.getMilliseconds();
    const sec = now.getSeconds() + ms / 1000;
    const min = now.getMinutes() + sec / 60;
    const hr = (now.getHours() % 12) + min / 60;

    // Obliczanie kątów dla każdej z wskazówek na podstawie aktualnego czasu
    const secAngle = (sec / 60) * (2 * Math.PI);
    const minAngle = (min / 60) * (2 * Math.PI);
    const hrAngle = (hr / 12) * (2 * Math.PI);

    // Dodanie aktualnego kąta wskazówki sekundowej do historii, aby umożliwić rysowanie efektu śladu
    this.secondHistory.push(secAngle);
    if (this.secondHistory.length > this.maxTrailSteps) {
      this.secondHistory.shift();
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    this.drawFace();

    ctx.save();
    ctx.translate(radius, radius);

    // Rysowanie śladu wskazówki sekundowej, iterując po historii kątów i rysując je z odpowiednim efektem rozmycia
    this.secondHistory.forEach((angle, index) => {
      this.secondHand.draw(ctx, angle, radius, true);
    });

    // Rysowanie aktualnych pozycji wszystkich wskazówek
    this.hourHand.draw(ctx, hrAngle, radius);
    this.minuteHand.draw(ctx, minAngle, radius);
    this.secondHand.draw(ctx, secAngle, radius);

    ctx.beginPath();
    ctx.arc(0, 0, 6, 0, Math.PI * 2);
    ctx.fillStyle = "#fff";
    ctx.fill();

    ctx.restore();
  }

  // Metoda animująca zegar, wywołująca renderowanie i ponownie wywołująca siebie za pomocą requestAnimationFrame dla płynnej animacji
  animate() {
    this.render();
    requestAnimationFrame(() => this.animate());
  }
}

// Inicjalizacja zegara na stronie, tworząc nową instancję klasy Clock i przekazując ID elementu canvas, na którym będzie rysowany zegar
const myClock = new Clock("clockCanvas");
