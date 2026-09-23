/**
 * MINDCARE NER - Voice Assistant Module
 * Uses Web Speech API (Speech Recognition + Speech Synthesis)
 * With Web Audio API synthesized chimes and graceful text fallbacks.
 */

class MindCareVoiceAssistant {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.synth = window.speechSynthesis;
    this.audioCtx = null;
    this.initAudioContext();
    this.initRecognition();
    this.bindControls();
  }

  initAudioContext() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.audioCtx = new AudioCtx();
      }
    } catch (e) {
      console.warn("Web Audio API not supported", e);
    }
  }

  // Gentle synthesized chime using Web Audio API (no external MP3/WAV needed)
  playChime(type = 'success') {
    if (!this.audioCtx) return;
    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();
    osc.connect(gain);
    gain.connect(this.audioCtx.destination);

    const now = this.audioCtx.currentTime;
    if (type === 'success') {
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.exponentialRampToValueAtTime(659.25, now + 0.15); // E5
      osc.frequency.exponentialRampToValueAtTime(783.99, now + 0.35); // G5
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
      osc.start(now);
      osc.stop(now + 0.5);
    } else if (type === 'prompt') {
      osc.frequency.setValueAtTime(440, now); // A4
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.2); // A5
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    }
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Speech Recognition API not supported in this browser. Fallback enabled.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = 'en-IN';

    this.recognition.onstart = () => {
      this.isListening = true;
      this.updateVoiceUI(true, "Listening... Say a command");
      this.playChime('prompt');
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.toLowerCase().trim();
      console.log("Voice Command Detected:", transcript);
      this.updateVoiceUI(false, `Heard: "${transcript}"`);
      this.handleVoiceCommand(transcript);
    };

    this.recognition.onerror = (event) => {
      console.warn("Voice Recognition Error:", event.error);
      this.isListening = false;
      this.updateVoiceUI(false, `Error: ${event.error}`);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      const btn = document.getElementById('floating-voice-trigger');
      if (btn) btn.classList.remove('voice-listening-pulse');
    };
  }

  speak(text) {
    if (!this.synth) return;
    this.synth.cancel(); // Cancel any ongoing speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.88; // Slightly slower, very clear for elderly
    utterance.pitch = 1.05;
    this.synth.speak(utterance);
  }

  startListening() {
    if (!this.recognition) {
      // Fallback: open voice command dialog
      const modalEl = document.getElementById('voiceFallbackModal');
      if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
      } else {
        alert("Voice recognition is best supported in Google Chrome on Windows. You can use standard button controls.");
      }
      return;
    }

    try {
      if (this.isListening) {
        this.recognition.stop();
      } else {
        this.recognition.start();
      }
    } catch (e) {
      console.error("Failed to start voice recognition", e);
    }
  }

  updateVoiceUI(listening, statusText) {
    const btn = document.getElementById('floating-voice-trigger');
    const pill = document.getElementById('voice-status-pill');

    if (btn) {
      if (listening) {
        btn.classList.add('voice-listening-pulse');
      } else {
        btn.classList.remove('voice-listening-pulse');
      }
    }

    if (pill) {
      pill.style.display = 'block';
      pill.textContent = statusText;
      setTimeout(() => {
        if (!this.isListening) {
          pill.style.display = 'none';
        }
      }, 4000);
    }
  }

  handleVoiceCommand(command) {
    this.playChime('success');

    if (command.includes('start') && (command.includes('game') || command.includes('memory'))) {
      this.speak("Opening the Memory Cards game.");
      setTimeout(() => { window.location.href = '/games/memory-cards'; }, 1000);
    } else if (command.includes('reminder') || command.includes('medicine')) {
      this.speak("Opening your daily reminders.");
      setTimeout(() => { window.location.href = '/reminders'; }, 1000);
    } else if (command.includes('next activity') || command.includes('what is next')) {
      const nextCard = document.querySelector('.upcoming-reminder-title');
      const reminderText = nextCard ? nextCard.textContent : "Your next reminder is afternoon water and memory games.";
      this.speak(`Your next scheduled activity is: ${reminderText}`);
    } else if (command.includes('read') || command.includes('aloud') || command.includes('repeat')) {
      this.readCurrentPageContent();
    } else if (command.includes('progress') || command.includes('score')) {
      this.speak("Showing your weekly progress and scores.");
      setTimeout(() => { window.location.href = '/progress'; }, 1000);
    } else if (command.includes('dashboard') || command.includes('home')) {
      this.speak("Navigating to home dashboard.");
      setTimeout(() => { window.location.href = '/dashboard'; }, 1000);
    } else if (command.includes('memories') || command.includes('culture')) {
      this.speak("Opening Familiar Memories from the North-East.");
      setTimeout(() => { window.location.href = '/familiar-memories'; }, 1000);
    } else {
      this.speak(`I heard: ${command}. You can say: Start memory game, Show reminders, or Go to dashboard.`);
    }
  }

  readCurrentPageContent() {
    // Read page headings and main cards
    const mainTitle = document.querySelector('h1, h2');
    const mainCard = document.querySelector('.card-body');
    let textToRead = "";

    if (mainTitle) {
      textToRead += mainTitle.textContent.trim() + ". ";
    }
    if (mainCard) {
      textToRead += mainCard.textContent.replace(/\s+/g, ' ').trim().slice(0, 200) + "...";
    }

    if (!textToRead) {
      textToRead = "Welcome to MindCare NER. Your cognitive assistance platform.";
    }

    this.speak(textToRead);
  }

  bindControls() {
    const attach = () => {
      // Floating voice trigger
      const floatBtn = document.getElementById('floating-voice-trigger');
      if (floatBtn) {
        floatBtn.addEventListener('click', () => this.startListening());
      }

      // Read Aloud buttons on pages
      document.querySelectorAll('.btn-read-aloud').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const targetSelector = btn.getAttribute('data-read-target');
          if (targetSelector) {
            const targetEl = document.querySelector(targetSelector);
            if (targetEl) {
              this.speak(targetEl.textContent.trim());
              return;
            }
          }
          this.readCurrentPageContent();
        });
      });

      // Voice fallback form submission
      const fallbackForm = document.getElementById('voiceFallbackForm');
      if (fallbackForm) {
        fallbackForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const input = document.getElementById('voiceFallbackInput');
          if (input && input.value.trim()) {
            this.handleVoiceCommand(input.value.trim().toLowerCase());
            input.value = '';
            const modalEl = document.getElementById('voiceFallbackModal');
            if (modalEl) {
              const modal = bootstrap.Modal.getInstance(modalEl);
              if (modal) modal.hide();
            }
          }
        });
      }
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', attach);
    } else {
      attach();
    }
  }
}

// Instantiate global voice assistant
window.voiceAssistant = new MindCareVoiceAssistant();
