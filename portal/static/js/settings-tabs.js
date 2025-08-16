/* settings-tabs.js — robust, idempotent tab controller */
(function(){
  if (window.__settingsTabsInitialized) return;
  window.__settingsTabsInitialized = true;

  document.addEventListener('DOMContentLoaded', function(){
    var wrap = document.querySelector('.settings-tabs');
    if(!wrap) return;

    var bar = wrap.querySelector('.tab-bar');
    if(!bar){
      bar = document.createElement('div');
      bar.className = 'tab-bar';
      wrap.insertBefore(bar, wrap.firstChild);
    }
    bar.setAttribute('role','tablist');

    // Find panels present in DOM
    var panels = Array.prototype.slice.call(document.querySelectorAll('.settings-tabs .tab-panel'));
    panels.forEach(function(p){
      p.setAttribute('role', 'tabpanel');
      if(!p.id) p.id = 'tab-' + Math.random().toString(36).slice(2);
      // Upsert a matching button if missing
      var name = p.id.replace(/^tab-/, '');
      var btn = document.getElementById('tab-btn-' + name) ||
                bar.querySelector('.tab-btn[data-tab="'+name+'"]');
      if(!btn){
        btn = document.createElement('button');
        btn.className = 'tab-btn btn btn-light';
        btn.setAttribute('data-tab', name);
        btn.id = 'tab-btn-' + name;
        btn.textContent = p.getAttribute('data-label') || name;
        bar.appendChild(btn);
      }
      btn.setAttribute('role','tab');
      btn.setAttribute('aria-controls', p.id);
    });

    function show(name){
      var activeName = name || (wrap.getAttribute('data-active') || 'portal');
      wrap.setAttribute('data-active', activeName);
      panels.forEach(function(p){
        var on = (p.id === 'tab-' + activeName);
        if(on){
          p.classList.add('active');
          p.removeAttribute('hidden');
          p.setAttribute('aria-hidden','false');
        }else{
          p.classList.remove('active');
          p.setAttribute('hidden','');
          p.setAttribute('aria-hidden','true');
        }
      });
      Array.prototype.forEach.call(bar.querySelectorAll('.tab-btn'), function(b){
        var isOn = b.getAttribute('data-tab') === activeName;
        b.classList.toggle('btn-secondary', isOn);
        b.classList.toggle('btn-light', !isOn);
        b.classList.toggle('active', isOn);
        b.setAttribute('aria-selected', isOn ? 'true' : 'false');
        b.setAttribute('tabindex', isOn ? '0' : '-1');
      });
    }

    bar.addEventListener('click', function(ev){
      var btn = ev.target.closest('.tab-btn');
      if(!btn) return;
      ev.preventDefault();
      ev.stopPropagation();
      var name = btn.getAttribute('data-tab');
      show(name);
    }, true);

    // Initial
    var initBtn = bar.querySelector('.tab-btn.active') || bar.querySelector('.tab-btn');
    var initName = (initBtn && initBtn.getAttribute('data-tab')) || (wrap.getAttribute('data-active') || 'portal');
    show(initName);
  });
})();
