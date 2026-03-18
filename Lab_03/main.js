// Klasa reprezentująca pojedynczą cząstkę wybuchu
class Particle {
  constructor() {
    this.active = false;
  }

  // Inicjalizuje cząstkę z podanymi parametrami
  reset(x, y, vx, vy, hue) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.hue = hue;
    this.alpha = 1;
    this.decay = 0.012 + Math.random() * 0.008;
    this.size = 2 + Math.random() * 2;
    this.active = true;
  }

  // Aktualizuje stan cząstki: ruch, grawitacja, opór, zanikanie i kolizja z ziemią
  update(gravity, canvasHeight) {
    this._applyMovement();
    this._applyGravity(gravity);
    this._applyDrag();
    this._applyFade();
    this._checkGround(canvasHeight);
  }
  // Zmienia pozycję cząstki na podstawie jej prędkości
  _applyMovement() {
    this.x += this.vx;
    this.y += this.vy;
  }
  // Dodaje grawitację do prędkości pionowej cząstki
  _applyGravity(g) {
    this.vy += g;
  }
  // Zmniejsza prędkość cząstki, symulując opór powietrza
  _applyDrag() {
    this.vx *= 0.98;
    this.vy *= 0.98;
  }
  // Zmniejsza przezroczystość cząstki, aż stanie się niewidoczna
  _applyFade() {
    this.alpha -= this.decay;
    if (this.alpha <= 0) this.active = false;
  }
  // Odbija cząstkę od "ziemi" i zmniejsza jej prędkość pionową
  _checkGround(h) {
    if (this.y >= h) {
      this.vy *= -0.6;
      this.y = h;
    }
  }
  // Rysuje cząstkę na kanwie z odpowiednim kolorem i przezroczystością
  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${this.hue}, 100%, 60%, ${this.alpha})`;
    ctx.fill();
  }
}
// Klasa reprezentująca pojedynczy fajerwerk, który leci do celu, a następnie eksploduje na cząstki
class Firework {
  constructor(startX, startY, targetX, targetY, particleCount) {
    this.x = startX;
    this.y = startY;
    this.targetX = targetX;
    this.targetY = targetY;
    this.particleCount = particleCount;

    this.hue = Math.random() * 360;

    this.active = true;
    this.exploded = false;
    this.explodedHandled = false;

    this._calcVelocity(8);
  }
  // Oblicza prędkość rakiety, aby leciała w kierunku celu z określoną prędkością
  _calcVelocity(speed) {
    const dx = this.targetX - this.x;
    const dy = this.targetY - this.y;
    const dist = Math.hypot(dx, dy) || 1;
    this.vx = (dx / dist) * speed;
    this.vy = (dy / dist) * speed;
  }
  // Aktualizuje pozycję rakiety i sprawdza, czy osiągnęła cel, aby rozpocząć eksplozję
  update() {
    if (this.exploded) return;

    this.x += this.vx;
    this.y += this.vy;

    if (Math.hypot(this.targetX - this.x, this.targetY - this.y) < 5) {
      this.exploded = true;
      this.active = false;
    }
  }
  // Rysuje rakietę jako mały punkt na kanwie
  draw(ctx) {
    if (this.exploded) return;

    ctx.beginPath();
    ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${this.hue}, 100%, 80%, 1)`;
    ctx.fill();
  }
  // Tworzy cząstki eksplozji rakiety bez użycia puli, generując nowe obiekty Particle
  explode() {
    const particles = [];
    for (let i = 0; i < this.particleCount; i++) {
      particles.push(this._createParticle());
    }
    return particles;
  }
  // Tworzy cząstki eksplozji rakiety, wykorzystując pulę obiektów Particle, aby uniknąć tworzenia nowych instancji
  explodeFromPool(pool) {
    const particles = [];
    for (let i = 0; i < this.particleCount; i++) {
      const p = pool.acquire();
      this._initParticle(p);
      particles.push(p);
    }
    return particles;
  }
  // Inicjalizuje cząstkę z losowym kierunkiem, prędkością i odcieniem koloru na podstawie koloru rakiety
  _createParticle() {
    const p = new Particle();
    this._initParticle(p);
    return p;
  }
  // Ustawia parametry cząstki, takie jak pozycja, prędkość i kolor, na podstawie rakiety
  _initParticle(p) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 1 + Math.random() * 6;
    const hueVar = this.hue + (Math.random() - 0.5) * 40;
    p.reset(
      this.x,
      this.y,
      Math.cos(angle) * speed,
      Math.sin(angle) * speed,
      hueVar,
    );
  }
}
// Klasa zarządzająca pulą obiektów Particle, umożliwiająca ponowne wykorzystanie cząstek zamiast tworzenia nowych instancji
class ParticlePool {
  constructor(size) {
    this.pool = Array.from({ length: size }, () => new Particle());
    this.index = 0;
  }
  // Zwraca aktywną cząstkę z puli i przygotowuje ją do ponownego użycia
  acquire() {
    const p = this.pool[this.index];
    this.index = (this.index + 1) % this.pool.length;
    return p;
  }
  // Zwraca listę aktywnych cząstek z puli, które są aktualnie używane w eksplozjach
  getActive() {
    return this.pool.filter((p) => p.active);
  }
}
// Główna klasa zarządzająca pokazem fajerwerków, obsługująca logikę rakiet, cząstek, interakcje użytkownika i renderowanie
class FireworkShow {
  constructor() {
    this.canvas = document.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");

    this.gravity = 0.15;
    this.particleCount = 120;
    this.usePooling = false;

    this.rockets = [];
    this.particles = [];

    this.pool = new ParticlePool(4000); // Tworzy pulę 4000 cząstek do ponownego wykorzystania

    this.fps = 0;
    this.lastTime = performance.now();
    this.frameCount = 0;

    this._setupCanvas();
    this._setupEvents();
    this._fireRandomRocket();
    this._setupUI();
    this._loop();
  }
  // Ustawia rozmiar kanwy na pełny ekran i dodaje nasłuchiwanie zdarzenia resize, aby dostosować rozmiar przy zmianie okna
  _setupCanvas() {
    const resize = () => {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);
  }
  // Dodaje nasłuchiwanie zdarzenia kliknięcia na kanwie, aby wystrzelić rakietę w kierunku kliknięcia i ukryć wskazówkę dla użytkownika
  _setupEvents() {
    this.canvas.addEventListener("click", (e) => {
      const startX = this.canvas.width / 2;
      const startY = this.canvas.height;
      this.rockets.push(
        new Firework(startX, startY, e.clientX, e.clientY, this.particleCount),
      );

      document.getElementById("hint").style.opacity = "0";
    });
  }
  // Losowo wystrzeliwuje rakietę w losowym miejscu na dole ekranu, lecącą do losowego celu w górnej części ekranu, z losowym opóźnieniem między kolejnymi rakietami
  _fireRandomRocket() {
    const startX = this.randomRange(
      this.canvas.width * 0.2,
      this.canvas.width * 0.8,
    );
    const startY = this.canvas.height;

    const targetX = this.randomRange(
      this.canvas.width * 0.1,
      this.canvas.width * 0.9,
    );
    const targetY = this.randomRange(
      this.canvas.height * 0.1,
      this.canvas.height * 0.2,
    );

    const delayMs = this.randomRange(500, 2500);

    setTimeout(() => {
      this.rockets.push(
        new Firework(startX, startY, targetX, targetY, this.particleCount),
      );

      this._fireRandomRocket();
    }, delayMs);
  }
  // Generuje losową liczbę z zakresu od min do max
  randomRange(min, max) {
    return Math.random() * (max - min) + min;
  }
  // Ustawia interfejs użytkownika, dodając nasłuchiwanie zdarzeń do suwaków i przycisku, aby kontrolować liczbę cząstek, grawitację i tryb działania (pooling vs standard)
  _setupUI() {
    const countSlider = document.getElementById("countSlider");
    const countVal = document.getElementById("countVal");
    countSlider.addEventListener("input", () => {
      this.particleCount = parseInt(countSlider.value);
      countVal.textContent = countSlider.value;
    });

    const gravSlider = document.getElementById("gravSlider");
    const gravVal = document.getElementById("gravVal");
    gravSlider.addEventListener("input", () => {
      this.gravity = parseInt(gravSlider.value) / 100;
      gravVal.textContent = this.gravity.toFixed(2);
    });

    const btn = document.getElementById("poolToggle");
    btn.addEventListener("click", () => {
      this.usePooling = !this.usePooling;
      btn.textContent = `Pooling: ${this.usePooling ? "ON" : "OFF"}`;
      btn.classList.toggle("active", this.usePooling);

      this.particles = [];
    });
  }
  // Główna pętla animacji, która aktualizuje FPS, czyści kanwę, aktualizuje rakiety i cząstki, a także aktualizuje statystyki wyświetlane na ekranie
  _loop() {
    this._updateFPS();
    this._clearCanvas();
    this._updateRockets();
    this._updateParticles();
    this._updateStats();
    requestAnimationFrame(() => this._loop());
  }
  // Aktualizuje licznik FPS, obliczając liczbę klatek na sekundę na podstawie czasu, który upłynął od ostatniej aktualizacji
  _updateFPS() {
    this.frameCount++;
    const now = performance.now();
    if (now - this.lastTime >= 1000) {
      this.fps = this.frameCount;
      this.frameCount = 0;
      this.lastTime = now;
    }
  }
  // Czyści kanwę, rysując półprzezroczysty czarny prostokąt, który tworzy efekt zanikania śladów rakiet i cząstek
  _clearCanvas() {
    this.ctx.globalCompositeOperation = "source-over";
    this.ctx.fillStyle = "rgba(0, 0, 0, 0.15)";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }
  // Aktualizuje i rysuje wszystkie aktywne rakiety, a także obsługuje eksplozję rakiet, tworząc nowe cząstki lub wykorzystując pulę cząstek w zależności od ustawień
  _updateRockets() {
    this.ctx.globalCompositeOperation = "lighter";

    for (const rocket of this.rockets) {
      rocket.update();
      rocket.draw(this.ctx);

      if (rocket.exploded && !rocket.explodedHandled) {
        rocket.explodedHandled = true;
        const newParticles = this.usePooling
          ? rocket.explodeFromPool(this.pool)
          : rocket.explode();

        if (!this.usePooling) {
          this.particles.push(...newParticles);
        }
      }
    }

    this.rockets = this.rockets.filter((r) => r.active);
  }
  // Aktualizuje i rysuje wszystkie aktywne cząstki, a także usuwa nieaktywne cząstki z listy, jeśli nie jest używana pula
  _updateParticles() {
    this.ctx.globalCompositeOperation = "lighter";

    const activeParticles = this.usePooling
      ? this.pool.getActive()
      : this.particles;

    for (const p of activeParticles) {
      p.update(this.gravity, this.canvas.height);
      p.draw(this.ctx);
    }

    if (!this.usePooling) {
      this.particles = this.particles.filter((p) => p.active);
    }

    this.ctx.globalCompositeOperation = "source-over";
  }
  // Aktualizuje statystyki wyświetlane na ekranie, takie jak FPS, liczba rakiet, liczba aktywnych cząstek i aktualny tryb działania (pooling vs standard)
  _updateStats() {
    const activeCount = this.usePooling
      ? this.pool.getActive().length
      : this.particles.length;

    document.getElementById("fpsVal").textContent = this.fps;
    document.getElementById("rocketVal").textContent = this.rockets.length;
    document.getElementById("particleVal").textContent = activeCount;
    document.getElementById("modeVal").textContent = this.usePooling
      ? "Pooling"
      : "Standard";
  }
}
// Inicjalizuje pokaz fajerwerków po załadowaniu strony, tworząc nową instancję klasy FireworkShow
window.addEventListener("load", () => new FireworkShow());
