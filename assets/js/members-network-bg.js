// assets/js/members-network-bg.js
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('networkCanvas');
  if (!canvas) return;
  
  // Respect prefers-reduced-motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (prefersReducedMotion.matches) return;

  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];
  let animationFrameId;
  let mouse = { x: -1000, y: -1000 };
  let isVisible = true;

  // Adjust these for the 'subtle' and 'premium' look
  const connectionDistance = 150;
  const mouseAttractionRadius = 250;
  
  function resize() {
    const parent = canvas.parentElement;
    if (!parent) return;
    const rect = parent.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    
    // Handle high-DPI displays for sharp rendering
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
    
    initParticles();
  }

  function getParticleCount() {
    if (window.innerWidth < 768) return 30;
    if (window.innerWidth < 1200) return 50;
    return 70;
  }

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.25; // Very slow organic movement
      this.vy = (Math.random() - 0.5) * 0.25;
      this.radius = Math.random() * 1.5 + 0.8; // Medium size nodes
    }

    update() {
      // Basic movement
      this.x += this.vx;
      this.y += this.vy;

      // Bounce smoothly off edges (kept inside canvas)
      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Mouse subtle attraction
      const dx = mouse.x - this.x;
      const dy = mouse.y - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < mouseAttractionRadius) {
        const force = (mouseAttractionRadius - dist) / mouseAttractionRadius;
        // The pull is extremely soft
        this.x += (dx / dist) * force * 0.3; 
        this.y += (dy / dist) * force * 0.3;
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'; // Slightly less opaque
      ctx.fill();
    }
  }

  function initParticles() {
    particles = [];
    const count = getParticleCount();
    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
  }

  function animate() {
    if (!isVisible) {
      animationFrameId = requestAnimationFrame(animate);
      return;
    }

    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();

      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < connectionDistance) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          
          const opacity = 1 - (dist / connectionDistance);
          // Medium visibility teal lines
          ctx.strokeStyle = `rgba(0, 169, 157, ${opacity * 0.5})`; 
          ctx.lineWidth = 0.7;
          ctx.stroke();
        }
      }
    }

    animationFrameId = requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => {
    clearTimeout(window.resizeTimer);
    window.resizeTimer = setTimeout(resize, 250);
  });

  document.addEventListener('visibilitychange', () => {
    isVisible = document.visibilityState === 'visible';
  });

  const hero = canvas.parentElement;
  if (hero) {
    hero.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });
    
    hero.addEventListener('mouseleave', () => {
      mouse.x = -1000;
      mouse.y = -1000;
    });
  }

  resize();
  animate();
});
