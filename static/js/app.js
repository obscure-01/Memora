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

  // ==========================================================================
  // TOP-LEVEL MODULE NAVIGATION CONTROLLER
  // ==========================================================================

  const moduleTabs = document.querySelectorAll('.module-tab-btn');
  const moduleContents = document.querySelectorAll('.module-tab-content');

  moduleTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetModule = tab.dataset.module;
      moduleTabs.forEach(t => {
        const isActive = (t === tab);
        t.classList.toggle('active', isActive);
        t.setAttribute('aria-selected', isActive ? 'true' : 'false');
      });
      moduleContents.forEach(content => {
        const matches = (content.id === `module-${targetModule}`);
        content.classList.toggle('active', matches);
        content.style.display = matches ? 'block' : 'none';
      });
    });
  });

  // ==========================================================================
  // MODULE 2: CPU SCHEDULING CONTROLLER
  // ==========================================================================

  const CPU_PRESETS = {
    'staggered': [
      { id: 'P1', arrival_time: 0, burst_time: 5 },
      { id: 'P2', arrival_time: 1, burst_time: 3 },
      { id: 'P3', arrival_time: 2, burst_time: 8 },
      { id: 'P4', arrival_time: 3, burst_time: 6 }
    ],
    'simultaneous': [
      { id: 'P1', arrival_time: 0, burst_time: 4 },
      { id: 'P2', arrival_time: 0, burst_time: 3 },
      { id: 'P3', arrival_time: 0, burst_time: 1 },
      { id: 'P4', arrival_time: 0, burst_time: 2 }
    ],
    'idle-gap': [
      { id: 'P1', arrival_time: 0, burst_time: 2 },
      { id: 'P2', arrival_time: 5, burst_time: 3 },
      { id: 'P3', arrival_time: 6, burst_time: 2 }
    ],
    'convoy': [
      { id: 'P1', arrival_time: 0, burst_time: 24 },
      { id: 'P2', arrival_time: 1, burst_time: 3 },
      { id: 'P3', arrival_time: 2, burst_time: 3 }
    ]
  };

  const CPU_ALGO_DESCRIPTIONS = {
    'FCFS': '<strong>FCFS (First-Come First-Served):</strong> Non-preemptive scheduling in order of process arrival. Simple queue discipline; susceptible to the Convoy Effect.',
    'SJF': '<strong>SJF (Shortest Job First):</strong> Non-preemptive scheduling selecting the process with minimal CPU burst. Mathematically minimizes Average Waiting Time (AWT).',
    'RR': '<strong>Round Robin (RR):</strong> Preemptive time-slicing using quantum q. Ensures fair CPU allocation and optimal interactive response time.'
  };

  const PID_COLORS = [
    '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6',
    '#ec4899', '#06b6d4', '#14b8a6', '#f97316'
  ];

  let currentCpuProcesses = JSON.parse(JSON.stringify(CPU_PRESETS['staggered']));
  const processTableBody = document.getElementById('process-table-body');
  const btnAddProcess = document.getElementById('btn-add-process');
  const cpuAlgoRadios = document.querySelectorAll('input[name="cpu-algorithm"]');
  const cpuAlgoBadge = document.getElementById('cpu-algo-badge');
  const cpuAlgoDesc = document.getElementById('cpu-algo-desc');
  const tqInput = document.getElementById('cpu-time-quantum');
  const tqBadge = document.getElementById('tq-badge');
  const btnTqDec = document.getElementById('btn-tq-dec');
  const btnTqInc = document.getElementById('btn-tq-inc');
  const btnRunCpu = document.getElementById('btn-run-cpu');
  const btnCompareCpu = document.getElementById('btn-compare-cpu');
  const btnResetCpu = document.getElementById('btn-reset-cpu');
  const cpuPresetBtns = document.querySelectorAll('[data-cpu-preset]');

  function markCpuOutdated() {
    const ganttBadge = document.getElementById('cpu-gantt-badge');
    if (ganttBadge) {
      ganttBadge.textContent = 'Workload Modified — Run to Refresh';
      ganttBadge.className = 'badge badge-warning';
    }
    const wrapper = document.getElementById('gantt-chart-wrapper');
    if (wrapper) wrapper.style.opacity = '0.65';
    const resTable = document.getElementById('cpu-results-table');
    if (resTable) resTable.style.opacity = '0.65';
    const compSec = document.getElementById('cpu-comparison-section');
    if (compSec) compSec.style.display = 'none';
  }

  function clearCpuOutdated() {
    const ganttBadge = document.getElementById('cpu-gantt-badge');
    if (ganttBadge) {
      ganttBadge.textContent = 'Timeline';
      ganttBadge.className = 'badge';
    }
    const wrapper = document.getElementById('gantt-chart-wrapper');
    if (wrapper) wrapper.style.opacity = '1';
    const resTable = document.getElementById('cpu-results-table');
    if (resTable) resTable.style.opacity = '1';
  }

  function getSelectedCpuAlgorithm() {
    const checked = document.querySelector('input[name="cpu-algorithm"]:checked');
    return checked ? checked.value : 'FCFS';
  }

  function renderProcessInputTable() {
    if (!processTableBody) return;
    processTableBody.innerHTML = '';
    currentCpuProcesses.forEach((p, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><input type="text" class="input-cell pid-input" value="${p.id}" style="width: 55px; padding: 4px; border-radius: 4px; background: #1f2937; color: #fff; border: 1px solid #374151;"></td>
        <td><input type="number" min="0" class="input-cell at-input" value="${p.arrival_time}" style="width: 55px; padding: 4px; border-radius: 4px; background: #1f2937; color: #fff; border: 1px solid #374151;"></td>
        <td><input type="number" min="1" class="input-cell bt-input" value="${p.burst_time}" style="width: 55px; padding: 4px; border-radius: 4px; background: #1f2937; color: #fff; border: 1px solid #374151;"></td>
        <td><button class="btn btn-sm btn-delete-proc" data-idx="${idx}" style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 2px 6px; border-radius: 4px; cursor: pointer;">✕</button></td>
      `;
      processTableBody.appendChild(tr);
    });

    // Attach input listeners to cells for live change detection
    document.querySelectorAll('.pid-input, .at-input, .bt-input').forEach(input => {
      input.addEventListener('input', () => {
        markCpuOutdated();
      });
    });

    // Delete buttons
    document.querySelectorAll('.btn-delete-proc').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const idx = parseInt(e.target.dataset.idx, 10);
        if (currentCpuProcesses.length <= 1) {
          showToast('At least one process is required.', 'error');
          return;
        }
        currentCpuProcesses.splice(idx, 1);
        renderProcessInputTable();
        markCpuOutdated();
      });
    });
  }

  function syncProcessesFromInputTable() {
    const pids = document.querySelectorAll('.pid-input');
    const ats = document.querySelectorAll('.at-input');
    const bts = document.querySelectorAll('.bt-input');
    const parsed = [];
    for (let i = 0; i < pids.length; i++) {
      const pid = pids[i].value.trim() || `P${i + 1}`;
      const at = Math.max(0, parseInt(ats[i].value, 10) || 0);
      const bt = Math.max(1, parseInt(bts[i].value, 10) || 1);
      parsed.push({ id: pid, arrival_time: at, burst_time: bt });
    }
    currentCpuProcesses = parsed;
    return parsed;
  }

  if (btnAddProcess) {
    btnAddProcess.addEventListener('click', () => {
      syncProcessesFromInputTable();
      const nextId = `P${currentCpuProcesses.length + 1}`;
      const lastAt = currentCpuProcesses.length > 0 ? currentCpuProcesses[currentCpuProcesses.length - 1].arrival_time + 1 : 0;
      currentCpuProcesses.push({ id: nextId, arrival_time: lastAt, burst_time: 4 });
      renderProcessInputTable();
      markCpuOutdated();
    });
  }

  cpuPresetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      cpuPresetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetKey = btn.dataset.cpuPreset;
      if (CPU_PRESETS[presetKey]) {
        currentCpuProcesses = JSON.parse(JSON.stringify(CPU_PRESETS[presetKey]));
        renderProcessInputTable();
        executeCpuSchedule(false);
        showToast(`Loaded ${btn.textContent} workload`, 'info');
      }
    });
  });

  cpuAlgoRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      const val = radio.value;
      if (cpuAlgoBadge) cpuAlgoBadge.textContent = val;
      if (cpuAlgoDesc && CPU_ALGO_DESCRIPTIONS[val]) {
        cpuAlgoDesc.innerHTML = CPU_ALGO_DESCRIPTIONS[val];
      }
      document.querySelectorAll('[data-cpu-algo]').forEach(label => {
        label.classList.toggle('active', label.dataset.cpuAlgo === val);
      });
      executeCpuSchedule(true);
    });
  });

  if (btnTqDec) {
    btnTqDec.addEventListener('click', () => {
      let val = parseInt(tqInput.value, 10) || 2;
      if (val > 1) {
        val -= 1;
        tqInput.value = val;
        if (tqBadge) tqBadge.textContent = `${val} ms`;
        markCpuOutdated();
      }
    });
  }

  if (btnTqInc) {
    btnTqInc.addEventListener('click', () => {
      let val = parseInt(tqInput.value, 10) || 2;
      if (val < 50) {
        val += 1;
        tqInput.value = val;
        if (tqBadge) tqBadge.textContent = `${val} ms`;
        markCpuOutdated();
      }
    });
  }

  if (tqInput) {
    tqInput.addEventListener('input', () => {
      let val = parseInt(tqInput.value, 10) || 2;
      if (val < 1) val = 1;
      if (tqBadge) tqBadge.textContent = `${val} ms`;
      markCpuOutdated();
    });
  }

  if (btnResetCpu) {
    btnResetCpu.addEventListener('click', () => {
      currentCpuProcesses = JSON.parse(JSON.stringify(CPU_PRESETS['staggered']));
      renderProcessInputTable();
      executeCpuSchedule(false);
      showToast('CPU workload reset to default', 'info');
    });
  }

  function renderCpuGantt(gantt, totalTime) {
    const bar = document.getElementById('gantt-timeline-bar');
    const ticks = document.getElementById('gantt-ticks');
    const legend = document.getElementById('gantt-legend');
    if (!bar || !ticks) return;

    bar.innerHTML = '';
    ticks.innerHTML = '';
    if (legend) legend.innerHTML = '';

    const safeTotal = Math.max(1, totalTime);
    const seenPids = new Set();
    let lastTickPct = 0;

    // Zero tick
    const zeroTick = document.createElement('span');
    zeroTick.className = 'gantt-tick';
    zeroTick.style.left = '0%';
    zeroTick.textContent = '0';
    ticks.appendChild(zeroTick);

    gantt.forEach((seg, idx) => {
      const pid = seg.process || seg.process_id || 'IDLE';
      const start = seg.start !== undefined ? seg.start : seg.start_time;
      const end = seg.end !== undefined ? seg.end : seg.end_time;
      const duration = end - start;
      const widthPct = (duration / safeTotal) * 100;

      const segDiv = document.createElement('div');
      segDiv.className = `gantt-segment ${pid === 'IDLE' ? 'idle-segment' : ''}`;
      segDiv.style.width = `${widthPct}%`;

      let segColor = '#4b5563';
      if (pid !== 'IDLE') {
        const colorIdx = Math.abs(pid.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)) % PID_COLORS.length;
        segColor = PID_COLORS[colorIdx];
        segDiv.style.backgroundColor = segColor;
        seenPids.add(pid);
      }

      segDiv.title = `${pid} [${start} - ${end}] (${duration} ms)`;
      if (widthPct >= 3.5) {
        segDiv.innerHTML = `<span>${pid}</span>`;
      } else {
        segDiv.innerHTML = `<span style="font-size:0.65rem;">•</span>`;
      }
      bar.appendChild(segDiv);

      // Add end tick avoiding collisions
      const endPct = (end / safeTotal) * 100;
      const isLast = (idx === gantt.length - 1);
      if (endPct - lastTickPct >= 4.0 || isLast) {
        const endTick = document.createElement('span');
        endTick.className = 'gantt-tick';
        endTick.style.left = `${endPct}%`;
        endTick.textContent = `${end}`;
        ticks.appendChild(endTick);
        lastTickPct = endPct;
      }
    });

    if (legend) {
      Array.from(seenPids).forEach(pid => {
        const colorIdx = Math.abs(pid.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)) % PID_COLORS.length;
        const color = PID_COLORS[colorIdx];
        const item = document.createElement('div');
        item.className = 'gantt-legend-item';
        item.innerHTML = `<span class="gantt-legend-box" style="background: ${color};"></span><span>${pid}</span>`;
        legend.appendChild(item);
      });
    }
  }

  function renderCpuResultsTable(processes) {
    const tbody = document.getElementById('cpu-results-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    processes.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${p.id}</strong></td>
        <td>${p.arrival_time}</td>
        <td>${p.burst_time}</td>
        <td>${p.completion_time}</td>
        <td>${p.turnaround_time}</td>
        <td>${p.waiting_time}</td>
        <td>${p.response_time}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function updateCpuMetrics(metrics) {
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    setVal('cpu-val-awt', metrics.avg_waiting_time !== undefined ? metrics.avg_waiting_time.toFixed(2) : '-');
    setVal('cpu-val-atat', metrics.avg_turnaround_time !== undefined ? metrics.avg_turnaround_time.toFixed(2) : '-');
    setVal('cpu-val-art', metrics.avg_response_time !== undefined ? metrics.avg_response_time.toFixed(2) : '-');
    setVal('cpu-val-util', metrics.cpu_utilization !== undefined ? metrics.cpu_utilization.toFixed(2) : '-');
    setVal('cpu-val-tp', metrics.throughput !== undefined ? metrics.throughput.toFixed(4) : '-');
  }

  async function executeCpuSchedule(showNotification = true) {
    const procs = syncProcessesFromInputTable();
    const algo = getSelectedCpuAlgorithm();
    const tq = parseInt(tqInput ? tqInput.value : 2, 10) || 2;

    if (btnRunCpu) {
      btnRunCpu.disabled = true;
      btnRunCpu.style.opacity = '0.6';
    }

    try {
      const resp = await MemoraAPI.scheduleCpu(algo, procs, tq);
      if (!resp.ok) {
        showToast(`Error: ${resp.error}`, 'error');
        return;
      }
      const data = resp.data;
      updateCpuMetrics(data.metrics);
      renderCpuGantt(data.gantt_chart, data.metrics.total_time);
      renderCpuResultsTable(data.processes);
      clearCpuOutdated();
      if (showNotification) {
        showToast(`Executed ${algo} CPU scheduling successfully`, 'success');
      }
    } catch (err) {
      showToast(`Failed: ${err.message}`, 'error');
    } finally {
      if (btnRunCpu) {
        btnRunCpu.disabled = false;
        btnRunCpu.style.opacity = '1';
      }
    }
  }

  if (btnRunCpu) {
    btnRunCpu.addEventListener('click', () => {
      executeCpuSchedule(true);
    });
  }

  if (btnCompareCpu) {
    btnCompareCpu.addEventListener('click', async () => {
      const procs = syncProcessesFromInputTable();
      const tq = parseInt(tqInput ? tqInput.value : 2, 10) || 2;

      btnCompareCpu.disabled = true;
      btnCompareCpu.style.opacity = '0.6';

      try {
        const resp = await MemoraAPI.compareCpu(procs, tq);
        if (!resp.ok) {
          showToast(`Error: ${resp.error}`, 'error');
          return;
        }
        const comp = resp.data;
        const compSec = document.getElementById('cpu-comparison-section');
        const tbody = document.getElementById('cpu-comp-tbody');
        if (tbody) {
          tbody.innerHTML = '';
          comp.comparison_table.forEach(row => {
            const tr = document.createElement('tr');
            const isBest = row.algorithm === comp.summary.best_waiting_time_algorithm;
            tr.innerHTML = `
              <td><strong>${row.algorithm}</strong> ${isBest ? '<span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; margin-left: 4px;">Best AWT</span>' : ''}</td>
              <td>${row.avg_waiting_time.toFixed(2)} ms</td>
              <td>${row.avg_turnaround_time.toFixed(2)} ms</td>
              <td>${row.avg_response_time.toFixed(2)} ms</td>
              <td>${row.cpu_utilization.toFixed(2)}%</td>
              <td>${row.throughput.toFixed(4)}</td>
              <td>${isBest ? 'Rank 1' : 'Rank 2'}</td>
            `;
            tbody.appendChild(tr);
          });
        }

        const bannerTitle = document.getElementById('cpu-winner-title');
        const bannerExp = document.getElementById('cpu-winner-explanation');
        if (bannerTitle) {
          bannerTitle.textContent = `${comp.summary.best_waiting_time_algorithm} achieves minimum average waiting time (${comp.summary.lowest_avg_waiting_time.toFixed(2)} ms)`;
        }
        if (bannerExp) {
          bannerExp.textContent = `Shortest Job First (SJF) minimizes Average Waiting Time when bursts are known. Round Robin provides preemptive responsiveness with time quantum q=${tq}.`;
        }

        if (compSec) compSec.style.display = 'block';

        // Also display FCFS Gantt
        const fcfsRes = comp.results.FCFS;
        updateCpuMetrics(fcfsRes.metrics);
        renderCpuGantt(fcfsRes.gantt_chart, fcfsRes.metrics.total_time);
        renderCpuResultsTable(fcfsRes.processes);
        clearCpuOutdated();

        showToast('CPU algorithms comparison completed', 'success');
      } catch (err) {
        showToast(`Failed: ${err.message}`, 'error');
      } finally {
        btnCompareCpu.disabled = false;
        btnCompareCpu.style.opacity = '1';
      }
    });
  }

  // Initialize process table
  renderProcessInputTable();

  // ==========================================================================
  // MODULE 3: DEADLOCK MANAGEMENT CONTROLLER (BANKER'S ALGORITHM)
  // ==========================================================================

  const DEADLOCK_PRESETS = {
    'classic': {
      available: '3, 3, 2',
      resources: 'A, B, C',
      allocation: '0 1 0\n2 0 0\n3 0 2\n2 1 1\n0 0 2',
      max: '7 5 3\n3 2 2\n9 0 2\n2 2 2\n4 3 3',
      request_proc: 1,
      request_vector: '1, 0, 2'
    },
    'unsafe': {
      available: '0, 0',
      resources: 'R1, R2',
      allocation: '1 0\n0 1',
      max: '2 1\n1 2',
      request_proc: 0,
      request_vector: '1, 0'
    },
    'single': {
      available: '2',
      resources: 'R1',
      allocation: '1\n2',
      max: '5\n3',
      request_proc: 0,
      request_vector: '2'
    }
  };

  const dlAvailableInput = document.getElementById('dl-available-input');
  const dlResourcesInput = document.getElementById('dl-resources-input');
  const dlAllocInput = document.getElementById('dl-allocation-input');
  const dlMaxInput = document.getElementById('dl-max-input');
  const dlReqProcSelect = document.getElementById('dl-request-proc');
  const dlReqVectorInput = document.getElementById('dl-request-vector');
  const btnCheckSafety = document.getElementById('btn-check-safety');
  const btnEvalRequest = document.getElementById('btn-eval-request');
  const dlPresetBtns = document.querySelectorAll('[data-deadlock-preset]');

  function markDeadlockOutdated() {
    const banner = document.getElementById('dl-status-banner');
    const heading = document.getElementById('dl-status-heading');
    const desc = document.getElementById('dl-status-desc');
    const seqWrapper = document.getElementById('dl-safe-sequence-wrapper');
    const reqCard = document.getElementById('dl-request-result-card');
    const matricesTable = document.getElementById('dl-matrices-table');
    const stepsTable = document.getElementById('dl-steps-table');

    if (banner) {
      banner.className = 'dl-status-banner warning';
    }
    if (heading) {
      heading.textContent = 'INPUT MODIFIED — RE-RUN SAFETY CHECK';
    }
    if (desc) {
      desc.textContent = 'System matrices or available resources have been modified. Click "Run Banker\'s Safety Check" to verify.';
    }
    if (seqWrapper) seqWrapper.style.opacity = '0.5';
    if (matricesTable) matricesTable.style.opacity = '0.65';
    if (stepsTable) stepsTable.style.opacity = '0.65';
    if (reqCard) reqCard.style.display = 'none';
  }

  function clearDeadlockOutdated() {
    const seqWrapper = document.getElementById('dl-safe-sequence-wrapper');
    const matricesTable = document.getElementById('dl-matrices-table');
    const stepsTable = document.getElementById('dl-steps-table');
    if (seqWrapper) seqWrapper.style.opacity = '1';
    if (matricesTable) matricesTable.style.opacity = '1';
    if (stepsTable) stepsTable.style.opacity = '1';
  }

  function parseMatrixText(text) {
    if (!text) return [];
    return text.trim().split('\n').filter(line => line.trim().length > 0).map(line => {
      return line.replace(/,/g, ' ').trim().split(/\s+/).map(x => parseInt(x, 10));
    });
  }

  function parseVectorText(text) {
    if (!text) return [];
    return text.replace(/,/g, ' ').trim().split(/\s+/).map(x => parseInt(x, 10));
  }

  function getDeadlockPayload() {
    const available = parseVectorText(dlAvailableInput.value);
    const allocation = parseMatrixText(dlAllocInput.value);
    const max = parseMatrixText(dlMaxInput.value);
    const resRaw = dlResourcesInput.value.replace(/,/g, ' ').trim();
    const resourceNames = resRaw ? resRaw.split(/\s+/) : null;
    const processNames = allocation.map((_, i) => `P${i}`);

    return { available, allocation, max, processNames, resourceNames };
  }

  function syncProcessSelectDropdown(numProcesses) {
    if (!dlReqProcSelect) return;
    const currentVal = parseInt(dlReqProcSelect.value, 10);
    dlReqProcSelect.innerHTML = '';
    for (let i = 0; i < numProcesses; i++) {
      const opt = document.createElement('option');
      opt.value = i;
      opt.textContent = `P${i}`;
      if (i === currentVal) opt.selected = true;
      dlReqProcSelect.appendChild(opt);
    }
  }

  // Attach live input listeners for deadlock matrix inputs
  if (dlAvailableInput) dlAvailableInput.addEventListener('input', markDeadlockOutdated);
  if (dlResourcesInput) dlResourcesInput.addEventListener('input', markDeadlockOutdated);
  if (dlAllocInput) {
    dlAllocInput.addEventListener('input', () => {
      markDeadlockOutdated();
      const parsed = parseMatrixText(dlAllocInput.value);
      if (parsed && parsed.length > 0) {
        syncProcessSelectDropdown(parsed.length);
      }
    });
  }
  if (dlMaxInput) dlMaxInput.addEventListener('input', markDeadlockOutdated);

  dlPresetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      dlPresetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetKey = btn.dataset.deadlockPreset;
      const p = DEADLOCK_PRESETS[presetKey];
      if (p) {
        dlAvailableInput.value = p.available;
        dlResourcesInput.value = p.resources;
        dlAllocInput.value = p.allocation;
        dlMaxInput.value = p.max;
        dlReqVectorInput.value = p.request_vector;
        const alloc = parseMatrixText(p.allocation);
        syncProcessSelectDropdown(alloc.length);
        if (dlReqProcSelect && p.request_proc !== undefined) {
          dlReqProcSelect.value = p.request_proc;
        }
        executeDeadlockSafety(false);
        showToast(`Loaded ${btn.textContent} preset`, 'info');
      }
    });
  });

  function renderDeadlockMatrices(data) {
    const tbody = document.getElementById('dl-matrices-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const pNames = data.process_names || data.allocation.map((_, i) => `P${i}`);
    for (let i = 0; i < data.allocation.length; i++) {
      const tr = document.createElement('tr');
      const allocStr = `[${data.allocation[i].join(', ')}]`;
      const maxStr = `[${data.max[i].join(', ')}]`;
      const needStr = `[${data.need[i].join(', ')}]`;

      tr.innerHTML = `
        <td><strong>${pNames[i]}</strong></td>
        <td><code>${allocStr}</code></td>
        <td><code>${maxStr}</code></td>
        <td><code style="color: #60a5fa; font-weight: 700;">${needStr}</code></td>
      `;
      tbody.appendChild(tr);
    }
  }

  function renderDeadlockSteps(steps) {
    const tbody = document.getElementById('dl-steps-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    steps.forEach(s => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${s.step}</strong></td>
        <td><span class="seq-badge" style="padding: 2px 8px; font-size: 0.8rem;">${s.process}</span></td>
        <td><code>[${s.work_before.join(', ')}]</code></td>
        <td><code>[${s.need.join(', ')}]</code></td>
        <td><code>[${s.allocation.join(', ')}]</code></td>
        <td><code>[${s.work_after.join(', ')}]</code></td>
        <td><span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">${s.status}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  function updateDeadlockVerdict(data) {
    const banner = document.getElementById('dl-status-banner');
    const heading = document.getElementById('dl-status-heading');
    const desc = document.getElementById('dl-status-desc');
    const seqWrapper = document.getElementById('dl-safe-sequence-wrapper');
    const seqBadges = document.getElementById('dl-safe-sequence-badges');

    if (banner) {
      banner.className = `dl-status-banner ${data.is_safe ? 'safe' : 'unsafe'}`;
    }
    if (heading) {
      heading.textContent = data.is_safe ? 'SYSTEM IS IN A SAFE STATE' : 'SYSTEM IS IN AN UNSAFE STATE';
    }
    if (desc) {
      desc.textContent = data.explanation;
    }

    if (seqBadges) {
      seqBadges.innerHTML = '';
      if (data.is_safe && data.safe_sequence && data.safe_sequence.length > 0) {
        data.safe_sequence.forEach((pid, idx) => {
          const badge = document.createElement('span');
          badge.className = 'seq-badge';
          badge.textContent = pid;
          seqBadges.appendChild(badge);

          if (idx < data.safe_sequence.length - 1) {
            const arrow = document.createElement('span');
            arrow.className = 'seq-arrow';
            arrow.textContent = '→';
            seqBadges.appendChild(arrow);
          }
        });
        if (seqWrapper) seqWrapper.style.display = 'flex';
      } else {
        if (seqWrapper) seqWrapper.style.display = 'none';
      }
    }
  }

  async function executeDeadlockSafety(showNotification = true) {
    try {
      const payload = getDeadlockPayload();
      if (btnCheckSafety) {
        btnCheckSafety.disabled = true;
        btnCheckSafety.style.opacity = '0.6';
      }

      const resp = await MemoraAPI.checkDeadlockSafety(
        payload.available,
        payload.allocation,
        payload.max,
        payload.processNames,
        payload.resourceNames
      );

      if (!resp.ok) {
        showToast(`Validation error: ${resp.error}`, 'error');
        return;
      }

      const data = resp.data;
      updateDeadlockVerdict(data);
      renderDeadlockMatrices(data);
      renderDeadlockSteps(data.steps);
      syncProcessSelectDropdown(data.allocation.length);
      clearDeadlockOutdated();

      const reqCard = document.getElementById('dl-request-result-card');
      if (reqCard) reqCard.style.display = 'none';

      if (showNotification) {
        showToast(
          data.is_safe ? 'Safety check verified: Safe sequence exists' : 'Safety check warning: Unsafe state detected',
          data.is_safe ? 'success' : 'error'
        );
      }
    } catch (err) {
      showToast(`Failed: ${err.message}`, 'error');
    } finally {
      if (btnCheckSafety) {
        btnCheckSafety.disabled = false;
        btnCheckSafety.style.opacity = '1';
      }
    }
  }

  if (btnCheckSafety) {
    btnCheckSafety.addEventListener('click', () => {
      executeDeadlockSafety(true);
    });
  }

  if (btnEvalRequest) {
    btnEvalRequest.addEventListener('click', async () => {
      try {
        const payload = getDeadlockPayload();
        const pIdx = parseInt(dlReqProcSelect.value, 10);
        const reqVector = parseVectorText(dlReqVectorInput.value);

        btnEvalRequest.disabled = true;
        btnEvalRequest.style.opacity = '0.6';

        const resp = await MemoraAPI.requestDeadlockResource(
          payload.available,
          payload.allocation,
          payload.max,
          pIdx,
          reqVector,
          payload.processNames,
          payload.resourceNames
        );

        if (!resp.ok) {
          showToast(`Request error: ${resp.error}`, 'error');
          return;
        }

        const reqData = resp.data;
        const reqCard = document.getElementById('dl-request-result-card');
        const reqBadge = document.getElementById('dl-request-badge');
        const reqContent = document.getElementById('dl-request-content');

        if (reqCard) reqCard.style.display = 'block';
        if (reqBadge) {
          reqBadge.textContent = reqData.approved ? 'GRANTED' : 'DENIED / MUST WAIT';
          reqBadge.style.background = reqData.approved ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
          reqBadge.style.color = reqData.approved ? '#34d399' : '#f87171';
        }

        if (reqContent) {
          reqContent.innerHTML = `
            <div style="font-size: 0.95rem; line-height: 1.6;">
              <p><strong>Evaluation Decision:</strong> <span style="color: ${reqData.approved ? '#34d399' : '#f87171'}; font-weight: 700;">${reqData.approved ? 'REQUEST GRANTED IMMEDIATELY' : 'REQUEST DENIED — PROCESS MUST WAIT'}</span></p>
              <p style="margin-top: 0.5rem; color: var(--text-secondary);">${reqData.reason}</p>
              ${reqData.approved && reqData.safety_result ? `
                <div style="margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-surface-elevated); border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                  <span style="font-size: 0.82rem; color: var(--text-secondary);">Resulting Safe Sequence:</span>
                  <strong style="color: #60a5fa; margin-left: 0.5rem;">${reqData.safety_result.safe_sequence.join(' → ')}</strong>
                </div>
              ` : ''}
            </div>
          `;
        }

        showToast(reqData.approved ? 'Resource request granted safely' : 'Resource request denied to prevent deadlock', reqData.approved ? 'success' : 'error');
      } catch (err) {
        showToast(`Evaluation failed: ${err.message}`, 'error');
      } finally {
        btnEvalRequest.disabled = false;
        btnEvalRequest.style.opacity = '1';
      }
    });
  }

  // Initial silent execution of CPU scheduling and Deadlock safety check on load
  executeCpuSchedule(false);
  executeDeadlockSafety(false);

});
