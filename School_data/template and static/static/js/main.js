/* ── Rutabo School — main.js ── */

// ── CSRF token helper for fetch() calls ───────────────────────────────────
function getCsrfToken() {
  return document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] ?? '';
}

// ── Auto-dismiss flash messages after 4 seconds ───────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // ── Tab system ────────────────────────────────────────────────────────────
  // Usage: <div class="tabs">
  //          <button class="tab-btn active" data-target="tab-1">Tab 1</button>
  //          <button class="tab-btn" data-target="tab-2">Tab 2</button>
  //        </div>
  //        <div id="tab-1" class="tab-panel active">...</div>
  //        <div id="tab-2" class="tab-panel">...</div>
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.target;
      const parent = btn.closest('[data-tabs]') ?? document;

      // Deactivate all buttons and panels in this group
      parent.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      parent.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

      // Activate clicked button and target panel
      btn.classList.add('active');
      document.getElementById(target)?.classList.add('active');
    });
  });

  // ── Staff enable/disable toggle via fetch ────────────────────────────────
  document.querySelectorAll('.staff-toggle').forEach(toggle => {
    toggle.addEventListener('change', async function () {
      const userId = this.dataset.userId;
      const enabled = this.checked;
      try {
        const resp = await fetch(`/accounts/staff/${userId}/toggle/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify({ enabled }),
        });
        const data = await resp.json();
        if (!data.success) {
          this.checked = !enabled; // revert on failure
          alert('Could not update staff access. Please try again.');
        }
      } catch {
        this.checked = !enabled;
      }
    });
  });

  // ── Confirm dangerous actions (delete buttons) ───────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      const msg = el.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ── Live table search ─────────────────────────────────────────────────────
  // Usage: <input class="table-search" data-table="my-table" placeholder="Search...">
  document.querySelectorAll('.table-search').forEach(input => {
    const tableId = input.dataset.table;
    const table = document.getElementById(tableId);
    if (!table) return;
    input.addEventListener('input', () => {
      const q = input.value.toLowerCase();
      table.querySelectorAll('tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });
});