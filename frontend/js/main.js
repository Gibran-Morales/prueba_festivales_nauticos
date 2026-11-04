// Interactividad UI de Festivales Náuticos MX 2026 (CORE-62)
document.addEventListener('DOMContentLoaded', () => {
    // 1. Menú Hamburguesa Responsivo (#navMenuBtn)
    const navMenuBtn = document.getElementById('navMenuBtn');
    const navLinks = document.querySelector('.nav-links');
    if (navMenuBtn && navLinks) {
        navMenuBtn.addEventListener('click', () => {
            const isOpen = navLinks.classList.toggle('open');
            navMenuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            navMenuBtn.textContent = isOpen ? '✕' : '☰';
        });
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
                navMenuBtn.setAttribute('aria-expanded', 'false');
                navMenuBtn.textContent = '☰';
            });
        });
    }

    // 2. Scroll-Spy: Iluminar sección activa en la barra de navegación
    const sectionLinks = [...document.querySelectorAll('.nav-links a[href^="#"]')];
    if (sectionLinks.length > 0 && 'IntersectionObserver' in window) {
        const navObserver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const activeId = '#' + entry.target.id;
                    sectionLinks.forEach(a => {
                        a.classList.toggle('active', a.getAttribute('href') === activeId);
                    });
                }
            });
        }, { rootMargin: '-30% 0px -55% 0px' });

        sectionLinks.forEach(a => {
            const targetEl = document.querySelector(a.getAttribute('href'));
            if (targetEl) navObserver.observe(targetEl);
        });
    }

    // 3. Barra de Progreso Superior (#prog) y Botón Flotante (#scrolltop)
    const progBar = document.getElementById('prog');
    const scrollTopBtn = document.getElementById('scrolltop');
    window.addEventListener('scroll', () => {
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (progBar && docHeight > 0) {
            const pct = Math.min(100, Math.max(0, (window.scrollY / docHeight) * 100));
            progBar.style.width = pct + '%';
        }
        if (scrollTopBtn) {
            scrollTopBtn.classList.toggle('show', window.scrollY > 400);
        }
    });

    // 4. Animaciones suaves al hacer scroll (.fade-in)
    const fadeEls = document.querySelectorAll('.fade-in');
    if (fadeEls.length > 0 && 'IntersectionObserver' in window) {
        const fadeObs = new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.classList.add('visible');
                    fadeObs.unobserve(e.target);
                }
            });
        }, { threshold: 0.08 });
        fadeEls.forEach(el => fadeObs.observe(el));
    } else {
        fadeEls.forEach(el => el.classList.add('visible'));
    }

    // 5. Selector Interactivo de Andadores para el Mapa Satelital (#andadores)
    const mapFrame = document.getElementById('andadoresMapFrame');
    const mapFilterBtns = document.querySelectorAll('.map-filter-btn');
    if (mapFrame && mapFilterBtns.length > 0) {
        mapFilterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                mapFilterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const slug = btn.getAttribute('data-andador');
                mapFrame.src = slug
                    ? `/mapa_interactivo/mapa-festivales-nauticos.html?embed=1&andador=${slug}`
                    : `/mapa_interactivo/mapa-festivales-nauticos.html?embed=1`;
            });
        });
    }
});