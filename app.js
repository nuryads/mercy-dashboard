/* MERCY Design Dashboard — GitHub Pages + Firebase real-time PO editor. */
(() => {
  'use strict';

  const CONFIG = window.MERCY_CONFIG || {};
  const el = (id) => document.getElementById(id);
  const fmt = (v) => new Intl.NumberFormat('id-ID').format(v);
  const PALETTE = {
    'TUNGGU ACC': '#f0b358', 'REV SO': '#ef8893', 'SO': '#6895e7',
    'ACC': '#50b499', 'REPEAT': '#8b73de'
  };
  const CHIPS = {
    'TUNGGU ACC': 'chip-wait', 'REV SO': 'chip-revise', 'SO': 'chip-so',
    'ACC': 'chip-acc', 'REPEAT': 'chip-repeat'
  };
  const BASE_STATUSES = ['TUNGGU ACC', 'REV SO', 'SO', 'ACC', 'REPEAT'];
  const MONTHS_ID = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  let DATA = Array.isArray(window.MERCY_INITIAL_DATA) ? window.MERCY_INITIAL_DATA.slice() : [];
  const INITIAL_DATA = DATA.map(r => ({...r}));
  const ADMIN_EMAIL = String(CONFIG.adminEmail || '').trim().toLowerCase();
  let CLOUD = null;
  let ADMIN = false;
  let REMOTE_READY = false;
  let CURRENT_ID = null;
  let SAVING = false;
  let TOAST_TIMEOUT = null;

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  function parseDate(input) {
    if (input === null || input === undefined || input === '') return '';
    const text = String(input).trim();
    let m = text.match(/^Date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})\)/i);
    if (m) return `${m[1]}-${String(Number(m[2]) + 1).padStart(2, '0')}-${m[3].padStart(2, '0')}`;
    m = text.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
    if (m) return `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}`;
    m = text.match(/^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$/);
    if (m) return `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}`;
    m = text.match(/^(\d{1,2})\s+([a-z]+)\s+(\d{2,4})$/i);
    if (m) {
      const names = {
        jan: 1, januari: 1, feb: 2, februari: 2, mar: 3, maret: 3,
        apr: 4, april: 4, mei: 5, may: 5, jun: 6, juni: 6,
        jul: 7, juli: 7, agu: 8, ags: 8, agustus: 8,
        sep: 9, september: 9, okt: 10, oktober: 10,
        nov: 11, november: 11, des: 12, desember: 12
      };
      const month = names[m[2].toLowerCase()];
      const year = m[3].length === 2 ? 2000 + Number(m[3]) : Number(m[3]);
      if (month) return `${year}-${String(month).padStart(2, '0')}-${m[1].padStart(2, '0')}`;
    }
    if (typeof input === 'number' || /^\d{5}(\.\d+)?$/.test(text)) {
      const dayNumber = Number(input);
      if (dayNumber > 35000 && dayNumber < 90000) {
        const date = new Date(Date.UTC(1899, 11, 30) + Math.round(dayNumber) * 86400000);
        return date.toISOString().slice(0, 10);
      }
    }
    return '';
  }

  function dateFmt(v) {
    if (!v || !/^\d{4}-\d{2}-\d{2}$/.test(v)) return '—';
    return new Date(`${v}T12:00:00`).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function parseQty(input) {
    if (input === null || input === undefined || String(input).trim() === '') return null;
    if (typeof input === 'number') return Number.isFinite(input) ? input : null;
    let s = String(input).trim().replace(/\s/g, '');
    if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)) s = s.replace(/\./g, '').replace(',', '.');
    else if (/^\d{1,3}(,\d{3})+(\.\d+)?$/.test(s)) s = s.replace(/,/g, '');
    else if (/^\d+,\d+$/.test(s)) s = s.replace(',', '.');
    const result = Number(s);
    return Number.isFinite(result) && result >= 0 ? result : null;
  }

  function normalizeHeader(input) {
    return String(input ?? '').toUpperCase().replace(/\u00A0/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function rowsToRecords(headers, rawRows) {
    const col = new Map(headers.map((h, i) => [normalizeHeader(h), i]));
    if (!col.has('DESIGN') && !col.has('DESAIN')) {
      throw new Error('Kolom DESIGN tidak ditemukan. Header wajib: TGL, DESIGN, WARNA, QTY, CUSTOMER, KODE, KET.');
    }
    const get = (r, names) => {
      for (const name of names) {
        if (col.has(name)) return r[col.get(name)] ?? '';
      }
      return '';
    };
    const result = rawRows.map((r, idx) => ({
      id: idx + 1,
      tgl: parseDate(get(r, ['TGL', 'TANGGAL', 'DATE'])),
      design: String(get(r, ['DESIGN', 'DESAIN', 'NAMA DESIGN']) ?? '').trim(),
      warna: String(get(r, ['WARNA', 'COLOR']) ?? '').trim(),
      qty: parseQty(get(r, ['QTY', 'QUANTITY', 'JUMLAH'])),
      customer: String(get(r, ['CUSTOMER', 'PELANGGAN']) ?? '').trim(),
      kode: String(get(r, ['KODE', 'CODE']) ?? '').trim(),
      status: String(get(r, ['KET', 'STATUS', 'KETERANGAN']) ?? '').trim().toUpperCase()
    })).filter(r => r.design !== '');
    if (!result.length) throw new Error('Tidak ada data desain yang terbaca.');
    return result;
  }

  function parseCSV(text) {
    const s = text.replace(/^\uFEFF/, '');
    const firstLine = s.split(/\r?\n/, 1)[0] || '';
    const delimiter = (firstLine.match(/;/g) || []).length > (firstLine.match(/,/g) || []).length ? ';' : ',';
    const result = [];
    let line = [], value = '', quoted = false;
    for (let i = 0; i < s.length; i++) {
      const c = s[i];
      if (c === '"') {
        if (quoted && s[i + 1] === '"') { value += '"'; i++; }
        else quoted = !quoted;
      } else if (c === delimiter && !quoted) {
        line.push(value); value = '';
      } else if ((c === '\n' || c === '\r') && !quoted) {
        if (c === '\r' && s[i + 1] === '\n') i++;
        line.push(value); value = '';
        if (line.some(x => x.trim())) result.push(line);
        line = [];
      } else value += c;
    }
    line.push(value);
    if (line.some(x => x.trim())) result.push(line);
    if (!result.length) throw new Error('CSV kosong');
    return rowsToRecords(result[0], result.slice(1));
  }

  function sourceState(mode, label, detail) {
    el('sourceStrip').className = 'source-strip' + (mode === 'live' ? ' live' : mode === 'error' ? ' error' : '');
    el('sourceLabel').textContent = label;
    el('sourceDetail').textContent = detail;
  }

  function allStatuses() {
    const extra = [...new Set(DATA.map(r => r.status || 'TANPA STATUS'))].filter(s => !BASE_STATUSES.includes(s));
    return [...BASE_STATUSES, ...extra];
  }
  function statusCount(status) { return DATA.filter(r => (r.status || 'TANPA STATUS') === status).length; }
  function qtyTotal() { return DATA.reduce((acc, r) => acc + (r.qty ?? 0), 0); }

  function renderKpis() {
    const kpis = [
      ['Total desain / PO', fmt(DATA.length), 'Jumlah seluruh baris order', '▦'],
      ['Menunggu ACC', fmt(statusCount('TUNGGU ACC')), 'Perlu follow-up customer', '◷'],
      ['Revisi SO', fmt(statusCount('REV SO')), 'Memerlukan revisi', '✎'],
      ['Total QTY', fmt(qtyTotal()), `${fmt(DATA.filter(x => x.qty !== null).length)} baris berisi QTY`, '◈']
    ];
    el('kpis').innerHTML = kpis.map(k => `<article class="kpi"><div class="kpi-top"><span class="kpi-label">${k[0].toUpperCase()}</span><span class="kpi-icon">${k[3]}</span></div><div class="num">${k[1]}</div><div class="hint">${escapeHtml(k[2])}</div></article>`).join('');
  }

  function renderStatus() {
    const statuses = allStatuses();
    let offset = 0;
    const slices = statuses.map(status => {
      const next = offset + (DATA.length ? statusCount(status) / DATA.length * 100 : 0);
      const slice = `${PALETTE[status] || '#b8b7c9'} ${offset}% ${next}%`;
      offset = next; return slice;
    });
    el('donut').style.background = DATA.length ? `conic-gradient(${slices.join(',')})` : '#efedf6';
    el('donutTotal').textContent = fmt(DATA.length);
    el('legend').innerHTML = statuses.map(status => `<div class="leg"><span class="swatch" style="background:${PALETTE[status] || '#b8b7c9'}"></span><span>${escapeHtml(status)}</span><strong>${fmt(statusCount(status))}</strong></div>`).join('');
  }

  function renderMonthly() {
    const counts = new Map();
    DATA.forEach(r => { if (/^\d{4}-\d{2}-\d{2}$/.test(r.tgl)) counts.set(r.tgl.slice(0, 7), (counts.get(r.tgl.slice(0, 7)) || 0) + 1); });
    const allMonths = [...counts.keys()].sort();
    const visible = allMonths.slice(-8);
    const maxCount = Math.max(1, ...visible.map(m => counts.get(m)));
    const label = (ym) => `${MONTHS_ID[Number(ym.slice(5, 7)) - 1]} ${ym.slice(0, 4)}`;
    el('monthChart').innerHTML = visible.map((ym, i) => `<div class="bar-col ${i === visible.length - 1 ? 'highlight' : ''}" title="${label(ym)}: ${counts.get(ym)} desain / PO"><div class="bar-number">${fmt(counts.get(ym))}</div><div class="bar" style="height:${Math.max(6, (counts.get(ym) / maxCount) * 120)}px"></div></div>`).join('');
    el('monthLabels').innerHTML = visible.map(ym => `<span>${MONTHS_ID[Number(ym.slice(5, 7)) - 1]}</span>`).join('');
    el('monthRange').textContent = visible.length ? (visible.length === 1 ? label(visible[0]) : `${label(visible[0])} – ${label(visible[visible.length - 1])}`) : 'Belum ada tanggal';
    el('trendFoot').textContent = 'Grafik dihitung ulang saat baris baru ditambahkan.';
  }

  function renderFollowUp() {
    const pending = DATA.filter(r => r.status === 'TUNGGU ACC').sort((a, b) => b.tgl.localeCompare(a.tgl) || b.id - a.id);
    el('taskItems').innerHTML = pending.length
      ? pending.slice(0, 5).map(r => `<div class="task-row"><div class="task-id"><div class="task-avatar">✿</div><div><strong>${escapeHtml(r.design)}</strong><span>${dateFmt(r.tgl)} · ${escapeHtml(r.warna)}</span></div></div><span class="chip chip-wait">TUNGGU ACC</span></div>`).join('')
      : '<div class="empty">Tidak ada desain menunggu ACC 🎉</div>';
  }

  function renderInsights() {
    el('qtyTotal').textContent = fmt(qtyTotal());
    const missing = DATA.filter(r => r.qty === null).length;
    el('insights').textContent = `${fmt(statusCount('ACC') + statusCount('REPEAT'))} baris berstatus ACC / REPEAT. ${fmt(missing)} dari ${fmt(DATA.length)} baris belum memiliki QTY. Angka QTY kosong tidak dianggap pesanan nol.`;
    el('qtyNote').textContent = `ℹ️ ${fmt(missing)} baris QTY masih kosong. Edit QTY lewat tombol Edit agar total terhitung otomatis.`;
    const colorCount = {};
    DATA.forEach(r => (r.warna || '').split(/[,/]/).forEach(t => { const color = t.trim(); if (color) colorCount[color] = (colorCount[color] || 0) + 1; }));
    el('colorTags').innerHTML = Object.entries(colorCount).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([color, n]) => `<span class="soft-tag">${escapeHtml(color)} · ${fmt(n)} desain</span>`).join('');
  }

  function setOptions(select, items, emptyLabel) {
    const previous = select.value;
    select.innerHTML = `<option value="">${emptyLabel}</option>` + items.map(({ value, label }) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join('');
    if (items.some(i => i.value === previous)) select.value = previous;
  }
  function renderFilters() {
    setOptions(el('status'), allStatuses().map(s => ({ value: s, label: s })), 'Semua status');
    const months = [...new Set(DATA.map(r => r.tgl.slice(0, 7)).filter(v => /^\d{4}-\d{2}$/.test(v)))].sort().reverse();
    setOptions(el('month'), months.map(m => ({ value: m, label: `${MONTHS_ID[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}` })), 'Semua bulan');
    const customers = [...new Set(DATA.map(r => r.customer).filter(Boolean))].sort();
    setOptions(el('customer'), customers.map(c => ({ value: c, label: c })), 'Semua customer');
  }

  function filtered() {
    const q = el('q').value.trim().toLocaleLowerCase('id-ID');
    const status = el('status').value, month = el('month').value, customer = el('customer').value;
    return [...DATA].sort((a, b) => b.tgl.localeCompare(a.tgl) || b.id - a.id)
      .filter(r => (!q || [r.design, r.warna, r.kode, r.customer, r.status, r.tgl].some(v => String(v || '').toLocaleLowerCase('id-ID').includes(q)))
        && (!status || r.status === status) && (!month || r.tgl.startsWith(month)) && (!customer || r.customer === customer));
  }


  function renderTable() {
    const entries = filtered();
    el('actionsHead').hidden = !ADMIN;
    el('tbody').innerHTML = entries.length ? entries.map(r => `<tr>
      <td>${dateFmt(r.tgl)}</td><td><span class="design-name">${escapeHtml(r.design)}</span></td>
      <td>${escapeHtml(r.warna)}</td><td class="qty">${r.qty === null ? '—' : fmt(r.qty)}</td>
      <td>${escapeHtml(r.customer)}</td><td><span class="code">${escapeHtml(r.kode || '—')}</span></td>
      <td><span class="chip ${CHIPS[r.status] || 'chip-so'}">${escapeHtml(r.status || 'TANPA STATUS')}</span></td>
      ${ADMIN ? `<td><button class="actionbtn" type="button" data-op="edit" data-id="${escapeHtml(r.id)}">Edit</button><button class="actionbtn delete" type="button" data-op="delete" data-id="${escapeHtml(r.id)}">Hapus</button></td>` : ''}
    </tr>`).join('') : `<tr><td colspan="${ADMIN ? 8 : 7}" class="empty">Belum ada data yang cocok dengan filter.</td></tr>`;
    el('showCount').textContent = `Menampilkan ${fmt(entries.length)} dari ${fmt(DATA.length)} baris`;
  }

  function renderAll() {
    renderKpis(); renderStatus(); renderMonthly(); renderFollowUp(); renderInsights(); renderFilters(); renderTable();
    const validDates = DATA.map(r => r.tgl).filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort();
    el('lastDate').innerHTML = '<span class="dot"></span>' + (validDates.length ? `Data s.d. ${dateFmt(validDates[validDates.length - 1])}` : 'Belum ada tanggal');
    el('addBtn').hidden = el('addBtnSecondary').hidden = !(ADMIN && REMOTE_READY);
    el('importBtn').hidden = !(ADMIN && REMOTE_READY && DATA.length === 0);
    el('loginBtn').hidden = ADMIN;
    el('logoutBtn').hidden = !el('adminLabel').textContent;
    el('adminLabel').hidden = !el('adminLabel').textContent;
  }

  function showToast(message, error = false) {
    const t = el('toast'); t.textContent = String(message); t.className = 'toast' + (error ? ' error' : ''); t.hidden = false;
    clearTimeout(TOAST_TIMEOUT); TOAST_TIMEOUT = setTimeout(() => { t.hidden = true; }, 4800);
  }

  function csvDownload() {
    const rows = [['TGL', 'DESIGN', 'WARNA', 'QTY', 'CUSTOMER', 'KODE', 'KET'], ...filtered().map(r => [r.tgl, r.design, r.warna, r.qty ?? '', r.customer, r.kode, r.status])];
    const safeCell = (value) => {
      // Mencegah nilai teks mengaktifkan formula saat dibuka di Excel.
      let s = String(value ?? '');
      if (/^\s*[=+@\-]/.test(s)) s = "'" + s;
      return `"${s.replace(/"/g, '""')}"`;
    };
    const csv = '\uFEFF' + rows.map(row => row.map(safeCell).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'MERCY_Backup_PO_' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1200);
  }

  function isConfigured() {
    const cfg = CONFIG.firebase || {};
    return ['apiKey','authDomain','projectId','appId'].every(k => typeof cfg[k] === 'string' && cfg[k].trim().length > 8 && !cfg[k].includes('ISI_'))
      && ADMIN_EMAIL.includes('@') && !ADMIN_EMAIL.includes('email_admin');
  }

  function refreshBanner(meta = {}) {
    if (!isConfigured()) {
      sourceState('pending', 'Mode contoh · belum terhubung', '61 data awal dapat dilihat. Isi Firebase dan email admin di config.js supaya tombol Tambah/Edit PO berfungsi.');
    } else if (!REMOTE_READY) {
      sourceState('pending', 'Menghubungkan database…', 'Sedang memuat data dari Firebase. Data contoh belum menjadi data online.');
    } else if (meta.cache) {
      sourceState('error', 'Data sementara (offline/cache)', 'Sedang menampilkan cache; periksa koneksi untuk memastikan perubahan terbaru.');
    } else if (DATA.length === 0) {
      sourceState('live', 'Firebase terhubung · database kosong', ADMIN ? 'Klik “Impor 61 data awal” untuk memindahkan semua data awal ke database.' : 'Login menggunakan email admin untuk mengimpor data awal.');
    } else {
      sourceState('live', 'Online · tersinkron otomatis ✓', `${fmt(DATA.length)} PO / desain tersimpan di Firebase. Perubahan dari perangkat lain tampil otomatis.`);
    }
  }

  function openModal(id = null) {
    if (!ADMIN || !REMOTE_READY || !CLOUD) { showToast('Login sebagai admin dan pastikan database online sebelum mengedit.', true); return; }
    const existing = id === null ? null : DATA.find(r => String(r.id) === String(id));
    if (id !== null && !existing) { showToast('Data sudah berubah. Coba lagi.', true); return; }
    CURRENT_ID = existing ? String(existing.id) : null;
    el('poForm').reset();
    el('poTitle').textContent = existing ? 'Edit PO / desain' : 'Tambah PO baru';
    el('fieldDate').value = existing?.tgl || new Date().toLocaleDateString('sv-SE', {timeZone:'Asia/Jakarta'});
    el('fieldCustomer').value = existing?.customer ?? 'MERCY';
    el('fieldDesign').value = existing?.design ?? '';
    el('fieldColor').value = existing?.warna ?? '';
    el('fieldQty').value = existing?.qty ?? '';
    el('fieldCode').value = existing?.kode ?? '';
    el('fieldStatus').value = existing?.status || 'TUNGGU ACC';
    el('saveBtn').textContent = existing ? 'Simpan Perubahan' : 'Simpan PO Baru';
    el('poBackdrop').hidden = false;
    document.body.classList.add('modal-open');
    el('fieldDesign').focus();
  }

  function closeModal() {
    if (SAVING) return;
    el('poBackdrop').hidden = true;
    document.body.classList.remove('modal-open');
    CURRENT_ID = null;
  }

  async function saveForm(event) {
    event.preventDefault();
    if (SAVING || !ADMIN || !CLOUD || !REMOTE_READY) return;
    const qtyText = el('fieldQty').value.trim();
    const qty = qtyText === '' ? null : Number(qtyText);
    const record = {
      tgl: el('fieldDate').value.trim(), design: el('fieldDesign').value.trim(),
      warna: el('fieldColor').value.trim().toUpperCase(), qty,
      customer: el('fieldCustomer').value.trim().toUpperCase(),
      kode: el('fieldCode').value.trim(), status: el('fieldStatus').value.trim()
    };
    if (!/^\d{4}-\d{2}-\d{2}$/.test(record.tgl) || !record.design || !record.customer || !record.status) {
      showToast('Tanggal, nama desain, customer, dan status wajib diisi.', true); return;
    }
    if (qty !== null && (!Number.isSafeInteger(qty) || qty < 0 || qty > 999999999)) {
      showToast('QTY harus angka bulat 0–999.999.999, atau kosong.', true); return;
    }
    SAVING = true; el('saveBtn').disabled = true; el('saveBtn').textContent = 'Menyimpan…';
    try {
      await CLOUD.save(CURRENT_ID, record);
      const isEdit = CURRENT_ID !== null;
      SAVING = false; closeModal();
      showToast(isEdit ? 'Perubahan PO sudah tersimpan ✓' : 'PO baru berhasil ditambahkan ✓');
    } catch (err) {
      showToast('Gagal menyimpan: ' + String(err.message || err), true);
    } finally {
      SAVING = false; el('saveBtn').disabled = false; el('saveBtn').textContent = CURRENT_ID ? 'Simpan Perubahan' : 'Simpan PO Baru';
    }
  }

  async function removeRow(id) {
    if (!ADMIN || !REMOTE_READY || !CLOUD) return;
    const item = DATA.find(r => String(r.id) === String(id));
    if (!item) return;
    if (!confirm(`Hapus PO “${item.design}” dari database?\n\nIni akan hilang untuk semua pengguna dan tidak bisa di-undo.`)) return;
    try { await CLOUD.remove(String(id)); showToast('PO berhasil dihapus ✓'); }
    catch (err) { showToast('Gagal menghapus: ' + String(err.message || err), true); }
  }

  async function importInitial() {
    if (!CLOUD || !ADMIN || !REMOTE_READY || DATA.length !== 0) return;
    if (!confirm(`Impor ${INITIAL_DATA.length} data desain lama ke Firebase sekarang?\n\nHanya bisa dilakukan saat database masih kosong.`)) return;
    el('importBtn').disabled = true;
    try { await CLOUD.importInitial(INITIAL_DATA); showToast(`${INITIAL_DATA.length} data lama berhasil diimpor ✓`); }
    catch (err) { showToast('Impor gagal: ' + String(err.message || err), true); }
    finally { el('importBtn').disabled = false; }
  }

  async function login() {
    if (!CLOUD) { showToast('Belum bisa login. Isi config.js dan firestore.rules dulu, lalu buka website online.', true); return; }
    el('loginBtn').disabled = true;
    try { await CLOUD.login(); }
    catch (err) { showToast('Login gagal: ' + String(err.message || err), true); }
    finally { el('loginBtn').disabled = false; }
  }

  function authChanged(user) {
    const email = String(user?.email || '').toLowerCase();
    ADMIN = Boolean(email && email === ADMIN_EMAIL);
    el('adminLabel').textContent = email ? (ADMIN ? '✓ Admin: ' : 'Bukan admin: ') + email : '';
    if (!ADMIN && !el('poBackdrop').hidden) closeModal();
    renderAll();
    refreshBanner();
    if (email && !ADMIN) showToast('Akun ini hanya bisa melihat. Login menggunakan email admin yang dipasang di config.js.', true);
  }

  function cloudDataChanged(rows, info = {}) {
    DATA = rows.map(r => ({
      id: String(r.id), tgl: String(r.tgl || ''), design: String(r.design || ''),
      warna: String(r.warna || ''),
      qty: r.qty === null || r.qty === undefined || r.qty === '' ? null : parseQty(r.qty),
      customer: String(r.customer || ''), kode: String(r.kode || ''), status: String(r.status || '')
    }));
    REMOTE_READY = true;
    renderAll();
    refreshBanner({cache:info.cache});
  }

  function cloudFailed(error) {
    sourceState('error', 'Gagal sinkron dengan Firebase', String(error?.message || error) + '. Data cadangan hanya untuk contoh, bukan data terbaru.');
    showToast('Firebase gagal terhubung. Periksa config.js dan Firestore Rules.', true);
  }

  // Search, filtering, export, and editor UI.
  ['q', 'status', 'month', 'customer'].forEach(id => el(id).addEventListener(id === 'q' ? 'input' : 'change', renderTable));
  el('clearBtn').addEventListener('click', () => {
    ['q', 'status', 'month', 'customer'].forEach(id => { el(id).value = ''; }); renderTable();
  });
  el('seeAllWaiting').addEventListener('click', () => {
    el('q').value = ''; el('month').value = ''; el('customer').value = '';
    el('status').value = 'TUNGGU ACC'; renderTable(); el('database').scrollIntoView({behavior:'smooth'});
  });
  el('exportBtn').addEventListener('click', csvDownload);
  el('loginBtn').addEventListener('click', login);
  el('logoutBtn').addEventListener('click', async () => {
    if (!CLOUD) return;
    try { await CLOUD.logout(); } catch(err){ showToast('Gagal keluar: '+err.message,true); }
  });
  el('addBtn').addEventListener('click', () => openModal());
  el('addBtnSecondary').addEventListener('click', () => openModal());
  el('importBtn').addEventListener('click', importInitial);
  el('poForm').addEventListener('submit', saveForm);
  el('closeModalBtn').addEventListener('click', closeModal);
  el('cancelModalBtn').addEventListener('click', closeModal);
  el('poBackdrop').addEventListener('click', e => { if (e.target === el('poBackdrop')) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !el('poBackdrop').hidden) closeModal(); });
  el('tbody').addEventListener('click', e => {
    const button = e.target.closest('button[data-op]');
    if (!button) return;
    if (button.dataset.op === 'edit') openModal(button.dataset.id);
    else if (button.dataset.op === 'delete') removeRow(button.dataset.id);
  });

  renderAll(); refreshBanner();
  if (isConfigured()) {
    // Di halaman contoh tanpa Firebase, chart tetap tampil; data belum bisa diubah online.
    import('./firebase-client.js')
      .then(module => { CLOUD = module.startFirebase(CONFIG, {
        onAuth: authChanged, onRows: cloudDataChanged, onError: cloudFailed
      }); })
      .catch(err => cloudFailed(err));
  }
})();
