"""Interactive QuranGraph Reviewer Server.
Serves an interactive scholarly review application for explained ayat.
Allows editorial reviewers to Approve, Edit, or Flag explanations with persistent saving
to ingest/content/review_log.json and ingest/content/explain/<surah>/<ayah>.json.

Usage:
    cd ingest && uv run generate/review_server.py [port]
    (Default port: 8080)
"""
import glob
import html
import http.server
import json
import os
import socketserver
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPLAIN_DIR = os.path.join(ROOT, "content", "explain")
REVIEW_LOG_FILE = os.path.join(ROOT, "content", "review_log.json")
DB_PATH = os.path.join(ROOT, "work", "quran.sqlite")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import validate
from qg import review_priority


def load_review_log():
    if os.path.exists(REVIEW_LOG_FILE):
        try:
            with open(REVIEW_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_review_log(log_data):
    with open(REVIEW_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)


def get_all_explained_ayat():
    files = sorted(glob.glob(os.path.join(EXPLAIN_DIR, "*", "*.json")))
    items = []
    review_log = load_review_log()

    for p in files:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        aid = data.get("id")
        if not aid:
            continue
        errs, warns = validate(data)
        prio = review_priority(data, errs, warns)
        status = review_log.get(aid, {}).get("status", "pending")
        notes = review_log.get(aid, {}).get("notes", "")

        items.append({
            "id": aid,
            "data": data,
            "errors": errs,
            "warnings": warns,
            "priority": prio,
            "status": status,
            "review_notes": notes
        })
    return items


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>QuranGraph Editorial Reviewer App</title>
  <style>
    :root {
      --bg: #f8f6f2; --surface: #ffffff; --border: #e0dad0; --text: #1a1c19;
      --text-muted: #5e635a; --accent: #0f766e; --accent-hover: #115e59;
      --gold: #b45309; --danger: #b91c1c; --success: #15803d;
      --radius: 8px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
    header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 1rem 1.5rem; position: sticky; top: 0; z-index: 100; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .header-row { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
    .logo { font-size: 1.25rem; font-weight: 700; color: var(--accent); }
    .stats { display: flex; gap: 1rem; font-size: 0.9rem; color: var(--text-muted); }
    .container { max-width: 1200px; margin: 2rem auto; padding: 0 1.5rem; }
    .filters { background: var(--surface); border: 1px solid var(--border); padding: 1rem; border-radius: var(--radius); margin-bottom: 2rem; display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; }
    .btn { padding: 0.45rem 0.9rem; border-radius: var(--radius); border: 1px solid var(--border); background: var(--surface); cursor: pointer; font-size: 0.85rem; font-weight: 600; min-height: 38px; }
    .btn.active { background: var(--accent); color: white; border-color: var(--accent); }
    .btn-approve { background: var(--success); color: white; border-color: var(--success); }
    .btn-reject { background: var(--danger); color: white; border-color: var(--danger); }
    .btn-edit { background: var(--accent); color: white; border-color: var(--accent); }
    .ayah-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1.5rem; }
    .ayah-card.must-review { border-left: 5px solid var(--danger); }
    .ayah-card.sample-review { border-left: 5px solid var(--gold); }
    .ayah-card.approved { border-left: 5px solid var(--success); }
    .arabic { font-family: "Amiri Quran", "Amiri", serif; font-size: 1.8rem; line-height: 2.2; direction: rtl; text-align: right; color: #0b1320; margin: 1rem 0; }
    .bangla { font-family: "Noto Serif Bengali", serif; line-height: 1.8; }
    .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
    .badge-must { background: #fee2e2; color: #991b1b; }
    .badge-sample { background: #fef3c7; color: #92400e; }
    .badge-approved { background: #dcfce7; color: #166534; }
    .badge-flagged { background: #fee2e2; color: #b91c1c; }
    .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200; align-items: center; justify-content: center; padding: 1.5rem; }
    .modal.active { display: flex; }
    .modal-box { background: var(--surface); max-width: 700px; width: 100%; border-radius: var(--radius); padding: 2rem; max-height: 90vh; overflow-y: auto; }
    textarea { width: 100%; border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem; font-family: inherit; font-size: 0.95rem; margin-bottom: 1rem; resize: vertical; }
  </style>
</head>
<body>
  <header>
    <div class="header-row">
      <div class="logo">۞ QuranGraph Reviewer Portal</div>
      <div class="stats" id="stats-bar">
        <span>Total Explained: <strong id="total-count">0</strong></span>
        <span>Approved: <strong id="approved-count" style="color:var(--success)">0</strong></span>
        <span>Must-Review: <strong id="must-count" style="color:var(--danger)">0</strong></span>
        <span>Sample: <strong id="sample-count" style="color:var(--gold)">0</strong></span>
      </div>
    </div>
  </header>

  <main class="container">
    <div class="filters">
      <button class="btn active" data-filter="all">All Explanations</button>
      <button class="btn" data-filter="must">Must-Review</button>
      <button class="btn" data-filter="sample">Sample-Review</button>
      <button class="btn" data-filter="approved">Approved</button>
      <button class="btn" data-filter="flagged">Flagged</button>
      <input type="search" id="search-box" placeholder="Filter by Ayah (e.g. 2:255) or keywords..." style="flex:1; padding:0.5rem 1rem; border:1px solid var(--border); border-radius:var(--radius); min-height:38px;">
    </div>

    <div id="cards-container">Loading explanations...</div>
  </main>

  <!-- Edit Modal -->
  <div class="modal" id="edit-modal">
    <div class="modal-box">
      <h2 style="margin-bottom:1rem;" id="modal-title">Edit Ayah Explanation</h2>
      <label style="font-weight:600; font-size:0.85rem;">Plain English Explanation (simple_en)</label>
      <textarea id="edit-simple-en" rows="3"></textarea>

      <label style="font-weight:600; font-size:0.85rem;">সহজ বাংলা ব্যাখ্যা (simple_bn)</label>
      <textarea id="edit-simple-bn" rows="3" class="bangla"></textarea>

      <label style="font-weight:600; font-size:0.85rem;">Practical Lesson (lesson_en)</label>
      <textarea id="edit-lesson-en" rows="2"></textarea>

      <label style="font-weight:600; font-size:0.85rem;">বাস্তব শিক্ষা (lesson_bn)</label>
      <textarea id="edit-lesson-bn" rows="2" class="bangla"></textarea>

      <label style="font-weight:600; font-size:0.85rem;">Review Notes / Scholar Commentary</label>
      <textarea id="edit-notes" rows="2" placeholder="Notes for review log..."></textarea>

      <div style="display:flex; justify-content:flex-end; gap:0.75rem;">
        <button class="btn" id="modal-cancel">Cancel</button>
        <button class="btn btn-edit" id="modal-save">Save & Mark Approved</button>
      </div>
    </div>
  </div>

  <script>
    let ayatData = [];
    let currentEditItem = null;

    async function loadData() {
      const res = await fetch('/api/ayat');
      ayatData = await res.json();
      updateStats();
      renderCards();
    }

    function updateStats() {
      document.getElementById('total-count').textContent = ayatData.length;
      document.getElementById('approved-count').textContent = ayatData.filter(a => a.status === 'approved').length;
      document.getElementById('must-count').textContent = ayatData.filter(a => a.priority === 'must-review').length;
      document.getElementById('sample-count').textContent = ayatData.filter(a => a.priority === 'sample-review').length;
    }

    function renderCards() {
      const container = document.getElementById('cards-container');
      const filter = document.querySelector('.btn.active')?.dataset.filter || 'all';
      const q = (document.getElementById('search-box')?.value || '').trim().toLowerCase();

      const filtered = ayatData.filter(item => {
        if (filter === 'must' && item.priority !== 'must-review') return false;
        if (filter === 'sample' && item.priority !== 'sample-review') return false;
        if (filter === 'approved' && item.status !== 'approved') return false;
        if (filter === 'flagged' && item.status !== 'flagged') return false;
        if (q && !item.id.includes(q) && !(item.data.simple_en || '').toLowerCase().includes(q)) return false;
        return true;
      });

      if (filtered.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:3rem; color:var(--text-muted);">No matching explanations found.</div>';
        return;
      }

      container.innerHTML = filtered.map(item => {
        const d = item.data;
        const pClass = item.status === 'approved' ? 'approved' : item.priority;
        return `
          <div class="ayah-card ${pClass}" id="card-${item.id.replace(':', '-')}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.5rem;">
              <div style="display:flex; align-items:center; gap:0.75rem;">
                <strong style="font-size:1.15rem; color:var(--accent);">Ayah ${item.id}</strong>
                <span class="badge badge-${item.priority === 'must-review' ? 'must' : 'sample'}">${item.priority}</span>
                <span class="badge badge-${item.status}">${item.status.toUpperCase()}</span>
                <span style="font-size:0.8rem; color:var(--text-muted);">Sensitivity: ${d.sensitivity || 'none'}</span>
              </div>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn btn-approve" onclick="approveAyah('${item.id}')">✓ Approve</button>
                <button class="btn btn-edit" onclick="openEditModal('${item.id}')">✏ Edit</button>
                <button class="btn btn-reject" onclick="flagAyah('${item.id}')">⚑ Flag</button>
              </div>
            </div>

            <div style="margin-bottom:1rem;">
              <div style="font-weight:600; font-size:0.85rem; color:var(--text-muted); text-transform:uppercase;">English Explanation</div>
              <p style="margin-top:0.25rem;">${d.simple_en || ''}</p>
            </div>

            <div style="margin-bottom:1rem;">
              <div style="font-weight:600; font-size:0.85rem; color:var(--text-muted); text-transform:uppercase;">সহজ বাংলা ব্যাখ্যা</div>
              <p class="bangla" style="margin-top:0.25rem;">${d.simple_bn || ''}</p>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
              <div style="background:var(--bg); padding:0.75rem; border-radius:var(--radius);">
                <div style="font-weight:600; font-size:0.8rem; color:var(--text-muted);">Practical Lesson (EN)</div>
                <p style="font-size:0.9rem;">${d.lesson_en || ''}</p>
              </div>
              <div style="background:var(--bg); padding:0.75rem; border-radius:var(--radius);">
                <div style="font-weight:600; font-size:0.8rem; color:var(--text-muted);">বাস্তব শিক্ষা (BN)</div>
                <p class="bangla" style="font-size:0.9rem;">${d.lesson_bn || ''}</p>
              </div>
            </div>

            ${d.claims && d.claims.length ? `
              <div style="border-top:1px dashed var(--border); padding-top:0.75rem; font-size:0.85rem;">
                <strong style="color:var(--text-muted);">Scholarly Citations (${d.claims.length}):</strong>
                <ul style="margin-top:0.25rem; padding-left:1.25rem;">
                  ${d.claims.map(c => `<li>"${c.text}" — <span style="color:var(--accent);">${c.sources.join(', ')}</span></li>`).join('')}
                </ul>
              </div>
            ` : ''}

            ${item.review_notes ? `
              <div style="margin-top:0.75rem; background:#f0fdf4; border:1px solid #bbf7d0; padding:0.5rem 0.75rem; border-radius:var(--radius); font-size:0.85rem; color:#166534;">
                <strong>Reviewer Notes:</strong> ${item.review_notes}
              </div>
            ` : ''}
          </div>
        `;
      }).join('');
    }

    async function approveAyah(aid) {
      const notes = prompt('Approval notes (optional, e.g. "Verified against Ibn Kathir and Sa\'di"):', '');
      if (notes === null) return;
      await fetch('/api/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: aid, status: 'approved', notes })
      });
      const item = ayatData.find(a => a.id === aid);
      if (item) {
        item.status = 'approved';
        item.review_notes = notes;
      }
      updateStats();
      renderCards();
    }

    async function flagAyah(aid) {
      const reason = prompt('Reason for flagging (e.g. "Needs classical citation check"):', '');
      if (!reason) return;
      await fetch('/api/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: aid, status: 'flagged', notes: reason })
      });
      const item = ayatData.find(a => a.id === aid);
      if (item) {
        item.status = 'flagged';
        item.review_notes = reason;
      }
      updateStats();
      renderCards();
    }

    function openEditModal(aid) {
      currentEditItem = ayatData.find(a => a.id === aid);
      if (!currentEditItem) return;
      const d = currentEditItem.data;
      document.getElementById('modal-title').textContent = `Edit Ayah ${aid}`;
      document.getElementById('edit-simple-en').value = d.simple_en || '';
      document.getElementById('edit-simple-bn').value = d.simple_bn || '';
      document.getElementById('edit-lesson-en').value = d.lesson_en || '';
      document.getElementById('edit-lesson-bn').value = d.lesson_bn || '';
      document.getElementById('edit-notes').value = currentEditItem.review_notes || '';
      document.getElementById('edit-modal').classList.add('active');
    }

    document.getElementById('modal-cancel').onclick = () => {
      document.getElementById('edit-modal').classList.remove('active');
    };

    document.getElementById('modal-save').onclick = async () => {
      if (!currentEditItem) return;
      const payload = {
        id: currentEditItem.id,
        simple_en: document.getElementById('edit-simple-en').value,
        simple_bn: document.getElementById('edit-simple-bn').value,
        lesson_en: document.getElementById('edit-lesson-en').value,
        lesson_bn: document.getElementById('edit-lesson-bn').value,
        notes: document.getElementById('edit-notes').value,
        status: 'approved'
      };

      const res = await fetch('/api/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        currentEditItem.data.simple_en = payload.simple_en;
        currentEditItem.data.simple_bn = payload.simple_bn;
        currentEditItem.data.lesson_en = payload.lesson_en;
        currentEditItem.data.lesson_bn = payload.lesson_bn;
        currentEditItem.status = 'approved';
        currentEditItem.review_notes = payload.notes;
        document.getElementById('edit-modal').classList.remove('active');
        updateStats();
        renderCards();
      } else {
        alert('Failed to save edits.');
      }
    };

    document.querySelectorAll('.filters .btn').forEach(b => {
      b.onclick = () => {
        document.querySelectorAll('.filters .btn').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        renderCards();
      };
    });

    document.getElementById('search-box').oninput = renderCards;

    loadData();
  </script>
</body>
</html>
"""


class ReviewHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif parsed.path == "/api/ayat":
            items = get_all_explained_ayat()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(items, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body)

        if parsed.path == "/api/review":
            aid = data.get("id")
            status = data.get("status")
            notes = data.get("notes", "")
            log_data = load_review_log()
            log_data[aid] = {
                "status": status,
                "notes": notes,
                "timestamp": "2026-11-03T16:00:00Z"
            }
            save_review_log(log_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

        elif parsed.path == "/api/edit":
            aid = data.get("id")
            s_num, a_num = aid.split(":")
            json_path = os.path.join(EXPLAIN_DIR, f"{int(s_num):03d}", f"{int(a_num):03d}.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    exp_data = json.load(f)
                exp_data["simple_en"] = data.get("simple_en", exp_data.get("simple_en"))
                exp_data["simple_bn"] = data.get("simple_bn", exp_data.get("simple_bn"))
                exp_data["lesson_en"] = data.get("lesson_en", exp_data.get("lesson_en"))
                exp_data["lesson_bn"] = data.get("lesson_bn", exp_data.get("lesson_bn"))
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(exp_data, f, ensure_ascii=False, indent=2)

                log_data = load_review_log()
                log_data[aid] = {
                    "status": "approved",
                    "notes": data.get("notes", "Edited and approved via Reviewer App"),
                    "timestamp": "2026-11-03T16:00:00Z"
                }
                save_review_log(log_data)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')
            else:
                self.send_error(404, "Explanation file not found")
        else:
            self.send_error(404)


def main():
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    server = socketserver.TCPServer(("", port), ReviewHandler)
    print(f"QuranGraph Reviewer Server running at http://localhost:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down review server.")
        server.server_close()


if __name__ == "__main__":
    main()
