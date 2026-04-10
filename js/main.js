/* ============================================================
   PRACTICAL AI CO. — MAIN JS
   Neural network background inspired by original site
============================================================ */

/* --- NEURAL NETWORK CANVAS --- */
const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d');
let W, H, nodes = [], mouse = { x: W/2, y: H/2 };

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', () => { resize(); initNodes(); });
window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });

class Node {
  constructor() { this.reset(true); }
  reset(init) {
    this.x  = Math.random() * W;
    this.y  = init ? Math.random() * H : -20;
    this.vx = (Math.random() - 0.5) * 0.4;
    this.vy = (Math.random() - 0.5) * 0.4;
    this.r  = Math.random() * 2.2 + 0.8;
    this.base = Math.random() * 0.6 + 0.2;
    this.opacity = this.base;
    this.color = Math.random() > 0.6 ? '20,184,166' : Math.random() > 0.5 ? '14,165,233' : '249,115,22';
    this.pulse = Math.random() * Math.PI * 2;
    this.pulseSpeed = 0.012 + Math.random() * 0.02;
  }
  update() {
    this.x += this.vx; this.y += this.vy;
    this.pulse += this.pulseSpeed;
    this.opacity = this.base + Math.sin(this.pulse) * 0.25;
    // Mouse repulsion — subtle
    const dx = this.x - mouse.x, dy = this.y - mouse.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist < 120) {
      this.vx += (dx / dist) * 0.015;
      this.vy += (dy / dist) * 0.015;
    }
    // Dampen velocity
    this.vx *= 0.99; this.vy *= 0.99;
    // Bounce off edges
    if (this.x < 0 || this.x > W) this.vx *= -1;
    if (this.y < 0 || this.y > H) this.vy *= -1;
    // Clamp
    this.x = Math.max(0, Math.min(W, this.x));
    this.y = Math.max(0, Math.min(H, this.y));
  }
  draw() {
    // Glow
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 4);
    g.addColorStop(0, `rgba(${this.color},${this.opacity})`);
    g.addColorStop(1, `rgba(${this.color},0)`);
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r * 4, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();
    // Core dot
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${this.color},${Math.min(1, this.opacity + 0.3)})`;
    ctx.fill();
  }
}

function drawConnections() {
  const maxDist = 160;
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < maxDist) {
        const alpha = 0.22 * (1 - dist / maxDist);
        // Color blend between the two nodes
        const c = nodes[i].color === '14,165,233' ? '14,165,233' : '20,184,166';
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.strokeStyle = `rgba(${c},${alpha})`;
        ctx.lineWidth = 0.8 * (1 - dist / maxDist);
        ctx.stroke();
      }
    }
  }
}

// Draw deep background gradient
function drawBackground() {
  // Base dark
  ctx.fillStyle = '#060d1a';
  ctx.fillRect(0, 0, W, H);
  // Radial glow blobs
  const blobs = [
    { x: W * 0.75, y: H * 0.2, r: Math.max(W,H) * 0.45, c: 'rgba(14,165,233,0.06)' },
    { x: W * 0.15, y: H * 0.7, r: Math.max(W,H) * 0.4,  c: 'rgba(20,184,166,0.05)' },
    { x: W * 0.5,  y: H * 0.5, r: Math.max(W,H) * 0.3,  c: 'rgba(249,115,22,0.025)' },
  ];
  blobs.forEach(b => {
    const g = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
    g.addColorStop(0, b.c);
    g.addColorStop(1, 'transparent');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  });
}

function initNodes() {
  const count = Math.min(180, Math.floor((W * H) / 7000));
  nodes = Array.from({ length: count }, () => new Node());
}
initNodes();

function animate() {
  drawBackground();
  drawConnections();
  nodes.forEach(n => { n.update(); n.draw(); });
  requestAnimationFrame(animate);
}
animate();

/* --- NAV SCROLL --- */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

/* --- MOBILE NAV --- */
document.getElementById('navToggle').addEventListener('click', () => {
  document.getElementById('navLinks').classList.toggle('open');
});
document.querySelectorAll('#navLinks a').forEach(a => {
  a.addEventListener('click', () => document.getElementById('navLinks').classList.remove('open'));
});

/* --- SCROLL REVEAL --- */
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
    }
  });
}, { threshold: 0.06, rootMargin: '0px 0px -30px 0px' });
document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

/* --- EMAIL FORM --- */
const emailForm = document.getElementById('emailForm');
if (emailForm) {
  emailForm.addEventListener('submit', e => {
    e.preventDefault();
    const btn = emailForm.querySelector('button');
    const orig = btn.textContent;
    btn.textContent = "✓ You're in!";
    btn.style.background = '#14B8A6';
    setTimeout(() => { btn.textContent = orig; btn.style.background = ''; emailForm.reset(); }, 3000);
  });
}

/* --- VIDEO FIX: try multiple path formats --- */
document.querySelectorAll('video').forEach(vid => {
  vid.addEventListener('error', function() {
    // If video fails, try alternative paths
    const sources = vid.querySelectorAll('source');
    sources.forEach(src => {
      const current = src.getAttribute('src');
      if (current && !current.startsWith('http')) {
        // Try without leading slash variations
        const alternatives = [
          current,
          './' + current.replace(/^\//, ''),
          '../' + current.replace(/^\//, ''),
          '/' + current.replace(/^\//, ''),
        ];
        // Just ensure src is set correctly
        src.setAttribute('src', current);
      }
    });
    vid.load();
  }, true);
});
