/**
 * TECHCAMAI AI Assistant Client (Hands-free Voice/NLP)
 * Handles:
 * - Voice synthesis (Talking back)
 * - Navigation commands
 * - Search queries
 */

class TechCamAIAssistant {
  constructor() {
    this.speechEnabled = 'speechSynthesis' in window;
    this.recognitionEnabled = 'webkitSpeechRecognition' in window;
    this.voice = null;
    this.initVoice();
  }

  initVoice() {
    if (!this.speechEnabled) return;
    const setVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      // Prefer a natural sounding male voice or the first available
      this.voice = voices.find(v => v.name.includes('Google UK English Male')) || voices[0];
    };
    setVoice();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = setVoice;
    }
  }

  speak(text) {
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

  // Handle command from UI or Voice
  async handleCommand(cmd) {
    const query = cmd.toLowerCase();
    this.speak(`Understood. I'm looking into: ${cmd}`);

    // Basic navigation mapping
    if (query.includes('show live') || query.includes('go to wall')) {
      this.speak("Navigating to live wall.");
      window.location.href = '/live';
      return;
    }
    if (query.includes('show alerts') || query.includes('check incidents')) {
      this.speak("Opening the alert inbox.");
      window.location.href = '/alerts';
      return;
    }
    if (query.includes('manage cameras')) {
      this.speak("Opening camera inventory.");
      window.location.href = '/cameras/manage';
      return;
    }

    if (query.includes('system health') || query.includes('check worker') || query.includes('check heartbeat')) {
      this.speak("Checking system telemetry and worker heartbeat.");
      window.location.href = '/health';
      return;
    }

    if (query.includes('show people') || query.includes('find persons')) {
      this.speak("Filtering for human activity.");
      window.location.href = '/alerts?q=person';
      return;
    }

    if (query.includes('show vehicles') || query.includes('find cars')) {
      this.speak("Filtering for vehicle activity.");
      window.location.href = '/alerts?q=vehicle';
      return;
    }

    // Mock search for "Red car" / "Main gate"
    if (query.includes('red car') || query.includes('main gate')) {
      this.speak("Searching recordings for specific object signatures. Please hold.");
      setTimeout(() => {
        this.speak("I've found potential matches in the alert inbox. Filtering for your query now.");
        window.location.href = '/alerts?q=red+car';
      }, 2000);
      return;
    }

    this.speak("I'm sorry, I don't have enough data yet to complete that specific request. I'm still learning.");
  }
}

window.techcamaiAssistant = new TechCamAIAssistant();

// Trigger via ⌘K palette placeholder
document.addEventListener('keydown', (e) => {
  if (e.metaKey && e.key === 'k') {
    const cmd = prompt("Ask TECHCAMAI Assistant:");
    if (cmd) window.techcamaiAssistant.handleCommand(cmd);
  }
});
