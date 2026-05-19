/* post.js — shared script for all pages */

// Mobile nav toggle
(function () {
  var toggle = document.getElementById('navToggle');
  var links  = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('open');
    });
  }
})();

// Reading progress bar
(function () {
  var bar = document.createElement('div');
  bar.id = 'readProgress';
  document.body.prepend(bar);
  window.addEventListener('scroll', function () {
    var doc     = document.documentElement;
    var scrolled = doc.scrollTop || document.body.scrollTop;
    var total   = doc.scrollHeight - doc.clientHeight;
    bar.style.width = total > 0 ? (scrolled / total * 100) + '%' : '0%';
  }, { passive: true });
})();

// Scroll-to-top button
(function () {
  var btn = document.createElement('button');
  btn.id = 'scrollTop';
  btn.setAttribute('aria-label', 'Back to top');
  btn.innerHTML = '&#8679;';
  document.body.appendChild(btn);
  window.addEventListener('scroll', function () {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

// Lazy-load images
(function () {
  document.querySelectorAll('img').forEach(function (img) {
    if (!img.hasAttribute('loading')) img.setAttribute('loading', 'lazy');
  });
})();

// Site footer
(function () {
  if (document.querySelector('.site-footer')) return;
  var footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.innerHTML =
    '<div class="footer-inner">' +
      '<div class="footer-links">' +
        '<a href="/index.html">Home</a>' +
        '<a href="/blog.html">Blog</a>' +
        '<a href="/projects.html">Projects</a>' +
        '<a href="/code.html">Code &amp; Tools</a>' +
        '<a href="/about.html">About</a>' +
      '</div>' +
      '<p class="footer-copy">&copy; 2025 18gi0n</p>' +
    '</div>';
  document.body.appendChild(footer);
})();

// Auto-generate Table of Contents from H2/H3 in #postBody
(function buildToC() {
  var body = document.getElementById('postBody');
  var list = document.getElementById('tocList');
  if (!body || !list) return;

  var headings = body.querySelectorAll('h2, h3');
  if (headings.length < 3) {
    var toc = document.getElementById('toc');
    if (toc) toc.style.display = 'none';
    return;
  }

  headings.forEach(function (h, i) {
    if (!h.id) h.id = 'heading-' + i;
    var li = document.createElement('li');
    li.style.marginLeft = h.tagName === 'H3' ? '16px' : '0';
    var a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent;
    li.appendChild(a);
    list.appendChild(li);
  });

  var tocNav = document.getElementById('toc');
  if (tocNav && !tocNav.querySelector('.toc-inner')) {
    var inner = document.createElement('div');
    inner.className = 'toc-inner';
    while (tocNav.firstChild) inner.appendChild(tocNav.firstChild);
    tocNav.appendChild(inner);
  }
})();

// Reading time estimate
(function () {
  var body = document.getElementById('postBody');
  var el   = document.getElementById('readingTime');
  if (!body || !el) return;
  var words = body.innerText.trim().split(/\s+/).length;
  var mins  = Math.max(1, Math.ceil(words / 220));
  el.textContent = mins + ' min read';
})();

// Inject copy buttons into all <pre> blocks
(function addCopyButtons() {
  document.querySelectorAll('pre').forEach(function (pre) {
    if (pre.querySelector('.copy-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'Copy';
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = code ? code.innerText : pre.innerText;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied!';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1800);
      }).catch(function () {
        btn.textContent = 'Error';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1800);
      });
    });
    pre.appendChild(btn);
  });
})();

// Syntax highlighting via highlight.js (loaded locally)
(function () {
  var s = document.createElement('script');
  s.src = '/assets/js/highlight.min.js';
  s.onload = function () {
    document.querySelectorAll('pre').forEach(function (pre) {
      var code = pre.querySelector('code');
      if (!code) {
        // No <code> wrapper — build one from the text content,
        // temporarily removing the .copy-btn so it isn't captured as code text.
        var btn = pre.querySelector('.copy-btn');
        if (btn) pre.removeChild(btn);
        code = document.createElement('code');
        code.textContent = pre.textContent.trimEnd();
        while (pre.firstChild) pre.removeChild(pre.firstChild);
        pre.appendChild(code);
        if (btn) pre.appendChild(btn);
      }
      hljs.highlightElement(code);
    });
  };
  document.head.appendChild(s);
})();
