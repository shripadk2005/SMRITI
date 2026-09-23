/**
 * MINDCARE NER - Cognitive Games Interactive Engines
 * Fully functional implementations for all 7 cognitive games.
 * Supports online submission to /api/games/result and offline queuing in IndexedDB.
 */

// Helper to play synthesized audio cues
function playTone(type) {
  if (window.voiceAssistant && window.voiceAssistant.playChime) {
    window.voiceAssistant.playChime(type);
  }
}

// Helper to save result to backend or offline queue
async function submitGameResult(payload) {
  try {
    if (navigator.onLine) {
      const resp = await fetch('/api/games/result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        return await resp.json();
      }
    }
  } catch (err) {
    console.warn("Online submission failed, queuing locally:", err);
  }

  // If offline or request failed, queue locally
  if (window.offlineSyncManager) {
    await window.offlineSyncManager.queueItem('game_result', payload);
  }

  return {
    offline: true,
    result: payload,
    ai_difficulty: payload.difficulty,
    ai_feedback: {
      difficulty: payload.difficulty,
      message: "Result saved locally. It will sync automatically when back online."
    }
  };
}

// Display game completion modal with AI feedback
function showGameSummaryModal(gameTitle, score, accuracy, timeTaken, aiData) {
  playTone('success');

  const modalEl = document.getElementById('gameResultModal');
  if (!modalEl) {
    alert(`🎉 Great Job!\nGame: ${gameTitle}\nScore: ${score}/100\nAccuracy: ${accuracy}%\nTime: ${timeTaken}s`);
    return;
  }

  document.getElementById('modal-game-title').textContent = gameTitle;
  document.getElementById('modal-score-value').textContent = `${score}/100`;
  document.getElementById('modal-accuracy-value').textContent = `${accuracy}%`;
  document.getElementById('modal-time-value').textContent = `${timeTaken}s`;

  const aiMessageEl = document.getElementById('modal-ai-feedback');
  if (aiMessageEl && aiData && aiData.ai_feedback) {
    aiMessageEl.innerHTML = `
      <div class="alert alert-success mt-3 mb-0">
        <div class="d-flex align-items-center gap-2 mb-1">
          <i class="fa-solid fa-brain fs-4 text-success"></i>
          <strong>AI Personalization Engine:</strong>
        </div>
        <p class="mb-1">${aiData.ai_feedback.message || 'Your next activity has been personalized based on your recent performance.'}</p>
        <div class="badge bg-primary fs-6">Next Recommended Level: ${aiData.ai_difficulty || 'EASY'}</div>
      </div>
    `;
  }

  try {
    if (window.bootstrap && bootstrap.Modal) {
      const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
      modal.show();
    } else {
      modalEl.classList.add('show');
      modalEl.style.display = 'block';
    }
  } catch (e) {
    console.warn("Bootstrap modal fallback:", e);
    alert(`🎉 Great Job!\nGame: ${gameTitle}\nScore: ${score}/100\nAccuracy: ${accuracy}%\nTime: ${timeTaken}s`);
  }
}

/* ==========================================================================
   GAME 1: MEMORY CARDS (CULTURAL MATCHING)
   ========================================================================== */
class MemoryCardsGame {
  constructor(containerId, initialDifficulty = 'EASY') {
    this.container = document.getElementById(containerId);
    this.difficulty = initialDifficulty;
    this.cards = [];
    this.flippedCards = [];
    this.matchedPairs = 0;
    this.attempts = 0;
    this.startTime = null;
    this.timerInterval = null;
    this.elapsedSeconds = 0;
    this.isLocked = false;

    this.symbols = [
      { id: 'tea', name: 'Assam Tea', icon: 'fa-mug-hot' },
      { id: 'japi', name: 'Japi Hat', icon: 'fa-umbrella' },
      { id: 'rice', name: 'Rice Bowl', icon: 'fa-bowl-rice' },
      { id: 'hornbill', name: 'Hornbill', icon: 'fa-dove' },
      { id: 'flute', name: 'Bamboo Flute', icon: 'fa-music' },
      { id: 'bell', name: 'Brass Bell', icon: 'fa-bell' },
      { id: 'orchid', name: 'NER Orchid', icon: 'fa-spa' },
      { id: 'drum', name: 'Bihu Dhol', icon: 'fa-drum' }
    ];

    this.init();
  }

  init() {
    if (!this.container) return;
    const pairCount = this.difficulty === 'HARD' ? 8 : (this.difficulty === 'MEDIUM' ? 6 : 4);
    const chosenSymbols = this.symbols.slice(0, pairCount);
    const deck = [...chosenSymbols, ...chosenSymbols].sort(() => Math.random() - 0.5);

    this.matchedPairs = 0;
    this.attempts = 0;
    this.flippedCards = [];
    this.isLocked = false;
    this.totalPairs = pairCount;

    this.container.innerHTML = '';
    deck.forEach((item, index) => {
      const card = document.createElement('div');
      card.className = 'memory-card';
      card.dataset.id = item.id;
      card.dataset.index = index;
      card.innerHTML = `
        <div class="card-front"><i class="fa-solid fa-clover"></i></div>
        <div class="card-back">
          <i class="fa-solid ${item.icon}"></i>
          <span>${item.name}</span>
        </div>
      `;
      card.addEventListener('click', () => this.handleCardClick(card, item));
      this.container.appendChild(card);
    });

    this.updateStatsUI();
    this.startTimer();
  }

  startTimer() {
    clearInterval(this.timerInterval);
    this.elapsedSeconds = 0;
    this.startTime = Date.now();
    this.timerInterval = setInterval(() => {
      this.elapsedSeconds = Math.floor((Date.now() - this.startTime) / 1000);
      const timerEl = document.getElementById('game-timer-display');
      if (timerEl) timerEl.textContent = `${this.elapsedSeconds}s`;
    }, 1000);
  }

  handleCardClick(card, item) {
    if (this.isLocked || card.classList.contains('flipped') || card.classList.contains('matched')) {
      return;
    }

    card.classList.add('flipped');
    playTone('prompt');
    this.flippedCards.push({ card, item });

    if (this.flippedCards.length === 2) {
      this.attempts++;
      this.updateStatsUI();
      this.checkMatch();
    }
  }

  checkMatch() {
    this.isLocked = true;
    const [first, second] = this.flippedCards;

    if (first.item.id === second.item.id) {
      // Match found
      playTone('success');
      first.card.classList.add('matched');
      second.card.classList.add('matched');
      this.matchedPairs++;
      this.flippedCards = [];
      this.isLocked = false;
      this.updateStatsUI();

      if (this.matchedPairs === this.totalPairs) {
        this.gameComplete();
      }
    } else {
      // Mismatch
      setTimeout(() => {
        first.card.classList.remove('flipped');
        second.card.classList.remove('flipped');
        this.flippedCards = [];
        this.isLocked = false;
      }, 1000);
    }
  }

  updateStatsUI() {
    const attemptsEl = document.getElementById('game-attempts-display');
    const matchesEl = document.getElementById('game-matches-display');
    if (attemptsEl) attemptsEl.textContent = this.attempts;
    if (matchesEl) matchesEl.textContent = `${this.matchedPairs} / ${this.totalPairs}`;
  }

  async gameComplete() {
    clearInterval(this.timerInterval);
    const accuracy = Math.min(100, Math.round((this.totalPairs / Math.max(this.attempts, 1)) * 100));
    const score = Math.max(20, Math.min(100, Math.round(100 - (this.attempts - this.totalPairs) * 5 - this.elapsedSeconds * 0.5)));

    const payload = {
      game_slug: 'memory-cards',
      score: score,
      accuracy: accuracy,
      completion_time: this.elapsedSeconds,
      attempts: this.attempts,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Memory Cards', score, accuracy, this.elapsedSeconds, aiRes);
  }
}

/* ==========================================================================
   GAME 2: REMEMBER THE OBJECTS (10-SECOND RECALL)
   ========================================================================== */
class ObjectRecallGame {
  constructor(displayAreaId, choiceAreaId, difficulty = 'EASY') {
    this.displayArea = document.getElementById(displayAreaId);
    this.choiceArea = document.getElementById(choiceAreaId);
    this.difficulty = difficulty;
    this.allObjects = [
      { id: 'tea_pot', name: 'Assam Tea Pot', icon: 'fa-mug-hot' },
      { id: 'japi', name: 'Traditional Japi', icon: 'fa-umbrella' },
      { id: 'rice_bowl', name: 'Warm Rice Bowl', icon: 'fa-bowl-rice' },
      { id: 'dhol', name: 'Bihu Dhol Drum', icon: 'fa-drum' },
      { id: 'orange', name: 'Khasi Mandarin Orange', icon: 'fa-lemon' },
      { id: 'bell', name: 'Brass Pooja Bell', icon: 'fa-bell' },
      { id: 'flower', name: 'Kopou Orchid', icon: 'fa-spa' },
      { id: 'flute', name: 'Bamboo Flute', icon: 'fa-music' },
      { id: 'fan', name: 'Bamboo Hand Fan', icon: 'fa-fan' },
      { id: 'lamp', name: 'Earthen Lamp', icon: 'fa-fire' }
    ];
    this.targetObjects = [];
    this.selectedObjects = new Set();
    this.countDown = 10;
    this.timerInterval = null;
    this.startTime = null;

    this.init();
  }

  init() {
    if (!this.displayArea || !this.choiceArea) return;
    this.targetObjects = [...this.allObjects].sort(() => Math.random() - 0.5).slice(0, 5);
    this.selectedObjects.clear();
    this.countDown = 10;

    this.renderMemorizePhase();
  }

  renderMemorizePhase() {
    this.choiceArea.style.display = 'none';
    this.displayArea.style.display = 'block';

    const header = document.getElementById('recall-phase-header');
    if (header) {
      header.textContent = "👀 Look carefully and remember these 5 familiar items:";
    }

    let cardsHtml = '<div class="row g-3 justify-content-center">';
    this.targetObjects.forEach(obj => {
      cardsHtml += `
        <div class="col-6 col-md-4">
          <div class="card p-3 text-center h-100 shadow-sm border-primary">
            <i class="fa-solid ${obj.icon} fs-1 text-primary mb-2"></i>
            <h5 class="fw-bold mb-0">${obj.name}</h5>
          </div>
        </div>
      `;
    });
    cardsHtml += '</div>';

    this.displayArea.innerHTML = `
      <div class="timer-bar-container mb-3">
        <div id="recall-timer-bar" class="timer-bar-fill" style="width: 100%;"></div>
      </div>
      <div class="text-center mb-3">
        <span class="badge bg-warning text-dark fs-5">Hiding in: <span id="countdown-num">10</span> seconds</span>
      </div>
      ${cardsHtml}
    `;

    const bar = document.getElementById('recall-timer-bar');
    const num = document.getElementById('countdown-num');

    this.timerInterval = setInterval(() => {
      this.countDown--;
      if (num) num.textContent = this.countDown;
      if (bar) bar.style.width = `${(this.countDown / 10) * 100}%`;

      if (this.countDown <= 0) {
        clearInterval(this.timerInterval);
        this.renderRecallPhase();
      }
    }, 1000);
  }

  renderRecallPhase() {
    playTone('prompt');
    this.startTime = Date.now();
    this.displayArea.style.display = 'none';
    this.choiceArea.style.display = 'block';

    const header = document.getElementById('recall-phase-header');
    if (header) {
      header.textContent = "❓ Which 5 items did you just see? (Click to select)";
    }

    // Clean, bug-free shuffle: exactly the 5 targets + 4 distractors (total 9 items)
    const targetIds = new Set(this.targetObjects.map(o => o.id));
    const distractors = this.allObjects.filter(o => !targetIds.has(o.id)).sort(() => Math.random() - 0.5).slice(0, 4);
    const options = [...this.targetObjects, ...distractors].sort(() => Math.random() - 0.5);

    this.choiceArea.innerHTML = `
      <div class="row g-3 justify-content-center" id="recall-options-grid">
        ${options.map(obj => `
          <div class="col-6 col-md-4">
            <button class="btn game-option-btn w-100 h-100" data-id="${obj.id}">
              <i class="fa-solid ${obj.icon} fs-2 mb-2"></i>
              <span>${obj.name}</span>
            </button>
          </div>
        `).join('')}
      </div>
      <div class="text-center mt-4">
        <button id="btn-submit-recall" class="btn btn-elderly btn-primary-mc px-5" disabled>
          <i class="fa-solid fa-check-circle me-2"></i> Submit Answers (<span id="recall-chosen-count">0</span>/5)
        </button>
      </div>
    `;

    const buttons = this.choiceArea.querySelectorAll('.game-option-btn');
    const submitBtn = document.getElementById('btn-submit-recall');
    const countSpan = document.getElementById('recall-chosen-count');

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        if (this.selectedObjects.has(id)) {
          this.selectedObjects.delete(id);
          btn.classList.remove('selected-correct', 'border-primary');
        } else {
          if (this.selectedObjects.size < 5) {
            this.selectedObjects.add(id);
            btn.classList.add('selected-correct');
            playTone('prompt');
          }
        }
        countSpan.textContent = this.selectedObjects.size;
        submitBtn.disabled = this.selectedObjects.size !== 5;
      });
    });

    submitBtn.addEventListener('click', () => this.evaluateResults());
  }

  async evaluateResults() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    let correctCount = 0;
    const targetIds = new Set(this.targetObjects.map(o => o.id));

    this.selectedObjects.forEach(id => {
      if (targetIds.has(id)) correctCount++;
    });

    const accuracy = Math.round((correctCount / 5) * 100);
    const score = Math.max(20, Math.min(100, correctCount * 20));

    const payload = {
      game_slug: 'object-recall',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Remember the Objects', score, accuracy, elapsedSec, aiRes);
  }
}

/* ==========================================================================
   GAME 3: PATTERN RECOGNITION (SHAPE SEQUENCES)
   ========================================================================== */
class PatternGame {
  constructor(containerId, difficulty = 'MEDIUM') {
    this.container = document.getElementById(containerId);
    this.difficulty = difficulty;
    this.round = 0;
    this.maxRounds = 4;
    this.score = 0;
    this.correctCount = 0;
    this.startTime = Date.now();

    this.patterns = [
      {
        sequence: [
          { icon: 'fa-circle text-danger', name: 'Red Circle' },
          { icon: 'fa-square text-primary', name: 'Blue Square' },
          { icon: 'fa-circle text-danger', name: 'Red Circle' }
        ],
        answer: { icon: 'fa-square text-primary', name: 'Blue Square' },
        options: [
          { icon: 'fa-square text-primary', name: 'Blue Square' },
          { icon: 'fa-circle text-danger', name: 'Red Circle' },
          { icon: 'fa-star text-warning', name: 'Yellow Star' },
          { icon: 'fa-caret-up text-success', name: 'Green Triangle' }
        ]
      },
      {
        sequence: [
          { icon: 'fa-sun text-warning', name: 'Sun' },
          { icon: 'fa-moon text-info', name: 'Moon' },
          { icon: 'fa-sun text-warning', name: 'Sun' }
        ],
        answer: { icon: 'fa-moon text-info', name: 'Moon' },
        options: [
          { icon: 'fa-cloud text-secondary', name: 'Cloud' },
          { icon: 'fa-moon text-info', name: 'Moon' },
          { icon: 'fa-sun text-warning', name: 'Sun' },
          { icon: 'fa-star text-warning', name: 'Star' }
        ]
      },
      {
        sequence: [
          { icon: 'fa-leaf text-success', name: 'Leaf' },
          { icon: 'fa-leaf text-success', name: 'Leaf' },
          { icon: 'fa-droplet text-primary', name: 'Water' },
          { icon: 'fa-leaf text-success', name: 'Leaf' },
          { icon: 'fa-leaf text-success', name: 'Leaf' }
        ],
        answer: { icon: 'fa-droplet text-primary', name: 'Water' },
        options: [
          { icon: 'fa-droplet text-primary', name: 'Water' },
          { icon: 'fa-leaf text-success', name: 'Leaf' },
          { icon: 'fa-seedling text-success', name: 'Plant' },
          { icon: 'fa-fire text-danger', name: 'Fire' }
        ]
      },
      {
        sequence: [
          { icon: 'fa-heart text-danger', name: 'Heart' },
          { icon: 'fa-star text-warning', name: 'Star' },
          { icon: 'fa-heart text-danger', name: 'Heart' },
          { icon: 'fa-star text-warning', name: 'Star' }
        ],
        answer: { icon: 'fa-heart text-danger', name: 'Heart' },
        options: [
          { icon: 'fa-square text-primary', name: 'Square' },
          { icon: 'fa-circle text-info', name: 'Circle' },
          { icon: 'fa-heart text-danger', name: 'Heart' },
          { icon: 'fa-star text-warning', name: 'Star' }
        ]
      }
    ];

    this.init();
  }

  init() {
    if (!this.container) return;
    this.round = 0;
    this.correctCount = 0;
    this.startTime = Date.now();
    this.renderRound();
  }

  renderRound() {
    if (this.round >= this.maxRounds) {
      this.gameComplete();
      return;
    }

    const curr = this.patterns[this.round];
    this.container.innerHTML = `
      <div class="text-center mb-4">
        <span class="badge bg-secondary fs-6 mb-2">Round ${this.round + 1} of ${this.maxRounds}</span>
        <h4 class="fw-bold">Which symbol comes next in the pattern?</h4>
      </div>

      <div class="card p-4 text-center mb-4 bg-light shadow-sm">
        <div class="d-flex align-items-center justify-content-center gap-3 flex-wrap fs-1">
          ${curr.sequence.map(s => `
            <div class="p-3 bg-white rounded-3 shadow-sm border">
              <i class="fa-solid ${s.icon}"></i>
            </div>
          `).join('<i class="fa-solid fa-arrow-right fs-4 text-muted"></i>')}
          <i class="fa-solid fa-arrow-right fs-4 text-muted"></i>
          <div class="p-3 bg-warning-subtle rounded-3 border border-warning border-3 text-warning">
            <i class="fa-solid fa-question"></i>
          </div>
        </div>
      </div>

      <div class="row g-3 justify-content-center" id="pattern-options-row">
        ${curr.options.map((opt, idx) => `
          <div class="col-6 col-md-3">
            <button class="btn game-option-btn w-100 p-3" data-idx="${idx}">
              <i class="fa-solid ${opt.icon} fs-1 mb-2"></i>
              <span class="fs-6">${opt.name}</span>
            </button>
          </div>
        `).join('')}
      </div>
    `;

    const btns = this.container.querySelectorAll('.game-option-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.dataset.idx);
        const chosen = curr.options[idx];
        btns.forEach(b => b.disabled = true);

        if (chosen.name === curr.answer.name) {
          btn.classList.add('selected-correct');
          playTone('success');
          this.correctCount++;
        } else {
          btn.classList.add('selected-wrong');
          playTone('prompt');
        }

        setTimeout(() => {
          this.round++;
          this.renderRound();
        }, 1200);
      });
    });
  }

  async gameComplete() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    const accuracy = Math.round((this.correctCount / this.maxRounds) * 100);
    const score = Math.max(25, accuracy);

    const payload = {
      game_slug: 'pattern-recognition',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Pattern Recognition', score, accuracy, elapsedSec, aiRes);
  }
}

/* ==========================================================================
   GAME 4: ATTENTION & CONCENTRATION (TARGET FINDER)
   ========================================================================== */
class AttentionGame {
  constructor(containerId, difficulty = 'EASY') {
    this.container = document.getElementById(containerId);
    this.difficulty = difficulty;
    this.round = 0;
    this.maxRounds = 4;
    this.correctCount = 0;
    this.startTime = Date.now();

    this.challenges = [
      {
        prompt: "Find the 🔴 Red Heart among the yellow leaves",
        targetIcon: 'fa-heart text-danger',
        targetColor: 'text-danger',
        distractorIcon: 'fa-leaf text-warning',
        gridSize: 16
      },
      {
        prompt: "Find the 🐦 Singing Bird among the trees",
        targetIcon: 'fa-dove text-primary',
        distractorIcon: 'fa-tree text-success',
        gridSize: 16
      },
      {
        prompt: "Find the ☕ Steaming Tea Cup among water glasses",
        targetIcon: 'fa-mug-hot text-danger',
        distractorIcon: 'fa-glass-water text-info',
        gridSize: 20
      },
      {
        prompt: "Find the ⭐ Bright Star among circles",
        targetIcon: 'fa-star text-warning',
        distractorIcon: 'fa-circle text-secondary',
        gridSize: 20
      }
    ];

    this.init();
  }

  init() {
    if (!this.container) return;
    this.round = 0;
    this.correctCount = 0;
    this.startTime = Date.now();
    this.renderRound();
  }

  renderRound() {
    if (this.round >= this.maxRounds) {
      this.gameComplete();
      return;
    }

    const curr = this.challenges[this.round];
    const targetIdx = Math.floor(Math.random() * curr.gridSize);

    let gridHtml = '<div class="row g-2 justify-content-center">';
    for (let i = 0; i < curr.gridSize; i++) {
      const isTarget = i === targetIdx;
      gridHtml += `
        <div class="col-3 col-md-3">
          <button class="btn btn-outline-secondary w-100 p-3 fs-1 attention-tile" data-target="${isTarget}">
            <i class="fa-solid ${isTarget ? curr.targetIcon : curr.distractorIcon}"></i>
          </button>
        </div>
      `;
    }
    gridHtml += '</div>';

    this.container.innerHTML = `
      <div class="text-center mb-4">
        <span class="badge bg-secondary fs-6 mb-2">Round ${this.round + 1} of ${this.maxRounds}</span>
        <h4 class="fw-bold">${curr.prompt}</h4>
      </div>
      <div class="card p-3 shadow-sm bg-light mb-3">
        ${gridHtml}
      </div>
    `;

    const tiles = this.container.querySelectorAll('.attention-tile');
    tiles.forEach(tile => {
      tile.addEventListener('click', () => {
        const isTarget = tile.dataset.target === 'true';
        tiles.forEach(t => t.disabled = true);

        if (isTarget) {
          tile.classList.remove('btn-outline-secondary');
          tile.classList.add('btn-success');
          playTone('success');
          this.correctCount++;
        } else {
          tile.classList.remove('btn-outline-secondary');
          tile.classList.add('btn-danger');
          playTone('prompt');
        }

        setTimeout(() => {
          this.round++;
          this.renderRound();
        }, 1000);
      });
    });
  }

  async gameComplete() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    const accuracy = Math.round((this.correctCount / this.maxRounds) * 100);
    const score = Math.max(25, accuracy);

    const payload = {
      game_slug: 'attention-game',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Focus & Attention', score, accuracy, elapsedSec, aiRes);
  }
}

/* ==========================================================================
   GAME 5: DAILY ROUTINE RECALL
   ========================================================================== */
class RoutineRecallGame {
  constructor(containerId, difficulty = 'EASY') {
    this.container = document.getElementById(containerId);
    this.difficulty = difficulty;
    this.round = 0;
    this.maxRounds = 3;
    this.correctCount = 0;
    this.startTime = Date.now();

    this.scenarios = [
      {
        title: "Morning Routine",
        steps: [
          { icon: 'fa-sun text-warning', name: 'Wake Up' },
          { icon: 'fa-tooth text-info', name: 'Brush Teeth' },
          { icon: 'fa-bowl-rice text-primary', name: 'Healthy Breakfast' },
          { icon: 'fa-pills text-danger', name: 'Morning Medicine' }
        ],
        question: "What comes immediately after Healthy Breakfast?",
        correct: "Morning Medicine",
        options: ["Morning Medicine", "Sleep", "Evening Walk", "Wash Dishes"]
      },
      {
        title: "Midday Routine",
        steps: [
          { icon: 'fa-glass-water text-primary', name: 'Drink Clean Water' },
          { icon: 'fa-book-open text-secondary', name: 'Read Newspaper' },
          { icon: 'fa-plate-wheat text-success', name: 'Lunch' },
          { icon: 'fa-bed text-info', name: 'Short Afternoon Rest' }
        ],
        question: "What activity follows Read Newspaper?",
        correct: "Lunch",
        options: ["Lunch", "Midnight Walk", "Breakfast", "Brush Teeth"]
      },
      {
        title: "Evening Routine",
        steps: [
          { icon: 'fa-person-walking text-success', name: 'Gentle Walk' },
          { icon: 'fa-mug-hot text-danger', name: 'Evening Tea' },
          { icon: 'fa-phone text-primary', name: 'Call Family Member' },
          { icon: 'fa-moon text-info', name: 'Night Sleep' }
        ],
        question: "What pleasant activity happens after Evening Tea?",
        correct: "Call Family Member",
        options: ["Call Family Member", "Heavy Lifting", "Drive Car", "Wake Up"]
      }
    ];

    this.init();
  }

  init() {
    if (!this.container) return;
    this.round = 0;
    this.correctCount = 0;
    this.startTime = Date.now();
    this.renderRound();
  }

  renderRound() {
    if (this.round >= this.maxRounds) {
      this.gameComplete();
      return;
    }

    const curr = this.scenarios[this.round];
    this.container.innerHTML = `
      <div class="text-center mb-3">
        <span class="badge bg-secondary fs-6 mb-2">Round ${this.round + 1} of ${this.maxRounds}</span>
        <h4 class="fw-bold">${curr.title} Sequence:</h4>
      </div>

      <div class="card p-4 bg-light shadow-sm mb-4">
        <div class="row g-2 text-center align-items-center justify-content-center">
          ${curr.steps.map((s, idx) => `
            <div class="col-6 col-md-3">
              <div class="p-3 bg-white rounded-3 shadow-sm border h-100">
                <span class="badge bg-light text-dark mb-1">Step ${idx + 1}</span>
                <div class="fs-1 my-2"><i class="fa-solid ${s.icon}"></i></div>
                <div class="fw-bold fs-6">${s.name}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="text-center mb-3">
        <h4 class="fw-bold text-primary">${curr.question}</h4>
      </div>

      <div class="row g-3 justify-content-center">
        ${curr.options.map(opt => `
          <div class="col-12 col-md-6">
            <button class="btn game-option-btn w-100 p-3 fs-5" data-ans="${opt}">
              <span>${opt}</span>
            </button>
          </div>
        `).join('')}
      </div>
    `;

    const btns = this.container.querySelectorAll('.game-option-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const chosen = btn.dataset.ans;
        btns.forEach(b => b.disabled = true);

        if (chosen === curr.correct) {
          btn.classList.add('selected-correct');
          playTone('success');
          this.correctCount++;
        } else {
          btn.classList.add('selected-wrong');
          playTone('prompt');
        }

        setTimeout(() => {
          this.round++;
          this.renderRound();
        }, 1200);
      });
    });
  }

  async gameComplete() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    const accuracy = Math.round((this.correctCount / this.maxRounds) * 100);
    const score = Math.max(25, accuracy);

    const payload = {
      game_slug: 'routine-recall',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Daily Routine Recall', score, accuracy, elapsedSec, aiRes);
  }
}

/* ==========================================================================
   GAME 6: FAMILIAR PICTURE RECOGNITION (NER CULTURAL HERITAGE)
   ========================================================================== */
class PictureRecognitionGame {
  constructor(containerId, difficulty = 'EASY') {
    this.container = document.getElementById(containerId);
    this.difficulty = difficulty;
    this.round = 0;
    this.maxRounds = 3;
    this.correctCount = 0;
    this.startTime = Date.now();

    this.items = [
      {
        title: "Cultural Object",
        icon: "fa-umbrella",
        color: "text-warning",
        clue: "Traditional conical headgear made of woven bamboo and toku leaves, representing respect in Assam.",
        correct: "Japi (Traditional Hat)",
        options: ["Japi (Traditional Hat)", "Raincoat", "Cricket Helmet", "Metal Cooking Pot"]
      },
      {
        title: "Musical Heritage",
        icon: "fa-drum",
        color: "text-danger",
        clue: "Double-headed barrel drum played during the joyful spring Bihu celebrations.",
        correct: "Bihu Dhol (Drum)",
        options: ["Bihu Dhol (Drum)", "Electric Guitar", "Violin", "Piano"]
      },
      {
        title: "Sacred Tray",
        icon: "fa-trophy",
        color: "text-primary",
        clue: "Manufactured from bell-metal with an elevated stand, traditionally used for offering betel nuts and paan.",
        correct: "Xorai (Offering Vessel)",
        options: ["Xorai (Offering Vessel)", "Plastic Bottle", "Coffee Mug", "Suitcase"]
      }
    ];

    this.init();
  }

  init() {
    if (!this.container) return;
    this.round = 0;
    this.correctCount = 0;
    this.startTime = Date.now();
    this.renderRound();
  }

  renderRound() {
    if (this.round >= this.maxRounds) {
      this.gameComplete();
      return;
    }

    const curr = this.items[this.round];
    this.container.innerHTML = `
      <div class="text-center mb-3">
        <span class="badge bg-secondary fs-6 mb-2">Item ${this.round + 1} of ${this.maxRounds}</span>
        <h4 class="fw-bold">What is this familiar cultural item?</h4>
      </div>

      <div class="card p-4 text-center bg-light shadow-sm mb-4">
        <div class="display-1 my-3 ${curr.color}">
          <i class="fa-solid ${curr.icon}"></i>
        </div>
        <p class="fs-5 text-muted fst-italic px-3 mb-0">${curr.clue}</p>
      </div>

      <div class="row g-3 justify-content-center">
        ${curr.options.map(opt => `
          <div class="col-12 col-md-6">
            <button class="btn game-option-btn w-100 p-3 fs-5" data-opt="${opt}">
              <span>${opt}</span>
            </button>
          </div>
        `).join('')}
      </div>
    `;

    const btns = this.container.querySelectorAll('.game-option-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const chosen = btn.dataset.opt;
        btns.forEach(b => b.disabled = true);

        if (chosen === curr.correct) {
          btn.classList.add('selected-correct');
          playTone('success');
          this.correctCount++;
        } else {
          btn.classList.add('selected-wrong');
          playTone('prompt');
        }

        setTimeout(() => {
          this.round++;
          this.renderRound();
        }, 1200);
      });
    });
  }

  async gameComplete() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    const accuracy = Math.round((this.correctCount / this.maxRounds) * 100);
    const score = Math.max(25, accuracy);

    const payload = {
      game_slug: 'picture-recognition',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Picture Recognition', score, accuracy, elapsedSec, aiRes);
  }
}

/* ==========================================================================
   GAME 7: EMOTIONAL PERCEPTION & FEELINGS RECOGNITION
   ========================================================================== */
class EmotionGame {
  constructor(containerId, difficulty = 'EASY') {
    this.container = document.getElementById(containerId);
    this.difficulty = difficulty;
    this.round = 0;
    this.maxRounds = 3;
    this.correctCount = 0;
    this.startTime = Date.now();

    this.expressions = [
      {
        icon: "fa-face-smile text-success",
        question: "How does this friendly face feel?",
        correct: "Happy & Cheerful",
        options: ["Happy & Cheerful", "Angry", "Fearful", "Sleepy"]
      },
      {
        icon: "fa-face-meh text-info",
        question: "How does this person feel right now?",
        correct: "Calm & Peaceful",
        options: ["Calm & Peaceful", "Furious", "Shouting", "Crying"]
      },
      {
        icon: "fa-face-surprise text-warning",
        question: "What expression is this person showing?",
        correct: "Surprised & Curious",
        options: ["Surprised & Curious", "Asleep", "Bored", "Bitter"]
      }
    ];

    this.init();
  }

  init() {
    if (!this.container) return;
    this.round = 0;
    this.correctCount = 0;
    this.startTime = Date.now();
    this.renderRound();
  }

  renderRound() {
    if (this.round >= this.maxRounds) {
      this.gameComplete();
      return;
    }

    const curr = this.expressions[this.round];
    this.container.innerHTML = `
      <div class="text-center mb-3">
        <span class="badge bg-secondary fs-6 mb-2">Round ${this.round + 1} of ${this.maxRounds}</span>
        <h4 class="fw-bold">${curr.question}</h4>
      </div>

      <div class="card p-4 text-center bg-light shadow-sm mb-4">
        <div class="display-1 my-3">
          <i class="fa-solid ${curr.icon}"></i>
        </div>
        <p class="fs-5 text-muted mb-0">Look at the eyes and smile.</p>
      </div>

      <div class="row g-3 justify-content-center">
        ${curr.options.map(opt => `
          <div class="col-12 col-md-6">
            <button class="btn game-option-btn w-100 p-3 fs-5" data-ans="${opt}">
              <span>${opt}</span>
            </button>
          </div>
        `).join('')}
      </div>
    `;

    const btns = this.container.querySelectorAll('.game-option-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const chosen = btn.dataset.ans;
        btns.forEach(b => b.disabled = true);

        if (chosen === curr.correct) {
          btn.classList.add('selected-correct');
          playTone('success');
          this.correctCount++;
        } else {
          btn.classList.add('selected-wrong');
          playTone('prompt');
        }

        setTimeout(() => {
          this.round++;
          this.renderRound();
        }, 1200);
      });
    });
  }

  async gameComplete() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    const accuracy = Math.round((this.correctCount / this.maxRounds) * 100);
    const score = Math.max(25, accuracy);

    const payload = {
      game_slug: 'emotion-recognition',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Emotional Perception', score, accuracy, elapsedSec, aiRes);
  }
}

/* ==========================================================================
   GAME 8: FAMILY & LIFE RECALL (DYNAMICALLY GENERATED FROM MEMORY VAULT)
   ========================================================================== */
class FamilyRecallGame {
  constructor(containerId, difficulty = 'EASY') {
    this.container = document.getElementById(containerId);
    this.difficulty = difficulty;
    this.questions = [];
    this.round = 0;
    this.maxRounds = 3;
    this.correctCount = 0;
    this.startTime = Date.now();

    this.init();
  }

  async init() {
    if (!this.container) return;
    this.round = 0;
    this.correctCount = 0;
    this.startTime = Date.now();

    try {
      const resp = await fetch('/api/games/personal-questions');
      if (resp.ok) {
        const data = await resp.json();
        this.questions = data.questions || [];
      }
    } catch (e) {
      console.warn("Could not load personal questions:", e);
    }

    if (!this.questions || this.questions.length === 0) {
      this.questions = [
        {
          category: 'Family Member',
          question: "Who is your primary family caregiver and loving daughter?",
          clue: "Visits you every Sunday with homemade warm pitha.",
          image_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&auto=format&fit=crop&q=80',
          correct: 'Sunita Sharma (Daughter)',
          options: ['Sunita Sharma (Daughter)', 'Priya Devi (Niece)', 'Kavita Baruah (Neighbor)', 'Meera (Sister)']
        }
      ];
    }

    this.maxRounds = Math.min(this.questions.length, 4);
    this.renderRound();
  }

  renderRound() {
    if (this.round >= this.maxRounds) {
      this.gameComplete();
      return;
    }

    const curr = this.questions[this.round];
    this.container.innerHTML = `
      <div class="text-center mb-3">
        <span class="badge bg-danger fs-6 mb-2"><i class="fa-solid fa-heart me-1"></i> Personal Memory Question ${this.round + 1} of ${this.maxRounds}</span>
        <h3 class="fw-bold text-dark mb-1">${curr.question}</h3>
        <span class="badge bg-light text-primary border">${curr.category}</span>
      </div>

      <div class="card p-4 text-center bg-light shadow-sm mb-4 rounded-4 border-0">
        ${curr.image_url ? `
          <div class="mb-3">
            <img src="${curr.image_url}" alt="${curr.category}" class="rounded-circle shadow" style="width: 140px; height: 140px; object-fit: cover; border: 4px solid #ffffff;" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300';">
          </div>
        ` : `
          <div class="display-1 text-primary my-2"><i class="fa-solid ${curr.icon || 'fa-user-heart'}"></i></div>
        `}
        <p class="fs-5 text-secondary fst-italic mb-0">"${curr.clue}"</p>
      </div>

      <div class="row g-3 justify-content-center">
        ${curr.options.map(opt => `
          <div class="col-12 col-md-6">
            <button class="btn game-option-btn w-100 p-3 fs-5" data-opt="${opt}">
              <span>${opt}</span>
            </button>
          </div>
        `).join('')}
      </div>
    `;

    const btns = this.container.querySelectorAll('.game-option-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const chosen = btn.dataset.opt;
        btns.forEach(b => b.disabled = true);

        if (chosen === curr.correct) {
          btn.classList.add('selected-correct');
          playTone('success');
          this.correctCount++;
        } else {
          btn.classList.add('selected-wrong');
          playTone('prompt');
        }

        setTimeout(() => {
          this.round++;
          this.renderRound();
        }, 1200);
      });
    });
  }

  async gameComplete() {
    const elapsedSec = Math.max(1, Math.round((Date.now() - this.startTime) / 1000));
    const accuracy = Math.round((this.correctCount / this.maxRounds) * 100);
    const score = Math.max(25, accuracy);

    const payload = {
      game_slug: 'family-recall',
      score: score,
      accuracy: accuracy,
      completion_time: elapsedSec,
      attempts: 1,
      difficulty: this.difficulty
    };

    const aiRes = await submitGameResult(payload);
    showGameSummaryModal('Family & Life Recall', score, accuracy, elapsedSec, aiRes);
  }
}


