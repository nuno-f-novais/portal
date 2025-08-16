
/*! settings-tabs-dedupe.js — drop‑in hotfix
 *  - Removes duplicate tab buttons (same data-tab)
 *  - Ensures only one panel is visible using the `hidden` attribute
 *  - Re-binds click handlers once (prevents multiple listeners)
 *  - Does not modify your panel content or styles
 */
(function(){
  var wrap = document.querySelector('.settings-tabs');
  if(!wrap) return;
  var bar = wrap.querySelector('.tab-bar');
  if(!bar) return;

  // 1) Remove duplicate tab buttons (first wins)
  var seen = new Set();
  Array.from(bar.querySelectorAll('.tab-btn')).forEach(function(btn){
    var key = (btn.getAttribute('data-tab') || btn.textContent || '').trim();
    if(!key) return;
    if(seen.has(key)) { btn.remove(); }
    else { seen.add(key); }
  });

  // 2) Collect buttons/panels
  var btns = Array.from(bar.querySelectorAll('.tab-btn'));
  var panels = Array.from(wrap.querySelectorAll('.tab-panel'));

  function show(name){
    panels.forEach(function(p){
      var on = (p.id === 'tab-' + name);
      p.toggleAttribute('hidden', !on);
      p.setAttribute('aria-hidden', on ? 'false' : 'true');
      // Cosmetic: keep/remove .active on panels if your CSS uses it (safe either way)
      p.classList.toggle('active', on);
    });
    btns.forEach(function(b){
      b.classList.toggle('active', b.getAttribute('data-tab') === name);
    });
    wrap.setAttribute('data-active', name);
  }

  // 3) Re-bind clicks exactly once (clone trick clears old listeners)
  btns = btns.map(function(b){
    var clone = b.cloneNode(true);
    b.parentNode.replaceChild(clone, b);
    return clone;
  });
  btns.forEach(function(btn){
    btn.addEventListener('click', function(ev){
      ev.preventDefault();
      show(btn.getAttribute('data-tab'));
    }, {capture:true, once:false});
  });

  // 4) Initial state
  var init =
    wrap.getAttribute('data-active') ||
    (wrap.querySelector('.tab-btn.active') && wrap.querySelector('.tab-btn.active').getAttribute('data-tab')) ||
    (btns[0] && btns[0].getAttribute('data-tab')) ||
    'portal';

  show(init);
})();
