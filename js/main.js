/* ============================================================
   PRACTICAL AI CO. — MAIN JS
============================================================ */

/* --- PARTICLE CANVAS BACKGROUND --- */
const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d');
let W, H, particles = [];

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', () => { resize(); initParticles(); });

class Particle {
  constructor() { this.reset(true); }
  reset(init) {
    this.x = Math.random() * W;
    this.y = init ? Math.random() * H : (Math.random() > 0.5 ? -5 : H + 5);
    this.size = Math.random() * 1.4 + 0.3;
    this.vx = (Math.random() - 0.5) * 0.25;
    this.vy = (Math.random() - 0.5) * 0.25;
    this.opacity = Math.random() * 0.55 + 0.08;
    this.color = Math.random() > 0.5 ? '20,184,166' : '14,165,233';
  }
  update() {
    this.x += this.vx; this.y += this.vy;
    if (this.x < -10 || this.x > W+10 || this.y < -10 || this.y > H+10) this.reset(false);
  }
  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
    ctx.fillStyle = `rgba(${this.color},${this.opacity})`;
    ctx.fill();
  }
}

function initParticles() {
  const count = Math.min(140, Math.floor((W * H) / 12000));
  particles = Array.from({ length: count }, () => new Particle());
}
initParticles();

function drawConnections() {
  const maxDist = 130;
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < maxDist) {
        const alpha = 0.07 * (1 - dist / maxDist);
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = `rgba(14,165,233,${alpha})`;
        ctx.lineWidth = 0.6;
        ctx.stroke();
      }
    }
  }
}

function animate() {
  ctx.clearRect(0, 0, W, H);
  particles.forEach(p => { p.update(); p.draw(); });
  drawConnections();
  requestAnimationFrame(animate);
}
animate();

/* --- NAV SCROLL --- */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

/* --- MOBILE NAV --- */
const toggle = document.getElementById('navToggle');
const links  = document.getElementById('navLinks');
toggle.addEventListener('click', () => links.classList.toggle('open'));
links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => links.classList.remove('open')));

/* --- SCROLL REVEAL --- */
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      const delay = entry.target.dataset.delay || i * 80;
      setTimeout(() => entry.target.classList.add('visible'), parseInt(delay));
    }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach((el, i) => {
  el.dataset.delay = i % 4 * 90;
  revealObs.observe(el);
});

/* --- EMAIL FORM --- */
const emailForm = document.getElementById('emailForm');
if (emailForm) {
  emailForm.addEventListener('submit', e => {
    e.preventDefault();
    const btn = emailForm.querySelector('button');
    const orig = btn.textContent;
    btn.textContent = '✓ You\'re in!';
    btn.style.background = '#14B8A6';
    setTimeout(() => {
      btn.textContent = orig;
      btn.style.background = '';
      emailForm.reset();
    }, 3000);
  });
}

/* --- GLOW FOLLOW on product cards --- */
document.querySelectorAll('.product-card, .start-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width  * 100).toFixed(1);
    const y = ((e.clientY - rect.top)  / rect.height * 100).toFixed(1);
    card.style.setProperty('--mx', `${x}%`);
    card.style.setProperty('--my', `${y}%`);
  });
});
