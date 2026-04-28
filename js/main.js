/* ============================================================
   PRACTICAL AI CO. — IMMERSIVE BACKGROUND
   Layers:
   1. Deep gradient background with glow blobs
   2. Neural node network with connecting lines
   3. Pulsing neural connection flashes
   4. Shooting star light streaks
============================================================ */

const canvas = document.getElementById('bgCanvas');
const ctx    = canvas.getContext('2d');
let W, H, nodes = [], stars = [], pulses = [];
const mouse = { x: -999, y: -999 };

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', () => { resize(); initNodes(); }, { passive: true });
window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });

/* ===================== BACKGROUND ===================== */
function drawBackground() {
  ctx.fillStyle = '#060d1a';
  ctx.fillRect(0, 0, W, H);

  const blobs = [
    { x: W * 0.75, y: H * 0.18, r: Math.max(W,H)*0.5,  c: 'rgba(14,165,233,0.07)' },
    { x: W * 0.12, y: H * 0.72, r: Math.max(W,H)*0.42, c: 'rgba(20,184,166,0.06)' },
    { x: W * 0.5,  y: H * 0.45, r: Math.max(W,H)*0.32, c: 'rgba(249,115,22,0.03)' },
  ];
  blobs.forEach(b => {
    const g = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
    g.addColorStop(0, b.c);
    g.addColorStop(1, 'transparent');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  });
}

/* ===================== NODES ===================== */
class Node {
  constructor(init) {
    this.reset(init);
  }
  reset(init) {
    this.x  = Math.random() * W;
    this.y  = init ? Math.random() * H : (Math.random() > 0.5 ? -10 : H + 10);
    this.vx = (Math.random() - 0.5) * 0.35;
    this.vy = (Math.random() - 0.5) * 0.35;
    this.r  = Math.random() * 2 + 0.6;
    this.baseOpacity = Math.random() * 0.55 + 0.15;
    this.opacity = this.baseOpacity;
    this.pulse = Math.random() * Math.PI * 2;
    this.pulseSpeed = 0.01 + Math.random() * 0.02;
    this.color = Math.random() > 0.55 ? '20,184,166' : Math.random() > 0.4 ? '14,165,233' : '249,115,22';
  }
  update() {
    this.pulse += this.pulseSpeed;
    this.opacity = this.baseOpacity + Math.sin(this.pulse) * 0.2;

    // Mouse repulsion
    const dx = this.x - mouse.x, dy = this.y - mouse.y;
    const d  = Math.sqrt(dx*dx + dy*dy);
    if (d < 130) { this.vx += (dx/d)*0.02; this.vy += (dy/d)*0.02; }

    this.vx *= 0.992; this.vy *= 0.992;
    this.x += this.vx; this.y += this.vy;

    if (this.x < -20 || this.x > W+20 || this.y < -20 || this.y > H+20) this.reset(false);
  }
  draw() {
    // Outer glow
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 5);
    g.addColorStop(0, `rgba(${this.color},${this.opacity * 0.6})`);
    g.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r * 5, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();
    // Core
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${this.color},${Math.min(1, this.opacity + 0.25)})`;
    ctx.fill();
  }
}

function drawConnections() {
  const MAX = 155;
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const d  = Math.sqrt(dx*dx + dy*dy);
      if (d < MAX) {
        const a = 0.18 * (1 - d / MAX);
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.strokeStyle = `rgba(14,165,233,${a})`;
        ctx.lineWidth = 0.7 * (1 - d/MAX);
        ctx.stroke();
      }
    }
  }
}

function initNodes() {
  const count = Math.min(160, Math.floor((W * H) / 7500));
  nodes = Array.from({ length: count }, () => new Node(true));
}
initNodes();

/* ===================== NEURAL PULSE FLASHES ===================== */
// A pulse travels along a connection between two random nodes
class NeuralPulse {
  constructor() {
    this.reset();
  }
  reset() {
    if (nodes.length < 2) return;
    // Pick two nearby nodes
    let attempts = 0;
    do {
      this.a = nodes[Math.floor(Math.random() * nodes.length)];
      this.b = nodes[Math.floor(Math.random() * nodes.length)];
      const dx = this.a.x - this.b.x, dy = this.a.y - this.b.y;
      this.dist = Math.sqrt(dx*dx + dy*dy);
      attempts++;
    } while ((this.dist > 200 || this.dist < 30) && attempts < 30);

    this.t       = 0;          // 0→1 travel progress
    this.speed   = 0.008 + Math.random() * 0.012;
    this.width   = 1.5 + Math.random() * 2;
    this.alive   = true;
    this.color   = Math.random() > 0.4 ? '20,184,166' : Math.random() > 0.5 ? '14,165,233' : '249,115,22';
    this.opacity = 0.7 + Math.random() * 0.3;
  }
  update() {
    this.t += this.speed;
    if (this.t >= 1) { this.alive = false; }
  }
  draw() {
    const x = this.a.x + (this.b.x - this.a.x) * this.t;
    const y = this.a.y + (this.b.y - this.a.y) * this.t;
    const fade = Math.sin(this.t * Math.PI); // fade in and out

    // Trail
    const trail = 0.12;
    const tx = this.a.x + (this.b.x - this.a.x) * Math.max(0, this.t - trail);
    const ty = this.a.y + (this.b.y - this.a.y) * Math.max(0, this.t - trail);

    const grad = ctx.createLinearGradient(tx, ty, x, y);
    grad.addColorStop(0, `rgba(${this.color},0)`);
    grad.addColorStop(1, `rgba(${this.color},${this.opacity * fade})`);

    ctx.beginPath();
    ctx.moveTo(tx, ty);
    ctx.lineTo(x, y);
    ctx.strokeStyle = grad;
    ctx.lineWidth = this.width;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Bright head dot
    ctx.beginPath();
    ctx.arc(x, y, this.width * 1.4, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${this.color},${this.opacity * fade})`;
    ctx.fill();

    // Glow around head
    const g2 = ctx.createRadialGradient(x, y, 0, x, y, 12);
    g2.addColorStop(0, `rgba(${this.color},${0.3 * fade})`);
    g2.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(x, y, 12, 0, Math.PI * 2);
    ctx.fillStyle = g2;
    ctx.fill();
  }
}

/* ===================== SHOOTING STARS ===================== */
class ShootingStar {
  constructor() {
    this.reset();
  }
  reset() {
    // Start from random edge or top
    const side = Math.random();
    if (side < 0.7) {
      // from top
      this.x = Math.random() * W;
      this.y = -10;
    } else if (side < 0.85) {
      // from left
      this.x = -10;
      this.y = Math.random() * H * 0.6;
    } else {
      // from right
      this.x = W + 10;
      this.y = Math.random() * H * 0.6;
    }

    // Direction — mostly diagonal downward
    const angle = (Math.PI * 0.25) + (Math.random() * Math.PI * 0.5);
    const speed = 4 + Math.random() * 8;
    this.vx = Math.cos(angle) * speed * (this.x > W/2 ? -1 : 1);
    this.vy = Math.sin(angle) * speed;

    this.len    = 80 + Math.random() * 200;  // trail length
    this.width  = 0.8 + Math.random() * 1.8;
    this.alive  = true;
    this.opacity = 0.6 + Math.random() * 0.4;
    this.color  = Math.random() > 0.5 ? '255,255,255' : Math.random() > 0.5 ? '20,184,166' : '14,165,233';
    this.life   = 0;
    this.maxLife = 60 + Math.random() * 80; // frames
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.life++;
    if (this.life > this.maxLife || this.x < -200 || this.x > W+200 || this.y > H+200) {
      this.alive = false;
    }
  }
  draw() {
    const fade = Math.sin((this.life / this.maxLife) * Math.PI);
    const tx = this.x - (this.vx / Math.sqrt(this.vx*this.vx+this.vy*this.vy)) * this.len;
    const ty = this.y - (this.vy / Math.sqrt(this.vx*this.vx+this.vy*this.vy)) * this.len;

    const grad = ctx.createLinearGradient(tx, ty, this.x, this.y);
    grad.addColorStop(0, 'transparent');
    grad.addColorStop(0.6, `rgba(${this.color},${this.opacity * fade * 0.3})`);
    grad.addColorStop(1, `rgba(${this.color},${this.opacity * fade})`);

    ctx.beginPath();
    ctx.moveTo(tx, ty);
    ctx.lineTo(this.x, this.y);
    ctx.strokeStyle = grad;
    ctx.lineWidth = this.width;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Bright tip
    const tipGlow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, 8);
    tipGlow.addColorStop(0, `rgba(${this.color},${0.8 * fade})`);
    tipGlow.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(this.x, this.y, 8, 0, Math.PI * 2);
    ctx.fillStyle = tipGlow;
    ctx.fill();
  }
}

/* ===================== SPAWN TIMERS ===================== */
let pulseTimer = 0;
let starTimer  = 0;

/* ===================== MAIN LOOP ===================== */
function animate() {
  drawBackground();

  // Connections first (behind nodes)
  drawConnections();

  // Nodes
  nodes.forEach(n => { n.update(); n.draw(); });

  // Neural pulses
  pulseTimer++;
  if (pulseTimer > 18) {
    pulseTimer = 0;
    if (pulses.length < 25) pulses.push(new NeuralPulse());
  }
  pulses = pulses.filter(p => p.alive);
  pulses.forEach(p => { p.update(); p.draw(); });

  // Shooting stars
  starTimer++;
  if (starTimer > 45 + Math.random() * 60) {
    starTimer = 0;
    if (stars.length < 6) stars.push(new ShootingStar());
  }
  stars = stars.filter(s => s.alive);
  stars.forEach(s => { s.update(); s.draw(); });

  requestAnimationFrame(animate);
}
animate();

/* ===================== NAV ===================== */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

/* ===================== MOBILE NAV ===================== */
document.getElementById('navToggle').addEventListener('click', () => {
  document.getElementById('navLinks').classList.toggle('open');
});
document.querySelectorAll('#navLinks a').forEach(a => {
  a.addEventListener('click', () => document.getElementById('navLinks').classList.remove('open'));
});

/* ===================== SCROLL REVEAL ===================== */
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) setTimeout(() => e.target.classList.add('visible'), i * 80);
  });
}, { threshold: 0.06, rootMargin: '0px 0px -30px 0px' });
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

/* ===================== POPUP FREQUENCY GUARD ===================== */
// MailerLite popup has two triggers: timeout (5s) + exit-intent.
// Both can fire in the same session, causing the "keeps repeating" issue.
// This ensures the popup shows maximum once per browser session.
(function () {
  var POPUP_CLASS = 'ml-subscribe-form-185522879970936427';
  var KEY = 'ml_popup_shown';

  function suppress() {
    var el = document.querySelector('.' + POPUP_CLASS);
    if (el) {
      var wrap = el.closest('[id^="mlb2-"]') || el.parentElement;
      if (wrap) wrap.style.display = 'none';
    }
  }

  if (sessionStorage.getItem(KEY)) {
    // Already shown this session — suppress any future appearances immediately
    var obs = new MutationObserver(suppress);
    obs.observe(document.body, { childList: true, subtree: true });
  } else {
    // Watch for first appearance, then lock it out for the rest of the session
    var obs2 = new MutationObserver(function () {
      var el = document.querySelector('.' + POPUP_CLASS);
      if (el) {
        sessionStorage.setItem(KEY, '1');
        obs2.disconnect();
        var obs3 = new MutationObserver(suppress);
        obs3.observe(document.body, { childList: true, subtree: true });
      }
    });
    obs2.observe(document.body, { childList: true, subtree: true });
  }
})();
