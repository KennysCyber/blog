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

  // Wrap in inner div if needed
  var tocNav = document.getElementById('toc');
  if (tocNav && !tocNav.querySelector('.toc-inner')) {
    var inner = document.createElement('div');
    inner.className = 'toc-inner';
    while (tocNav.firstChild) inner.appendChild(tocNav.firstChild);
    tocNav.appendChild(inner);
  }
})();

// Reading time estimate
(function readingTime() {
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
    if (pre.querySelector('.copy-btn')) return; // already added
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
