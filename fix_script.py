"""Patch index.html: add bulk paste mode using regex-based replacement."""
import re

with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# ── 1. Replace the URL tab panel contents ──
# Find the URL tab panel and replace everything from the url-input-wrap to the scan button
OLD_PATTERN = r'(<!-- TAB: URL scanning[^>]*-->\s*<div class="tab-panel" id="panelUrl">)(.*?)(<button class="analyze-btn" id="scanBtn" onclick="scanUrl\(\)">[^<]*<i data-lucide="scan-search">[^<]*</i>[^<]*Scan Product Reviews[^<]*</button>)'

NEW_PANEL_INNER = '''

        <!-- Sub-mode toggle -->
        <div class="sub-mode-wrap">
          <button class="sub-mode-btn active" id="subBtnUrl" onclick="switchSubMode('url')">
            <i data-lucide="link"></i> URL Scrape
          </button>
          <button class="sub-mode-btn" id="subBtnBulk" onclick="switchSubMode('bulk')">
            <i data-lucide="clipboard-list"></i> Paste Reviews
          </button>
        </div>

        <!-- URL sub-panel -->
        <div id="subPanelUrl">
          <div class="url-input-wrap">
            <div class="url-input-icon"><i data-lucide="link"></i></div>
            <input type="url" id="urlInput" class="url-input"
              placeholder="https://www.amazon.in/dp/B09... or flipkart.com/..."/>
          </div>
          <div class="url-hint">
            <i data-lucide="info"></i>
            Amazon &amp; Flipkart may block automated scrapers. Use &ldquo;Paste Reviews&rdquo; for a reliable demo.
          </div>
          <button class="analyze-btn" id="scanBtn" onclick="scanUrl()">
            <i data-lucide="scan-search"></i>
            Scan Product Reviews
          </button>
        </div>

        <!-- Bulk paste sub-panel -->
        <div id="subPanelBulk" style="display:none">
          <div class="url-hint" style="margin-bottom:10px;">
            <i data-lucide="info"></i>
            Paste multiple reviews below &mdash; separate each with a blank line or <code>---</code>. Up to 15 reviews.
          </div>
          <div style="text-align:right;margin-bottom:8px;">
            <button class="load-demo-btn" onclick="loadDemoReviews()">
              <i data-lucide="flask-conical"></i> Load Demo Reviews
            </button>
          </div>
          <textarea id="bulkInput" class="input-area" style="min-height:180px"
            placeholder="Paste review 1 here...&#10;&#10;Paste review 2 here...&#10;&#10;---&#10;Paste review 3 here..."></textarea>
          <button class="analyze-btn" id="bulkBtn" onclick="analyzeBulk()">
            <i data-lucide="layers"></i>
            Analyse All Reviews
          </button>
        </div>'''

m = re.search(OLD_PATTERN, content, re.DOTALL)
if not m:
    print("ERROR: Could not find URL tab panel via regex.")
    import sys; sys.exit(1)

content = content[:m.start()] + m.group(1) + NEW_PANEL_INNER + content[m.end():]
print("Step 1 done: URL tab panel replaced")

# ── 2. Add CSS for sub-mode buttons before '/* URL input */' ──
CSS_MARKER = "    /* URL input */"
NEW_CSS = """    /* Sub-mode toggle */
    .sub-mode-wrap {
      display: flex; gap: 6px; margin-bottom: 18px;
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--border); border-radius: 10px; padding: 4px;
    }
    .sub-mode-btn {
      flex: 1; padding: 8px 12px; border-radius: 7px; border: none;
      background: transparent; color: var(--text-muted);
      font-size: 13px; font-weight: 600; cursor: pointer;
      display: flex; align-items: center; justify-content: center; gap: 6px;
      font-family: 'Inter', sans-serif; transition: all 0.2s;
    }
    .sub-mode-btn svg { width: 13px; height: 13px; }
    .sub-mode-btn.active { background: rgba(108,59,255,0.2); color: var(--purple-light); }
    .sub-mode-btn:not(.active):hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }
    .load-demo-btn {
      background: rgba(108,59,255,0.12); border: 1px solid rgba(108,59,255,0.3);
      color: var(--purple-light); font-size: 12px; font-weight: 600;
      padding: 6px 14px; border-radius: 8px; cursor: pointer;
      display: inline-flex; align-items: center; gap: 5px;
      font-family: 'Inter', sans-serif; transition: all 0.2s;
    }
    .load-demo-btn:hover { background: rgba(108,59,255,0.22); }
    .load-demo-btn svg { width: 12px; height: 12px; }

    /* URL input */"""

if CSS_MARKER in content:
    content = content.replace(CSS_MARKER, NEW_CSS, 1)
    print("Step 2 done: CSS added")
else:
    print("WARNING: CSS marker not found — CSS skipped")

# ── 3. Inject JS functions before 'async function scanUrl()' ──
JS_MARKER = "  async function scanUrl() {"
NEW_JS = """  function switchSubMode(mode) {
    document.getElementById('subPanelUrl').style.display  = mode === 'url'  ? 'block' : 'none';
    document.getElementById('subPanelBulk').style.display = mode === 'bulk' ? 'block' : 'none';
    document.getElementById('subBtnUrl').classList.toggle('active',  mode === 'url');
    document.getElementById('subBtnBulk').classList.toggle('active', mode === 'bulk');
    lucide.createIcons();
  }

  const DEMO_REVIEWS = [
    "Amazing product!! Best purchase EVER!! Totally transformed my life!! 5 stars without hesitation!! Buy it NOW!!",
    "I love this product. It is great and works perfectly. I love it. Great quality. Works great. Very satisfied.",
    "Bought this for my office setup. The build quality feels premium and cable management is clean. Took 20 minutes to set up.",
    "Returned after one week. The screen started flickering on day 3 and customer support was unhelpful.",
    "Great product great price great quality great delivery great packaging great everything great great great.",
    "Works as described. Battery life is decent, gets me through a full workday if I am not on video calls constantly. Charger feels a bit flimsy though."
  ];

  function loadDemoReviews() {
    document.getElementById('bulkInput').value = DEMO_REVIEWS.join('\\n\\n---\\n');
  }

  async function analyzeBulk() {
    const reviews_text = document.getElementById('bulkInput').value.trim();
    if (!reviews_text) { alert('Please paste some reviews first, or click Load Demo Reviews.'); return; }
    const btn = document.getElementById('bulkBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div> Analysing reviews...';
    document.getElementById('scrapeResult').style.display = 'none';
    try {
      const res = await fetch('/bulk-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviews_text })
      });
      let data = {};
      try { data = await res.json(); } catch (_) {}
      if (!res.ok || data.error) throw new Error(data.error || 'Analysis failed.');
      showScrapeResult(data);
    } catch (e) {
      alert(e.message || 'Analysis failed.');
    }
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="layers"></i> Analyse All Reviews';
    lucide.createIcons();
  }

  async function scanUrl() {"""

if JS_MARKER in content:
    content = content.replace(JS_MARKER, NEW_JS, 1)
    print("Step 3 done: JS functions injected")
else:
    print("WARNING: JS marker not found")

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(content)

# Verify
for fn in ['function switchSubMode', 'function loadDemoReviews', 'function analyzeBulk', 'subPanelBulk', 'sub-mode-wrap']:
    print(fn + ":", "FOUND" if fn in content else "MISSING")
print("All done!")
