// Lightweight polling for “live-ish” UI with Notification support.
(function () {
  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  async function fetchJson(url) {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  }

  function notify(alert) {
    if (!("Notification" in window)) return;
    if (Notification.permission === "granted") {
      const n = new Notification(`TECHCAMAI: ${alert.label.toUpperCase()}`, {
        body: `Confidence: ${Math.round(alert.conf * 100)}% on camera #${alert.camera_id}`,
        icon: '/static/techcamai-icon-128.png',
        tag: 'techcamai-alert'
      });
      n.onclick = () => {
        window.focus();
        window.location.href = '/alerts';
      };
    }
  }

  async function run() {
    const cfg = window.TECHCAMAI_POLL || { enabled: false };
    if (!cfg.enabled) return;

    // Request permission on first interaction/load
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }

    let since = cfg.since || Math.floor(Date.now() / 1000) - 10;
    const everyMs = cfg.everyMs || 2500;

    while (true) {
      try {
        const url = (cfg.endpoint || '/api/alerts/latest') + (cfg.endpoint?.includes('?') ? '&' : '?') + 'since=' + encodeURIComponent(since);
        const data = await fetchJson(url);

        if (data && Array.isArray(data.alerts) && data.alerts.length) {
          // Notify for the most recent alert
          notify(data.alerts[0]);

          // Refresh the page to show new data
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
