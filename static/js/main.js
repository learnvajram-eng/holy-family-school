/* Holy Family English Medium School – Main JS */

document.addEventListener('DOMContentLoaded', function () {

  // ── AOS Init ───────────────────────────────────────────────────────────────
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      offset: 60,
    });
  }

  // ── Navbar scroll effect ───────────────────────────────────────────────────
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
  }

  // ── Back to Top ────────────────────────────────────────────────────────────
  const backTopBtn = document.getElementById('backToTop');
  if (backTopBtn) {
    window.addEventListener('scroll', () => {
      backTopBtn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    backTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── Animated counters ──────────────────────────────────────────────────────
  function animateCounters() {
    const counters = document.querySelectorAll('.stat-number[data-target]');
    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target'), 10);
      const duration = 2000; // ms
      const step = Math.ceil(target / (duration / 16));
      let current = 0;

      const timer = setInterval(() => {
        current = Math.min(current + step, target);
        counter.textContent = current.toLocaleString();
        if (current >= target) clearInterval(timer);
      }, 16);
    });
  }

  // Trigger counter animation when stats section enters viewport
  const statsSection = document.querySelector('.stats-section');
  if (statsSection) {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        animateCounters();
        observer.disconnect();
      }
    }, { threshold: 0.3 });
    observer.observe(statsSection);
  }

  // ── Ticker duplicate for seamless loop ────────────────────────────────────
  const ticker = document.querySelector('.ticker-content');
  if (ticker) {
    ticker.innerHTML += ticker.innerHTML; // duplicate content
  }

  // ── Auto-dismiss flash alerts ─────────────────────────────────────────────
  const alerts = document.querySelectorAll('.flash-container .alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  // ── Active nav link highlight on scroll (for single-page sections) ────────
  const sections = document.querySelectorAll('section[id]');
  if (sections.length > 0) {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    window.addEventListener('scroll', () => {
      let current = '';
      sections.forEach(section => {
        if (window.scrollY >= section.offsetTop - 100) {
          current = section.getAttribute('id');
        }
      });
      navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') && link.getAttribute('href').includes(current)) {
          link.classList.add('active');
        }
      });
    }, { passive: true });
  }

  // ── Form validation enhancement ───────────────────────────────────────────
  const forms = document.querySelectorAll('form[novalidate]');
  forms.forEach(form => {
    form.addEventListener('submit', function (e) {
      const inputs = form.querySelectorAll('[required]');
      let hasError = false;
      inputs.forEach(input => {
        if (!input.value.trim()) {
          input.classList.add('is-invalid');
          hasError = true;
        } else {
          input.classList.remove('is-invalid');
        }
      });
      // Let server-side validation handle the rest
    });

    // Clear invalid state on input
    form.querySelectorAll('input, textarea, select').forEach(el => {
      el.addEventListener('input', () => el.classList.remove('is-invalid'));
    });
  });

  // ── Gallery filter (if using URL param filter) ────────────────────────────
  const filterBtns = document.querySelectorAll('[data-filter]');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function (e) {
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // ── Phone number formatting (basic) ──────────────────────────────────────
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach(input => {
    input.addEventListener('input', function () {
      this.value = this.value.replace(/[^0-9+\-\s()]/g, '');
    });
  });

  // ── Smooth anchor scrolling ───────────────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 80; // navbar height
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  // ── Navbar mobile: close on link click ───────────────────────────────────
  const navbarToggle = document.querySelector('.navbar-toggler');
  const navbarCollapse = document.getElementById('navbarMain');
  if (navbarCollapse) {
    navbarCollapse.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 992) {
          const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
          bsCollapse.hide();
        }
      });
    });
  }

  console.log('Holy Family School website loaded successfully.');
});
