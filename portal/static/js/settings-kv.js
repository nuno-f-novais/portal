/* settings-kv.js — lazy load and save KV settings */
(function(){
  if (window.__settingsKVInitialized) window.__settingsKVInitialized();
  window.__settingsKVInitialized = function(){};

  function $(s, c){ return (c||document).querySelector(s); }
  function $$(s, c){ return Array.prototype.slice.call((c||document).querySelectorAll(s)); }

  async function getList(){
    async function fetchJson(url){
      try { const r = await fetch(url); if(!r.ok) return null; return await r.json(); } catch(e){ return null; }
    }
    return await fetchJson('/settings/admin/kv/list') || await fetchJson('/settings/kv/list') || {items:[]};
  }
  async function postSave(payload){
    async function post(url){
      try { const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)}); if(!r.ok) return null; return await r.json(); } catch(e){ return null; }
    }
    return await post('/settings/admin/kv/save') || await post('/settings/kv/save');
  }

  document.addEventListener('DOMContentLoaded', function(){
    var portalBtn = document.getElementById('tab-btn-portal');
    var kvBtn = document.getElementById('tab-btn-kv');
    var kvPane = document.getElementById('tab-kv');
    var tbody = document.getElementById('kv-body');
    var addBtn = document.getElementById('kv-add');
    var saveBtn = document.getElementById('kv-save');

    function row(key, val){
      var tr = document.createElement('tr');
      tr.className = 'kv-row';
      tr.innerHTML = ''
        + '<td><input class="kv-key" type="text" value="' + (key || '') + '"></td>'
        + '<td><input class="kv-value" type="text" value="' + (val || '') + '"></td>'
        + '<td><button class="btn btn-danger kv-del" type="button">×</button></td>';
      tr.querySelector('.kv-del').addEventListener('click', function(){ tr.remove(); });
      return tr;
    }

    async function ensureLoaded(){
      if(!kvPane || kvPane.dataset.loaded) return;
      kvPane.dataset.loaded = '1';
      var list = await getList();
      tbody.innerHTML = '';
      (list.items || []).forEach(function(it){ tbody.appendChild(row(it.key, it.value)); });
    }

    if(kvBtn){
      kvBtn.addEventListener('click', ensureLoaded);
    }
    // If KV is initially active
    if(kvPane && kvPane.classList.contains('active')) ensureLoaded();

    if(addBtn) addBtn.addEventListener('click', function(){ tbody.appendChild(row('', '')); });
    if(saveBtn) saveBtn.addEventListener('click', async function(){
      var items = $$('.kv-row', tbody).map(function(tr){
        return { key: tr.querySelector('.kv-key').value.trim(), value: tr.querySelector('.kv-value').value };
      }).filter(function(it){ return it.key; });
      var resp = await postSave({items: items});
      // optional: you can show a toast/status if needed
    });
  });
})();
