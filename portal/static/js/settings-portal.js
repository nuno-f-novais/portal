/* settings-portal.js — collects & saves portal icons/modules */
(function(){
  if (window.__settingsPortalInitialized) window.__settingsPortalInitialized();
  window.__settingsPortalInitialized = function(){ /* allow re-init if needed */ };

  function $(s, c){ return (c||document).querySelector(s); }
  function $$(s, c){ return Array.prototype.slice.call((c||document).querySelectorAll(s)); }

  function collectPayload(){
    // Icons
    var icons = $$('#portal-icons-body .pi-row').map(function(row){
      return {
        enabled: row.querySelector('.pi-enabled')?.checked || false,
        title: row.querySelector('.pi-title')?.value.trim() || '',
        url: row.querySelector('.pi-url')?.value.trim() || '',
        icon_class: row.querySelector('.pi-icon')?.value.trim() || '',
        show_in_nav: row.querySelector('.pi-shownav')?.checked || false,
        new_tab: row.querySelector('.pi-newtab')?.checked || false
      };
    }).filter(function(it){ return it.title || it.url; });

    // Modules
    var modules = {};
    $$('#modules-body .mod-row').forEach(function(row){
      var k = row.getAttribute('data-key');
      var enabled = row.querySelector('.mod-enabled')?.checked || false;
      var showNav = row.querySelector('.mod-nav')?.checked || false;
      var showHome = row.querySelector('.mod-home')?.checked || false;
      var anon = row.querySelector('.mod-anon')?.checked || false;
      var roles = row.querySelector('.mod-roles')?.value.trim() || '';

      // Send a superset of keys to match older/newer backends
      modules[k] = {
        enabled: enabled,
        show_in_nav: showNav,
        show_in_home: showHome,
        // Legacy aliases to avoid regressions:
        nav: showNav,
        home: showHome,
        show_home: showHome,
        anonymous: anon,
        roles: roles
      };
    });

    return { icons: icons, modules: modules };
  }

  async function save(){
    var btn = document.getElementById('save-btn');
    var status = document.getElementById('save-status');
    if(!btn || !status) return;
    btn.disabled = true;
    status.textContent = 'Saving...';
    var payload = collectPayload();

    async function post(url){
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if(!res.ok) return { ok:false };
        return await res.json();
      } catch(e){ return { ok:false }; }
    }

    // Try primary route, then fallback
    var resp = await post('/settings/admin/save');
    if(!resp.ok) resp = await post('/settings/save');

    status.textContent = resp.ok ? 'Saved.' : 'Save failed.';
    setTimeout(function(){ status.textContent=''; }, 2200);
    btn.disabled = false;
  }

  document.addEventListener('DOMContentLoaded', function(){
    var addIcon = document.getElementById('add-icon');
    if(addIcon){
      addIcon.addEventListener('click', function(){
        var tbody = document.getElementById('portal-icons-body');
        if(!tbody) return;
        var tr = document.createElement('tr');
        tr.className = 'pi-row';
        tr.innerHTML = ''
          + '<td><label class="switch">'
          + '  <input type="checkbox" class="pi-enabled" checked><span class="slider"></span>'
          + '</label></td>'
          + '<td><input class="pi-title" type="text" placeholder="e.g. Docs"></td>'
          + '<td><input class="pi-url" type="url" placeholder="https://..."></td>'
          + '<td><input class="pi-icon" type="text" placeholder="fa-solid fa-book or bi bi-book"></td>'
          + '<td><label class="switch"><input type="checkbox" class="pi-shownav"><span class="slider"></span></label></td>'
          + '<td><label class="switch"><input type="checkbox" class="pi-newtab" checked><span class="slider"></span></label></td>'
          + '<td><button class="btn btn-danger btn-sm pi-remove" type="button" title="Remove">×</button></td>';
        tbody.appendChild(tr);
      });
    }

    document.body.addEventListener('click', function(e){
      var b = e.target.closest('.pi-remove');
      if(b){
        e.preventDefault();
        var tr = b.closest('tr'); if(tr) tr.remove();
      }
    });

    var saveBtn = document.getElementById('save-btn');
    if(saveBtn) saveBtn.addEventListener('click', save);
  });
})();
