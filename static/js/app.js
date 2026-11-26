/**
 * Memora Application Coordinator.
 * Handles user interactions, input validation, simulation runs, comparison, and toast notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Preset definitions
  const PRESETS = {
    reference: {
      sequence: '7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1',
      frames: 3,
    },
    belady: {
      sequence: '1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5',
      frames: 3,
    },
    locality: {
      sequence: '1, 2, 1, 2, 3, 1, 2, 4, 5, 4, 5, 6, 7',
      frames: 3,
    },
    sequential: {
      sequence: '0, 1, 2, 3, 4, 5, 6, 7',
      frames: 3,
    },
  };

  const ALGO_DESCRIPTIONS = {
    'FIFO': '<strong>FIFO (First In, First Out):</strong> Replaces the memory page that was loaded earliest. Simple queue discipline; susceptible to Bélády\'s anomaly.',
    'LRU': '<strong>LRU (Least Recently Used):</strong> Replaces the page not referenced for the longest time in the past. Exploits temporal locality of reference.',
    'Optimal': '<strong>Optimal (Bélády\'s Algorithm):</strong> Replaces the page whose next reference occurs farthest in the future. Serves as a theoretical upper bound benchmark.',
  };

  // DOM Elements
  const sequenceInput = document.getElementById('page-sequence-input');
  const sequenceError = document.getElementById('sequence-error');
  const frameInput = document.getElementById('frame-count-input');
  const frameBadge = document.getElementById('frame-count-badge');
  const btnFrameDec = document.getElementById('btn-frame-dec');
  const btnFrameInc = document.getElementById('btn-frame-inc');
  const btnRandom = document.getElementById('btn-random-sequence');
  const btnRun = document.getElementById('btn-run-simulation');
  const btnCompare = document.getElementById('btn-compare-all');
  const btnResetVis = document.getElementById('btn-reset-vis');
  const algoRadios = document.querySelectorAll('input[name="algorithm"]');
  const algoBadge = document.getElementById('current-algo-badge');
  const algoDesc = document.getElementById('algo-description-text');
  const backendStatus = document.getElementById('backend-status');
  const toastContainer = document.getElementById('toast-container');

  // Metrics elements
  const valTotalPages = document.getElementById('val-total-pages');
  const valHits = document.getElementById('val-hits');
  const valFaults = document.getElementById('val-faults');
  const subHitRatio = document.getElementById('sub-hit-ratio');
  const subFaultRatio = document.getElementById('sub-fault-ratio');
  const valHitPct = document.getElementById('val-hit-percentage');
  const valFaultPct = document.getElementById('val-fault-percentage');
  const barHit = document.getElementById('bar-hit-ratio');
  const barFault = document.getElementById('bar-fault-ratio');

  // Playback control buttons
  const btnPlayPause = document.getElementById('btn-play-pause');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnFirst = document.getElementById('btn-first');
  const btnLast = document.getElementById('btn-last');
  const speedBtns = document.querySelectorAll('.btn-speed');

  // Comparison section elements
  const compSection = document.getElementById('comparison-section');
  const compTableBody = document.getElementById('comparison-table-body');
  const winnerName = document.getElementById('winner-name');
  const winnerFaults = document.getElementById('winner-faults');
  const chartFaultsCanvas = document.getElementById('chart-faults-canvas');
  const chartRatiosCanvas = document.getElementById('chart-ratios-canvas');
  const compOutdatedBanner = document.getElementById('comp-outdated-banner');
  const simOutdatedBanner = document.getElementById('sim-outdated-banner');

  // Track state of the last executed simulation to detect pending input changes
  let lastSimulatedSequence = null;
  let lastSimulatedFrames = null;
  let lastSimulatedAlgo = null;

  // Track state of the last executed comparison to ensure synchronization
  let currentComparisonData = null;
  let lastComparedSequence = null;
  let lastComparedFrames = null;

  // Initialize Visualizer module
  MemoraVisualizer.init();

  // 1. Check Backend Connectivity
  checkBackend();

  // 2. Setup Event Listeners
  setupEventListeners();

  // 3. Initial Run on Reference Case for immediate visualization
  runSimulation();

  /**
   * Check backend health and update status pill.
   */
  async function checkBackend() {
    const res = await MemoraAPI.checkHealth();
    if (res.ok) {
      backendStatus.className = 'status-indicator online';
      backendStatus.querySelector('.status-label').textContent = 'Backend Online';
      backendStatus.title = 'Flask REST API connected';
    } else {
      backendStatus.className = 'status-indicator offline';
      backendStatus.querySelector('.status-label').textContent = 'Backend Offline';
      backendStatus.title = res.error;
    }
  }

  /**
   * Attach all interactive DOM event listeners.
   */
  function setupEventListeners() {
    // Algorithm radio selection
    algoRadios.forEach(radio => {
      radio.addEventListener('change', (e) => {
        const val = e.target.value;
        algoBadge.textContent = val;
        algoDesc.innerHTML = ALGO_DESCRIPTIONS[val] || '';

        // Update active class on label wrappers
        document.querySelectorAll('.algo-option').forEach(opt => {
          opt.classList.toggle('active', opt.getAttribute('data-algo') === val);
        });

        // Trigger simulation run with newly selected algorithm
        runSimulation();
      });
    });

    // Preset chips
    document.querySelectorAll('.btn-preset').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const presetKey = btn.getAttribute('data-preset');
        const p = PRESETS[presetKey];
        if (p) {
          sequenceInput.value = p.sequence;
          setFrameCount(p.frames);
          clearInputError();
          markComparisonOutdated();
          runSimulation();
        }
      });
    });

    // Random sequence generator
    btnRandom.addEventListener('click', () => {
      const length = Math.floor(Math.random() * 6) + 15; // 15 to 20 numbers
      const randomSeq = [];
      for (let i = 0; i < length; i++) {
        randomSeq.push(Math.floor(Math.random() * 8)); // pages 0 to 7
      }
      sequenceInput.value = randomSeq.join(', ');
      clearInputError();
      markComparisonOutdated();

      document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
      showToast(`Generated random sequence of ${length} pages.`, 'info');
      runSimulation();
    });

    // Frame stepper controls
    btnFrameDec.addEventListener('click', () => {
      const cur = parseInt(frameInput.value, 10) || 3;
      if (cur > 1) {
        setFrameCount(cur - 1);
        runSimulation();
      }
    });

    btnFrameInc.addEventListener('click', () => {
      const cur = parseInt(frameInput.value, 10) || 3;
      if (cur < 8) {
        setFrameCount(cur + 1);
        runSimulation();
      }
    });

    frameInput.addEventListener('change', () => {
      let val = parseInt(frameInput.value, 10);
      if (isNaN(val) || val < 1) val = 1;
      if (val > 8) val = 8;
      setFrameCount(val);
      runSimulation();
    });

    // Frame preset chips
    document.querySelectorAll('.chip-frame').forEach(chip => {
      chip.addEventListener('click', () => {
        const val = parseInt(chip.getAttribute('data-frames'), 10);
        setFrameCount(val);
        runSimulation();
      });
    });

    // Run Simulation button
    btnRun.addEventListener('click', () => {
      runSimulation();
    });

    // Compare Algorithms button
    btnCompare.addEventListener('click', () => {
      compareAlgorithms();
    });

    // Playback control buttons
    btnPlayPause.addEventListener('click', () => {
      MemoraVisualizer.togglePlay();
    });

    btnPrev.addEventListener('click', () => {
      MemoraVisualizer.pause();
      MemoraVisualizer.prev();
    });

    btnNext.addEventListener('click', () => {
      MemoraVisualizer.pause();
      MemoraVisualizer.next();
    });

    btnFirst.addEventListener('click', () => {
      MemoraVisualizer.first();
    });

    btnLast.addEventListener('click', () => {
      MemoraVisualizer.last();
    });

    btnResetVis.addEventListener('click', () => {
      MemoraVisualizer.reset();
      showToast('Visualizer reset to Step 0.', 'info');
    });

    // Speed selector
    speedBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        speedBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const speedMs = parseInt(btn.getAttribute('data-speed'), 10);
        MemoraVisualizer.setSpeed(speedMs);
      });
    });

    // Keyboard Shortcuts (Left, Right, Space)
    document.addEventListener('keydown', (e) => {
      // Ignore if user is currently typing inside an input or textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        MemoraVisualizer.togglePlay();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        MemoraVisualizer.pause();
        MemoraVisualizer.prev();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        MemoraVisualizer.pause();
        MemoraVisualizer.next();
      }
    });

    // Clear error on input and mark simulation / comparison outdated if modified
    sequenceInput.addEventListener('input', () => {
      clearInputError();
      markSimulationOutdated();
      markComparisonOutdated();
    });
  }

  /**
   * Set physical memory frame count safely.
   */
  function setFrameCount(count) {
    frameInput.value = count;
    frameBadge.textContent = `${count} Frames`;

    document.querySelectorAll('.chip-frame').forEach(chip => {
      chip.classList.toggle('active', parseInt(chip.getAttribute('data-frames'), 10) === count);
    });
    markSimulationOutdated();
    markComparisonOutdated();
  }

  /**
   * Parse and validate page sequence input.
   * Returns array of integers or null if invalid.
   */
  function parsePageSequence() {
    const raw = sequenceInput.value.trim();
    if (!raw) {
      showInputError('Page reference sequence cannot be empty.');
      return null;
    }

    // Split by comma or whitespace
    const tokens = raw.split(/[\s,]+/).filter(t => t.length > 0);
    if (tokens.length === 0) {
      showInputError('Please enter at least one page number.');
      return null;
    }

    const sequence = [];
    for (let i = 0; i < tokens.length; i++) {
      const num = Number(tokens[i]);
      if (!Number.isInteger(num)) {
        showInputError(`Invalid page '${tokens[i]}' at position ${i + 1}: page numbers must be integers.`);
        return null;
      }
      if (num < 0) {
        showInputError(`Invalid page '${tokens[i]}' at position ${i + 1}: page numbers must be non-negative (>= 0).`);
        return null;
      }
      sequence.push(num);
    }

    clearInputError();
    return sequence;
  }

  function showInputError(msg) {
    sequenceError.textContent = msg;
    sequenceError.style.display = 'block';
  }

  function clearInputError() {
    sequenceError.textContent = '';
    sequenceError.style.display = 'none';
  }

  function getSelectedAlgorithm() {
    const checked = document.querySelector('input[name="algorithm"]:checked');
    return checked ? checked.value : 'FIFO';
  }

  /**
   * Execute single simulation flow.
   */
  async function runSimulation() {
    const sequence = parsePageSequence();
    if (!sequence) return;

    const frames = parseInt(frameInput.value, 10);
    if (isNaN(frames) || frames < 1 || frames > 8) {
      showToast('Frame count must be an integer between 1 and 8.', 'error');
      return;
    }

    const algo = getSelectedAlgorithm();

    // Dismiss lingering completion toasts so user does not see stale completion info
    document.querySelectorAll('.toast-success').forEach(t => t.remove());

    // Disable action buttons during fetch
    setButtonsLoading(true);

    try {
      const res = await MemoraAPI.simulate(sequence, frames, algo);

      if (!res.ok) {
        showToast(res.error, 'error');
        return;
      }

      const data = res.data;

      // Update KPI Metrics Cards
      valTotalPages.textContent = data.total_pages;
      valHits.textContent = data.hits;
      valFaults.textContent = data.faults;

      const hitPct = (data.hit_ratio * 100).toFixed(1);
      const faultPct = (data.fault_ratio * 100).toFixed(1);

      subHitRatio.textContent = `Hit Ratio: ${(data.hit_ratio * 100).toFixed(2)}%`;
      subFaultRatio.textContent = `Fault Ratio: ${(data.fault_ratio * 100).toFixed(2)}%`;

      valHitPct.textContent = `${hitPct}%`;
      valFaultPct.textContent = `${faultPct}%`;

      barHit.style.width = `${hitPct}%`;
      barFault.style.width = `${faultPct}%`;

      // Load data into Memory Visualizer
      MemoraVisualizer.load(data);

      // Track last successfully simulated state and clear outdated banner
      lastSimulatedSequence = sequenceInput.value.trim();
      lastSimulatedFrames = frames;
      lastSimulatedAlgo = algo;
      clearSimulationOutdated();

      showToast(`Simulation complete: ${data.algorithm} (${data.faults} faults, ${data.hits} hits).`, 'success');
    } catch (e) {
      showToast('An unexpected client error occurred while running the simulation.', 'error');
    } finally {
      setButtonsLoading(false);
    }
  }

  /**
   * Mark main simulation display as outdated when input sequence or frames change.
   */
  function markSimulationOutdated() {
    if (!lastSimulatedSequence) return;
    const currentSeq = sequenceInput.value.trim();
    const currentFrames = parseInt(frameInput.value, 10);
    const isDifferent = (currentSeq !== lastSimulatedSequence) || (currentFrames !== lastSimulatedFrames);

    if (simOutdatedBanner) {
      simOutdatedBanner.style.display = isDifferent ? 'flex' : 'none';
    }
  }

  /**
   * Clear simulation outdated banner.
   */
  function clearSimulationOutdated() {
    if (simOutdatedBanner) {
      simOutdatedBanner.style.display = 'none';
    }
  }

  /**
   * Mark comparison section as outdated when inputs change.
   */
  function markComparisonOutdated() {
    if (!currentComparisonData || !compSection || compSection.style.display === 'none') {
      return;
    }
    const currentSeq = sequenceInput.value.trim();
    const currentFrames = parseInt(frameInput.value, 10);
    const isDifferent = (currentSeq !== lastComparedSequence) || (currentFrames !== lastComparedFrames);

    if (isDifferent) {
      if (compOutdatedBanner) compOutdatedBanner.style.display = 'flex';
      compSection.classList.add('is-outdated');
    } else {
      if (compOutdatedBanner) compOutdatedBanner.style.display = 'none';
      compSection.classList.remove('is-outdated');
    }
  }

  /**
   * Clear outdated banner and status.
   */
  function clearComparisonOutdated() {
    if (compOutdatedBanner) compOutdatedBanner.style.display = 'none';
    if (compSection) compSection.classList.remove('is-outdated');
  }

  /**
   * Render comparison table, winner badge, and charts atomically from comparison data.
   */
  function renderComparisonUI(data) {
    if (!data) return;

    const resultsMap = data.results;
    const summary = data.summary;

    // Reveal comparison section
    compSection.style.display = 'block';

    // Update winner badge
    const bestAlgos = summary.best_algorithms || ['Optimal'];
    const bestAlgo = summary.best_algorithm || 'Optimal';
    const fewestFaults = summary.fewest_faults;
    const isTie = bestAlgos.length > 1;

    const winnerBadgeEl = document.getElementById('winner-badge');
    if (winnerBadgeEl) {
      if (isTie) {
        winnerBadgeEl.innerHTML = `🤝 Tied: <span id="winner-name">${bestAlgo}</span> (<span id="winner-faults">${fewestFaults}</span> Faults)`;
      } else {
        winnerBadgeEl.innerHTML = `🏆 Best: <span id="winner-name">${bestAlgo}</span> (<span id="winner-faults">${fewestFaults}</span> Faults)`;
      }
    }

    // Build comparison table
    let tableHtml = '';
    const algos = ['FIFO', 'LRU', 'OPTIMAL'];
    const algoType = { 'FIFO': 'Practical (Queue)', 'LRU': 'Practical (Locality)', 'OPTIMAL': 'Theoretical Upper Bound' };

    algos.forEach(key => {
      const item = resultsMap[key];
      if (!item) return;

      const isBest = item.faults === fewestFaults;
      const diff = item.faults - fewestFaults;
      let diffText;
      if (isBest) {
        diffText = isTie ? '<span class="pill-hit">Tied Winner</span>' : '<span class="pill-hit">Best Result</span>';
      } else {
        diffText = `+${diff} faults`;
      }

      tableHtml += `
        <tr class="${isBest ? 'best-algo-row' : ''}">
          <td><strong>${item.algorithm}</strong></td>
          <td><span class="algo-tag">${algoType[key] || 'Standard'}</span></td>
          <td><strong class="text-fault">${item.faults}</strong></td>
          <td><strong class="text-hit">${item.hits}</strong></td>
          <td>${(item.fault_ratio * 100).toFixed(2)}%</td>
          <td>${(item.hit_ratio * 100).toFixed(2)}%</td>
          <td>${diffText}</td>
        </tr>
      `;
    });

    compTableBody.innerHTML = tableHtml;

    // Render Canvas Charts atomically
    MemoraCharts.renderFaultsHitsChart(chartFaultsCanvas, resultsMap);
    MemoraCharts.renderHitRatioChart(chartRatiosCanvas, resultsMap);
  }

  /**
   * Execute algorithm comparison flow.
   */
  async function compareAlgorithms() {
    const sequence = parsePageSequence();
    if (!sequence) return;

    const frames = parseInt(frameInput.value, 10);
    if (isNaN(frames) || frames < 1 || frames > 8) {
      showToast('Frame count must be an integer between 1 and 8.', 'error');
      return;
    }

    const algo = getSelectedAlgorithm();

    // Dismiss lingering completion toasts so user does not see stale completion info
    document.querySelectorAll('.toast-success').forEach(t => t.remove());

    setButtonsLoading(true);

    try {
      const res = await MemoraAPI.compare(sequence, frames);

      if (!res.ok) {
        showToast(res.error, 'error');
        return;
      }

      // Cache comparison data and record the inputs used
      currentComparisonData = res.data;
      lastComparedSequence = sequenceInput.value.trim();
      lastComparedFrames = frames;
      clearComparisonOutdated();

      renderComparisonUI(res.data);

      // Smooth scroll to comparison section
      compSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

      const summary = res.data.summary;
      const isTie = (summary.best_algorithms || []).length > 1;
      const bestAlgo = summary.best_algorithm || 'Optimal';
      const fewestFaults = summary.fewest_faults;

      if (isTie) {
        showToast(`Comparison complete: Algorithms tied (${bestAlgo}) with ${fewestFaults} faults.`, 'info');
      } else {
        showToast(`Comparison complete: Best algorithm is ${bestAlgo} with ${fewestFaults} faults.`, 'success');
      }
    } catch (e) {
      showToast('An unexpected client error occurred during comparison.', 'error');
    } finally {
      setButtonsLoading(false);
    }
  }

  function setButtonsLoading(isLoading) {
    btnRun.disabled = isLoading;
    btnCompare.disabled = isLoading;
    if (isLoading) {
      btnRun.style.opacity = '0.6';
      btnCompare.style.opacity = '0.6';
    } else {
      btnRun.style.opacity = '1';
      btnCompare.style.opacity = '1';
    }
  }

  /**
   * Display floating toast notification with stacking prevention.
   */
  function showToast(message, type = 'info') {
    if (!toastContainer) return;

    // Prevent excessive notification stacking (keep at most 2 active toasts)
    while (toastContainer.children.length >= 2) {
      toastContainer.firstChild.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 300ms ease';
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  // Window resize: re-draw canvas charts from cached comparison data (zero network requests, zero desync)
  let resizeTimer = null;
  window.addEventListener('resize', () => {
    if (compSection && compSection.style.display !== 'none' && currentComparisonData && currentComparisonData.results) {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        MemoraCharts.renderFaultsHitsChart(chartFaultsCanvas, currentComparisonData.results);
        MemoraCharts.renderHitRatioChart(chartRatiosCanvas, currentComparisonData.results);
      }, 100);
    }
  });

});
