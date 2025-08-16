
(function(){
  var search = document.getElementById('user-search');
  var table = document.getElementById('users-table');
  if (!table) return;
  var rows = Array.prototype.slice.call(table.querySelectorAll('tbody tr'));

  function normalize(s){ return (s||'').toLowerCase(); }
  function applyFilter(){
    var q = normalize(search && search.value);
    rows.forEach(function(tr){
      var text = normalize(tr.getAttribute('data-username') + ' ' + tr.getAttribute('data-roles'));
      tr.style.display = (q && q.length) ? (text.indexOf(q) !== -1 ? '' : 'none') : '';
    });
  }
  if (search){
    search.addEventListener('input', applyFilter);
  }

  // Delete modal
  var modal = document.getElementById('confirm-modal');
  var yes = document.getElementById('confirm-yes');
  var toDelete = null;

  function openModal(name, id){
    toDelete = id;
    document.getElementById('confirm-text').textContent = 'Are you sure you want to delete "' + name + '"? This cannot be undone.';
    modal.setAttribute('aria-hidden','false');
    document.documentElement.classList.add('modal-open');
  }
  function closeModal(){
    modal.setAttribute('aria-hidden','true');
    document.documentElement.classList.remove('modal-open');
    toDelete = null;
  }
  modal.addEventListener('click', function(e){
    if (e.target.closest('[data-close]')) closeModal();
  });
  yes.addEventListener('click', function(){
    if (!toDelete) return;
    var form = document.getElementById('delete-form-' + toDelete);
    if (form) form.submit();
  });

  table.addEventListener('click', function(e){
    var btn = e.target.closest('[data-delete]');
    if (!btn) return;
    var id = btn.getAttribute('data-user-id');
    var name = btn.getAttribute('data-user-name');
    openModal(name, id);
  });
})();