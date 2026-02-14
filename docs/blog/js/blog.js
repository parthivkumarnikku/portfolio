/**
 * Blog Section JavaScript
 * Handles theme toggle, sidebar toggle, and active link highlighting
 */

(function() {
  'use strict';

  // ===== THEME TOGGLE =====
  const themeToggle = document.getElementById('theme-toggle');
  
  // Check for saved theme preference or default to dark theme
  function getSavedTheme() {
    return localStorage.getItem('blog-theme') || 'dark';
  }
  
  // Apply theme to document
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('blog-theme', theme);
  }
  
  // Toggle theme
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
  }
  
  // Initialize theme on page load
  function initTheme() {
    const savedTheme = getSavedTheme();
    applyTheme(savedTheme);
  }
  
  // Add event listener for theme toggle
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  
  // Initialize theme
  initTheme();


  // ===== SIDEBAR TOGGLE (Mobile) =====
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('blog-sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  
  function openSidebar() {
    if (sidebar) {
      sidebar.classList.add('open');
    }
    if (sidebarOverlay) {
      sidebarOverlay.classList.add('active');
    }
    document.body.style.overflow = 'hidden';
  }
  
  function closeSidebar() {
    if (sidebar) {
      sidebar.classList.remove('open');
    }
    if (sidebarOverlay) {
      sidebarOverlay.classList.remove('active');
    }
    document.body.style.overflow = '';
  }
  
  function toggleSidebar() {
    if (sidebar && sidebar.classList.contains('open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  }
  
  // Add event listener for sidebar toggle button
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', toggleSidebar);
  }
  
  // Close sidebar when clicking overlay
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
  }
  
  // Close sidebar when pressing Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeSidebar();
    }
  });


  // ===== ACTIVE LINK HIGHLIGHTING =====
  function highlightActiveLink() {
    const currentPath = window.location.pathname;
    const currentFile = currentPath.split('/').pop() || 'index.html';
    
    // Handle navbar active state
    const navLinks = document.querySelectorAll('.blog-navbar .nav-link');
    navLinks.forEach(link => {
      const linkPath = link.getAttribute('href');
      const linkFile = linkPath.split('/').pop();
      
      if (linkFile === currentFile || 
          (currentFile === '' && linkFile === 'index.html') ||
          (currentFile === 'blog1.html' && linkPath.includes('blog1')) ||
          (currentFile === 'blog2.html' && linkPath.includes('blog2'))) {
        link.classList.add('active');
      }
    });
    
    // Handle sidebar active state (for blog pages)
    const sidebarLinks = document.querySelectorAll('.blog-sidebar a');
    sidebarLinks.forEach(link => {
      const linkPath = link.getAttribute('href');
      const linkFile = linkPath.split('/').pop();
      
      if (linkFile === currentFile) {
        link.classList.add('active');
      }
    });
  }
  
  // Initialize active link highlighting
  highlightActiveLink();


  // ===== MOBILE NAVBAR TOGGLE =====
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.querySelector('.blog-navbar .nav-links');
  
  function toggleMobileNav() {
    if (navLinks) {
      navLinks.classList.toggle('mobile-open');
    }
    if (mobileMenuBtn) {
      mobileMenuBtn.classList.toggle('active');
    }
  }
  
  function closeMobileNav() {
    if (navLinks) {
      navLinks.classList.remove('mobile-open');
    }
    if (mobileMenuBtn) {
      mobileMenuBtn.classList.remove('active');
    }
  }
  
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', toggleMobileNav);
  }
  
  // Close mobile menu when clicking outside
  document.addEventListener('click', function(e) {
    if (navLinks && navLinks.classList.contains('mobile-open')) {
      if (!navLinks.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
        closeMobileNav();
      }
    }
  });
  
  // Close mobile menu when pressing Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeMobileNav();
    }
  });
  

  // ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });


  // ===== FADE-IN ANIMATION ON SCROLL =====
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);
  
  // Observe elements with fade-in class
  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });

})();

