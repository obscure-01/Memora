/**
 * Memora API Client Module.
 * Communicates with the Flask REST endpoints (/api/health, /api/simulate, /api/compare).
 */

const MemoraAPI = (() => {
  const BASE_URL = window.location.origin;

  /**
   * Helper to perform JSON fetch with standardized error parsing.
   */
  async function request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
    };

    try {
      const response = await fetch(url, config);
      let data = null;

      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        data = { message: text };
      }

      if (!response.ok) {
        // Extract descriptive error details if present
        let errorMsg = 'An unexpected server error occurred.';
        if (data && data.error) {
          errorMsg = data.error.details || data.error.message || errorMsg;
        } else if (data && data.message) {
          errorMsg = data.message;
        }
        return { ok: false, status: response.status, error: errorMsg };
      }

      return { ok: true, status: response.status, data };
    } catch (err) {
      return {
        ok: false,
        status: 0,
        error: 'Cannot connect to Memora backend. Ensure "python app.py" is running on http://127.0.0.1:5000.',
      };
    }
  }

  /**
   * Check backend health and readiness.
   * GET /api/health
   */
  async function checkHealth() {
    return await request('/api/health', { method: 'GET' });
  }

  /**
   * Execute single algorithm simulation.
   * POST /api/simulate
   * @param {number[]} sequence - List of non-negative page integers
   * @param {number} frames - Number of physical memory frames
   * @param {string} algorithm - "FIFO" | "LRU" | "Optimal"
   */
  async function simulate(sequence, frames, algorithm) {
    const payload = {
      sequence: sequence,
      frames: frames,
      algorithm: algorithm,
    };
    return await request('/api/simulate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Compare FIFO, LRU, and Optimal algorithms on identical input.
   * POST /api/compare
   * @param {number[]} sequence - List of non-negative page integers
   * @param {number} frames - Number of physical memory frames
   */
  async function compare(sequence, frames) {
    const payload = {
      sequence: sequence,
      frames: frames,
    };
    return await request('/api/compare', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Run single CPU scheduling algorithm simulation (FCFS, SJF, RR).
   * POST /api/cpu/schedule
   */
  async function scheduleCpu(algorithm, processes, timeQuantum = 2) {
    const payload = {
      algorithm,
      processes,
      time_quantum: timeQuantum,
    };
    return await request('/api/cpu/schedule', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Compare FCFS, SJF, and Round Robin on identical workload.
   * POST /api/cpu/compare
   */
  async function compareCpu(processes, timeQuantum = 2) {
    const payload = {
      processes,
      time_quantum: timeQuantum,
    };
    return await request('/api/cpu/compare', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Execute Banker's Safety Algorithm to verify safe state and sequence.
   * POST /api/deadlock/safety
   */
  async function checkDeadlockSafety(available, allocation, maxMatrix, processNames = null, resourceNames = null) {
    const payload = {
      available,
      allocation,
      max: maxMatrix,
      process_names: processNames,
      resource_names: resourceNames,
    };
    return await request('/api/deadlock/safety', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Evaluate a process's resource request using Banker's Algorithm.
   * POST /api/deadlock/request
   */
  async function requestDeadlockResource(available, allocation, maxMatrix, processIndex, requestVector, processNames = null, resourceNames = null) {
    const payload = {
      available,
      allocation,
      max: maxMatrix,
      process_index: processIndex,
      request: requestVector,
      process_names: processNames,
      resource_names: resourceNames,
    };
    return await request('/api/deadlock/request', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  return {
    checkHealth,
    simulate,
    compare,
    scheduleCpu,
    compareCpu,
    checkDeadlockSafety,
    requestDeadlockResource,
  };
})();

window.MemoraAPI = MemoraAPI;
