// Lightweight polling for “live-ish” UI without websockets.
// Usage: include and set window.TECHCAMAI_POLL = { enabled: true, everyMs: 2500, endpoint: '/api/alerts/latest?since=...' }
(function () {
  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  async function fetchJson(url) {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  }

  async function run() {
    const cfg = window.TECHCAMAI_POLL || { enabled: false };
    if (!cfg.enabled) return;

    let since = cfg.since || 0;
    const everyMs = cfg.everyMs || 2500;

    while (true) {
      try {
        const url = (cfg.endpoint || '/api/alerts/latest') + (cfg.endpoint?.includes('?') ? '&' : '?') + 'since=' + encodeURIComponent(since);
        const data = await fetchJson(url);
        if (data && Array.isArray(data.alerts) && data.alerts.length) {
          // Simplest + most robust for MVP: refresh the page if anything new arrives.
          // (No fragile DOM patching.)
          window.location.reload();
          return;
        }
        if (data && typeof data.now_ts === 'number') since = Math.max(since, data.now_ts);
      } catch (e) {
        // Ignore transient errors.
      }
      await sleep(everyMs);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
