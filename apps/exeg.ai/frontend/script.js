/**
 * A Culpa é das Ovelhas - Script Principal
 * Interações e funcionalidades do site
 */

document.addEventListener("DOMContentLoaded", function () {
  // Menu Toggle (hamburger)
  const menuToggle = document.getElementById("menuToggle");
  const navMenu = document.querySelector(".nav-menu");

  if (navMenu) {
    const navLinks = Array.from(navMenu.querySelectorAll("a"));

    // Garantir link "Bíblia" e padronizar URL para o leitor (biblia.html)
    const bibleLink =
      navLinks.find((link) =>
        (link.textContent || "").toLowerCase().includes("bíblia")
      ) ||
      navLinks.find((link) =>
        (link.getAttribute("href") || "").toLowerCase().includes("biblia")
      );

    if (bibleLink) {
      bibleLink.href = "biblia.html";
      bibleLink.classList.add("nav-link");
      bibleLink.textContent = "Bíblia";
    } else {
      const newBibleLink = document.createElement("a");
      newBibleLink.href = "biblia.html";
      newBibleLink.className = "nav-link";
      newBibleLink.textContent = "Bíblia";
      navMenu.appendChild(newBibleLink);
    }

    // Ajustar estado ativo baseado na URL atual
    const normalizeActivePage = (file) => {
      const map = {
        "biblia-belem.html": "biblia.html",
        "blog.html": "artigos.html",
        "livrinho.html": "livro.html"
      };
      return map[file] || file;
    };

    const currentPage = (() => {
      const path = window.location.pathname;
      const file = path.endsWith("/") ? "index.html" : path.split("/").pop();
      return normalizeActivePage(file || "index.html");
    })();

    navMenu.querySelectorAll("a.nav-link").forEach((link) => {
      const href = (link.getAttribute("href") || "")
        .split("#")[0]
        .split("?")[0];
      const hrefFile =
        href === "" || href === "/" ? "index.html" : href.split("/").pop();
      link.classList.toggle(
        "active",
        normalizeActivePage(hrefFile) === currentPage
      );
    });
  }

  if (menuToggle && navMenu) {
    const openLabel = (
      menuToggle.getAttribute("data-open-label") ||
      menuToggle.textContent ||
      "Menu"
    ).trim();
    const closeLabel = (
      menuToggle.getAttribute("data-close-label") ||
      (openLabel === "☰" ? "✕" : "Fechar")
    ).trim();

    const setMenuLabel = (isOpen) => {
      menuToggle.textContent = isOpen ? closeLabel : openLabel;
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    };

    setMenuLabel(navMenu.classList.contains("active"));

    menuToggle.addEventListener("click", function () {
      navMenu.classList.toggle("active");
      setMenuLabel(navMenu.classList.contains("active"));
    });

    // Fechar menu ao clicar em um link
    navMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", function () {
        navMenu.classList.remove("active");
        setMenuLabel(false);
      });
    });
  }

  // Theme Toggle
  const themeToggle = document.getElementById("themeToggle");

  if (themeToggle) {
    const setThemeLabel = (isLight) => {
      themeToggle.textContent = isLight ? "Escuro" : "Claro";
      themeToggle.setAttribute("aria-pressed", String(isLight));
    };

    // Carregar tema salvo
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
      document.body.classList.add("light-mode");
    }
    setThemeLabel(document.body.classList.contains("light-mode"));

    themeToggle.addEventListener("click", function () {
      document.body.classList.toggle("light-mode");
      const isLight = document.body.classList.contains("light-mode");
      setThemeLabel(isLight);
      localStorage.setItem("theme", isLight ? "light" : "dark");
    });
  }

  // Smooth scrolling for navigation links
  const navLinks = document.querySelectorAll("a[href^='#']");

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (targetId === "#") return;

      const targetElement = document.querySelector(targetId);

      if (targetElement) {
        e.preventDefault();
        const offsetTop = targetElement.offsetTop - 70;

        window.scrollTo({
          top: offsetTop,
          behavior: "smooth"
        });
      }
    });
  });

  // Header scroll effect
  const header = document.querySelector(".header, .site-header");
  if (header) {
    window.addEventListener("scroll", function () {
      const currentScroll = window.pageYOffset;

      if (currentScroll > 100) {
        header.style.boxShadow = "0 4px 16px rgba(0,0,0,0.3)";
      } else {
        header.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
      }
    });
  }

  // Animate elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe feature cards
  const featureCards = document.querySelectorAll(".feature-card");
  featureCards.forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(card);
  });

  // Observe manifesto sections
  const manifestoText = document.querySelector(".manifesto-text");
  if (manifestoText) {
    manifestoText.style.opacity = "0";
    manifestoText.style.transform = "translateY(20px)";
    manifestoText.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(manifestoText);
  }

  // Add hover effect to buttons
  const buttons = document.querySelectorAll(".btn");
  buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-2px)";
    });

    button.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });

  // Book cover animation
  const bookCover = document.querySelector(".book-cover");
  if (bookCover) {
    bookCover.addEventListener("mouseenter", function () {
      this.style.transform = "scale(1.05) rotateY(5deg)";
      this.style.transition = "transform 0.3s ease";
    });

    bookCover.addEventListener("mouseleave", function () {
      this.style.transform = "scale(1) rotateY(0)";
    });
  }

  // Parallax effect for hero section
  window.addEventListener("scroll", function () {
    const hero = document.querySelector(".hero");
    if (hero) {
      const scrolled = window.pageYOffset;
      const parallax = scrolled * 0.5;
      hero.style.transform = `translateY(${parallax}px)`;
    }
  });

  // Console message
  console.log(
    "%cA Culpa e das Ovelhas",
    "font-size: 20px; font-weight: bold; color: #1a73e8;"
  );
  console.log(
    "%cEdicao 666 - The Beast Exposed",
    "font-size: 14px; color: #f9ab00; font-style: italic;"
  );
  console.log(
    "%cAnderson Belem Costa - Soldado Leal do Deus Justo e Fiel",
    "font-size: 12px; color: #9aa0a6;"
  );
});
