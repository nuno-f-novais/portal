(function(){
  var wrap = document.querySelector('.settings-tabs');
  if(!wrap) return;
  var btnPortal = document.getElementById('tab-btn-portal');
  var btnKV     = document.getElementById('tab-btn-kv');
  var portal    = document.getElementById('tab-portal');
  var kv        = document.getElementById('tab-kv');

  function setActive(which){
    var isPortal = (which === 'portal');
    wrap.setAttribute('data-active', which);
    // buttons style swap (keep your classes)
    if(btnPortal){ btnPortal.classList.toggle('btn-secondary', isPortal); btnPortal.classList.toggle('btn-light', !isPortal); btnPortal.setAttribute('aria-selected', isPortal ? 'true' : 'false'); }
    if(btnKV){ btnKV.classList.toggle('btn-secondary', !isPortal); btnKV.classList.toggle('btn-light', isPortal); btnKV.setAttribute('aria-selected', !isPortal ? 'true' : 'false'); }
    if(portal){ portal.toggleAttribute('hidden', !isPortal); }
    if(kv){ kv.toggleAttribute('hidden', isPortal); }
    // announce
    var ev = new CustomEvent('settings:tabchange', {detail: which});
    document.dispatchEvent(ev);
  }

  btnPortal && btnPortal.addEventListener('click', function(e){ e.preventDefault(); setActive('portal'); });
  btnKV && btnKV.addEventListener('click', function(e){ e.preventDefault(); setActive('kv'); });

  // initial
  setActive(wrap.getAttribute('data-active') || 'portal');
})();
