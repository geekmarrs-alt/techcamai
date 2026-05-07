/**
 * TECHCAMAI AI Assistant Client (Jarvis UI)
 * Handles:
 * - Voice synthesis (Talking back)
 * - Navigation commands
 * - UI updates (Orb, Bubble, Panel)
 */

class TechCamAIAssistant {
  constructor() {
    this.speechEnabled = 'speechSynthesis' in window;
    this.voice = null;
    this.initVoice();
    this.initUI();
  }

  initVoice() {
    if (!this.speechEnabled) return;
    const setVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      this.voice = voices.find(v => v.name.includes('Google UK English Male')) || voices[0];
    };
    setVoice();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = setVoice;
    }
  }

  initUI() {
    this.orb = document.getElementById('ai-orb-trigger');
    this.bubble = document.getElementById('ai-speech-bubble');
    this.panel = document.getElementById('ai-jarvis-panel');
    this.history = document.getElementById('ai-history-log');
    this.input = document.getElementById('ai-command-input');

    if (this.orb) {
      this.orb.addEventListener('click', () => this.togglePanel());
    }

    if (this.input) {
      this.input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          const cmd = this.input.value.trim();
          if (cmd) {
            this.input.value = '';
            this.handleCommand(cmd);
          }
        }
      });
    }

    // Global Cmd+K / Ctrl+K focus
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.openPanel();
        if (this.input) this.input.focus();
      }
    });
  }

  togglePanel() {
    if (this.panel) this.panel.classList.toggle('active');
  }

  openPanel() {
    if (this.panel) this.panel.classList.add('active');
  }

  log(text, side = 'bot') {
    if (!this.history) return;
    const entry = document.createElement('div');
    entry.className = `ai-log-entry ${side}`;
    entry.textContent = text;
    this.history.appendChild(entry);
    this.history.scrollTop = this.history.scrollHeight;
  }

  showBubble(text, duration = 4000) {
    if (!this.bubble) return;
    this.bubble.textContent = text;
    this.bubble.classList.add('active');
    clearTimeout(this.bubbleTimeout);
    this.bubbleTimeout = setTimeout(() => {
      this.bubble.classList.remove('active');
    }, duration);
  }

  speak(text) {
    this.showBubble(text);
    this.log(text, 'bot');

    if (!this.speechEnabled) {
      console.log("AI Assistant (Text-only):", text);
      return;
    }
    window.speechSynthesis.cancel();
    const msg = new SpeechSynthesisUtterance(text);
    if (this.voice) msg.voice = this.voice;
    msg.pitch = 0.9;
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
  }

  async handleCommand(cmd) {
    this.log(cmd, 'user');
    const query = cmd.toLowerCase();

    // Basic navigation mapping
    if (query.includes('show live') || query.includes('go to wall')) {
      this.speak("Navigating to live wall.");
      setTimeout(() => window.location.href = '/live', 1500);
      return;
    }
    if (query.includes('show alerts') || query.includes('check incidents')) {
      this.speak("Opening the alert inbox.");
      setTimeout(() => window.location.href = '/alerts', 1500);
      return;
    }
    if (query.includes('manage cameras')) {
      this.speak("Opening camera inventory.");
      setTimeout(() => window.location.href = '/cameras/manage', 1500);
      return;
    }
    if (query.includes('system health') || query.includes('check worker') || query.includes('check heartbeat')) {
      this.speak("Checking system telemetry and worker heartbeat.");
      setTimeout(() => window.location.href = '/health', 1500);
      return;
    }
    if (query.includes('show people') || query.includes('find persons')) {
      this.speak("Filtering for human activity.");
      setTimeout(() => window.location.href = '/alerts?q=person', 1500);
      return;
    }
    if (query.includes('show vehicles') || query.includes('find cars')) {
      this.speak("Filtering for vehicle activity.");
      setTimeout(() => window.location.href = '/alerts?q=vehicle', 1500);
      return;
    }

    if (query.includes('status report') || query.includes('site status') || query.includes('how is the site')) {
      this.speak("Generating a full site status report.");
      try {
        const res = await fetch('/api/ai/summary');
        const data = await res.json();
        if (data.ok) {
          this.speak(data.summary);
        } else {
          this.speak("I'm having trouble accessing the telemetry right now.");
        }
      } catch (e) {
        this.speak("I cannot reach the command center at this moment.");
      }
      return;
    }

    // Mock search
    if (query.includes('red car') || query.includes('main gate')) {
      this.speak("Searching recordings for specific object signatures. Please hold.");
      setTimeout(() => {
        this.speak("I've found potential matches in the alert inbox. Filtering now.");
        setTimeout(() => window.location.href = '/alerts?q=red+car', 1000);
      }, 2000);
      return;
    }

    this.speak("I'm sorry, I don't have enough data yet to complete that specific request. I'm still learning.");
  }
}

window.techcamaiAssistant = new TechCamAIAssistant();
