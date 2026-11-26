/**
 * Memora Visualizer & Step-by-Step Controller Module.
 * Renders the hardware memory frame rack and coordinates step-by-step playback.
 */

const MemoraVisualizer = (() => {
  let simulationHistory = [];
  let frameCount = 3;
  let currentStep = 0;
  let isPlaying = false;
  let playInterval = 800; // ms
  let timerId = null;

  // DOM Elements cache
  let rackEl = null;
  let sliderEl = null;
  let counterEl = null;
  let pageBadgeEl = null;
  let statusTagEl = null;
  let actionDescEl = null;
  let playBtnLabel = null;
  let playBtnIcon = null;
  let historyBodyEl = null;
  let historyHeaderEl = null;
  let tableContainerEl = null;
  let btnPrev = null;
  let btnNext = null;
  let btnFirst = null;
  let btnLast = null;

  function init() {
    rackEl = document.getElementById('memory-frames-rack');
    sliderEl = document.getElementById('timeline-slider');
    counterEl = document.getElementById('step-counter-text');
    pageBadgeEl = document.getElementById('step-current-page');
    statusTagEl = document.getElementById('step-status-tag');
    actionDescEl = document.getElementById('step-action-desc');
    playBtnLabel = document.getElementById('play-pause-label');
    playBtnIcon = document.getElementById('play-pause-icon');
    historyBodyEl = document.getElementById('history-table-body');
    historyHeaderEl = document.getElementById('history-table-header');
    tableContainerEl = document.getElementById('history-table-container');

    btnPrev = document.getElementById('btn-prev');
    btnNext = document.getElementById('btn-next');
    btnFirst = document.getElementById('btn-first');
    btnLast = document.getElementById('btn-last');

    // Slider scrubbing
    if (sliderEl) {
      sliderEl.addEventListener('input', (e) => {
        pause();
        const step = parseInt(e.target.value, 10);
        renderStep(step);
      });
    }
  }

  /**
   * Load new simulation results into visualizer.
   */
  function load(result) {
    pause();

    simulationHistory = result.history || [];
    frameCount = result.frame_count || 3;
    currentStep = 0;

    // Update timeline scrubber
    if (sliderEl) {
      sliderEl.min = 0;
      sliderEl.max = Math.max(0, simulationHistory.length - 1);
      sliderEl.value = 0;
    }

    const maxLabel = document.getElementById('timeline-max-label');
    if (maxLabel) {
      maxLabel.textContent = `Step ${Math.max(0, simulationHistory.length - 1)}`;
    }

    // Build History Table Header & Rows
    buildHistoryTable();

    // Render initial step (Step 0)
    renderStep(0);
  }

  /**
   * Build the step-by-step history trace table.
   */
  function buildHistoryTable() {
    if (!historyHeaderEl || !historyBodyEl) return;

    // Build Header based on frameCount
    let headerHtml = '<th>Step</th><th>Page</th>';
    for (let f = 0; f < frameCount; f++) {
      headerHtml += `<th>Frame ${f}</th>`;
    }
    headerHtml += '<th>Outcome</th><th>Evicted</th>';
    historyHeaderEl.innerHTML = headerHtml;

    // Build Rows
    let rowsHtml = '';
    simulationHistory.forEach((step, idx) => {
      const isHit = step.is_hit;
      const statusClass = isHit ? 'pill-hit' : 'pill-fault';
      const statusText = isHit ? 'HIT' : 'FAULT';
      const evictedText = (step.evicted !== null && step.evicted !== undefined) ? step.evicted : '-';

      let framesCols = '';
      for (let f = 0; f < frameCount; f++) {
        const pageVal = (step.frames && f < step.frames.length && step.frames[f] !== null)
          ? step.frames[f]
          : '-';
        framesCols += `<td>${pageVal}</td>`;
      }

      rowsHtml += `
        <tr id="history-row-${idx}" data-step="${idx}">
          <td><strong>#${step.step}</strong></td>
          <td><span class="badge">${step.page}</span></td>
          ${framesCols}
          <td><span class="${statusClass}">${statusText}</span></td>
          <td>${evictedText}</td>
        </tr>
      `;
    });

    historyBodyEl.innerHTML = rowsHtml;

    // Row click listeners to jump to step
    const rows = historyBodyEl.querySelectorAll('tr');
    rows.forEach(row => {
      row.addEventListener('click', () => {
        pause();
        const stepIdx = parseInt(row.getAttribute('data-step'), 10);
        renderStep(stepIdx);
      });
    });
  }

  /**
   * Render a specific simulation step in the memory rack and UI.
   */
  function renderStep(index) {
    if (!simulationHistory || simulationHistory.length === 0) return;

    // Bound check
    if (index < 0) index = 0;
    if (index >= simulationHistory.length) index = simulationHistory.length - 1;
    currentStep = index;

    const step = simulationHistory[currentStep];
    const prevStep = currentStep > 0 ? simulationHistory[currentStep - 1] : null;

    // 1. Update Counters & Header
    if (counterEl) {
      counterEl.textContent = `Step ${currentStep} / ${simulationHistory.length - 1}`;
    }
    if (pageBadgeEl) {
      pageBadgeEl.textContent = step.page;
    }
    if (sliderEl) {
      sliderEl.value = currentStep;
    }

    // 2. Outcome Badge & Description
    if (statusTagEl && actionDescEl) {
      if (step.is_hit) {
        statusTagEl.textContent = 'HIT';
        statusTagEl.className = 'badge-status status-hit';
        actionDescEl.textContent = `Page ${step.page} already in physical memory`;
      } else {
        statusTagEl.textContent = 'FAULT';
        statusTagEl.className = 'badge-status status-fault';
        if (step.evicted !== null && step.evicted !== undefined) {
          actionDescEl.textContent = `Memory full: Evicted Page ${step.evicted} to load Page ${step.page}`;
        } else {
          actionDescEl.textContent = `Empty frame available: Loaded Page ${step.page}`;
        }
      }
    }

    // 3. Render Physical Memory Frame Slots
    if (rackEl) {
      let rackHtml = '';
      const frames = step.frames || [];

      for (let f = 0; f < frameCount; f++) {
        const pageVal = (f < frames.length && frames[f] !== null) ? frames[f] : null;
        let slotClass = 'frame-slot';
        let stateTagText = '';

        if (pageVal !== null) {
          if (step.is_hit && pageVal === step.page) {
            slotClass += ' is-hit';
            stateTagText = 'PAGE HIT';
          } else if (!step.is_hit) {
            // Check if this slot was modified in this step
            const prevVal = (prevStep && prevStep.frames && f < prevStep.frames.length) ? prevStep.frames[f] : null;
            if (prevVal !== pageVal && pageVal === step.page) {
              if (step.evicted !== null && step.evicted !== undefined) {
                slotClass += ' is-evicted';
                stateTagText = `REPLACED P${step.evicted}`;
              } else {
                slotClass += ' is-loaded';
                stateTagText = 'NEWLY LOADED';
              }
            }
          }
        }

        const valueDisplay = pageVal !== null
          ? `<div class="frame-value">${pageVal}</div>`
          : `<div class="frame-empty">[ EMPTY ]</div>`;

        rackHtml += `
          <div class="${slotClass}">
            <div class="frame-slot-header">Frame ${f}</div>
            ${valueDisplay}
            <div class="frame-state-tag">${stateTagText}</div>
          </div>
        `;
      }

      rackEl.innerHTML = rackHtml;
    }

    // 4. Update History Table Row Selection
    if (historyBodyEl) {
      const activeRows = historyBodyEl.querySelectorAll('.active-step-row');
      activeRows.forEach(r => r.classList.remove('active-step-row'));

      const targetRow = document.getElementById(`history-row-${currentStep}`);
      if (targetRow) {
        targetRow.classList.add('active-step-row');
        // Scroll into view within container
        if (tableContainerEl) {
          const rowTop = targetRow.offsetTop;
          const containerScroll = tableContainerEl.scrollTop;
          const containerH = tableContainerEl.clientHeight;

          if (rowTop < containerScroll || rowTop > containerScroll + containerH - 60) {
            tableContainerEl.scrollTop = Math.max(0, rowTop - 70);
          }
        }
      }
    }

    // 5. Update Control Buttons State
    if (btnFirst) btnFirst.disabled = currentStep === 0;
    if (btnPrev) btnPrev.disabled = currentStep === 0;
    if (btnNext) btnNext.disabled = currentStep === simulationHistory.length - 1;
    if (btnLast) btnLast.disabled = currentStep === simulationHistory.length - 1;
  }

  function next() {
    if (currentStep < simulationHistory.length - 1) {
      renderStep(currentStep + 1);
    } else {
      pause();
    }
  }

  function prev() {
    if (currentStep > 0) {
      renderStep(currentStep - 1);
    }
  }

  function first() {
    pause();
    renderStep(0);
  }

  function last() {
    pause();
    renderStep(simulationHistory.length - 1);
  }

  function play() {
    if (isPlaying) return;
    if (currentStep >= simulationHistory.length - 1) {
      renderStep(0); // loop from beginning if at end
    }

    isPlaying = true;
    if (playBtnIcon) playBtnIcon.textContent = '⏸';
    if (playBtnLabel) playBtnLabel.textContent = 'Pause';

    timerId = setInterval(() => {
      if (currentStep < simulationHistory.length - 1) {
        next();
      } else {
        pause();
      }
    }, playInterval);
  }

  function pause() {
    if (!isPlaying && timerId === null) return;
    isPlaying = false;
    if (timerId !== null) {
      clearInterval(timerId);
      timerId = null;
    }
    if (playBtnIcon) playBtnIcon.textContent = '▶';
    if (playBtnLabel) playBtnLabel.textContent = 'Play';
  }

  function togglePlay() {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }

  function setSpeed(ms) {
    playInterval = ms;
    if (isPlaying) {
      pause();
      play();
    }
  }

  function reset() {
    pause();
    renderStep(0);
  }

  return {
    init,
    load,
    renderStep,
    next,
    prev,
    first,
    last,
    play,
    pause,
    togglePlay,
    setSpeed,
    reset,
    getCurrentStep: () => currentStep,
    isPlaying: () => isPlaying,
  };
})();

window.MemoraVisualizer = MemoraVisualizer;
