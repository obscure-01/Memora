/**
 * Memora Charts Module.
 * Self-contained HTML5 Canvas comparison chart renderer.
 * Requires zero external CDNs or third-party dependencies, guaranteeing 100% offline functionality.
 */

const MemoraCharts = (() => {

  /**
   * Helper to set up high-DPI canvas scaling for razor-sharp rendering.
   */
  function setupHiDpiCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = rect.width || canvas.width;
    const height = rect.height || canvas.height;

    canvas.width = width * dpr;
    canvas.height = height * dpr;

    const ctx = canvas.getContext('2d');
    ctx.resetTransform?.();
    ctx.scale(dpr, dpr);
    return { ctx, width, height };
  }

  /**
   * Render Page Faults vs Hits Grouped Bar Chart.
   * Compares FIFO, LRU, and Optimal on identical sequence.
   * 
   * @param {HTMLCanvasElement} canvas
   * @param {Object} resultsMap - Map of { "FIFO": {...}, "LRU": {...}, "OPTIMAL": {...} }
   */
  function renderFaultsHitsChart(canvas, resultsMap) {
    if (!canvas || !resultsMap) return;
    const { ctx, width, height } = setupHiDpiCanvas(canvas);

    ctx.clearRect(0, 0, width, height);

    const algos = ['FIFO', 'LRU', 'OPTIMAL'];
    const displayNames = { 'FIFO': 'FIFO', 'LRU': 'LRU', 'OPTIMAL': 'Optimal' };

    // Find max value for Y-axis scaling
    let maxVal = 0;
    algos.forEach(key => {
      const data = resultsMap[key] || { faults: 0, hits: 0 };
      if (data.faults > maxVal) maxVal = data.faults;
      if (data.hits > maxVal) maxVal = data.hits;
    });
    maxVal = Math.max(maxVal + 2, 10); // buffer

    // Chart margins
    const padding = { top: 30, right: 20, bottom: 45, left: 45 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Draw horizontal grid lines & Y labels
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.fillStyle = '#9ca3af';
    ctx.font = '11px ui-monospace, SFMono-Regular, Consolas, monospace';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    const ySteps = 5;
    for (let i = 0; i <= ySteps; i++) {
      const val = Math.round((maxVal / ySteps) * i);
      const y = padding.top + chartH - (val / maxVal) * chartH;

      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartW, y);
      ctx.stroke();

      ctx.fillText(val.toString(), padding.left - 8, y);
    }

    // Legend
    const legendY = 14;
    // Faults Legend Pill
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(width - 170, legendY - 5, 12, 10);
    ctx.fillStyle = '#d1d5db';
    ctx.font = '11px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Faults', width - 152, legendY);

    // Hits Legend Pill
    ctx.fillStyle = '#10b981';
    ctx.fillRect(width - 95, legendY - 5, 12, 10);
    ctx.fillStyle = '#d1d5db';
    ctx.fillText('Hits', width - 78, legendY);

    // Draw grouped bars for each algorithm
    const groupWidth = chartW / algos.length;
    const barWidth = Math.min(28, (groupWidth - 30) / 2);

    algos.forEach((key, index) => {
      const data = resultsMap[key] || { faults: 0, hits: 0 };
      const groupCenter = padding.left + (index + 0.5) * groupWidth;

      const faultsH = (data.faults / maxVal) * chartH;
      const hitsH = (data.hits / maxVal) * chartH;

      const faultX = groupCenter - barWidth - 3;
      const faultY = padding.top + chartH - faultsH;

      const hitX = groupCenter + 3;
      const hitY = padding.top + chartH - hitsH;

      // Draw Faults Bar (Coral/Red)
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(faultX, faultY, barWidth, faultsH, [4, 4, 0, 0]) : ctx.fillRect(faultX, faultY, barWidth, faultsH);
      ctx.fill();

      // Value label on Faults
      ctx.fillStyle = '#fca5a5';
      ctx.font = 'bold 11px ui-monospace, Consolas, monospace';
      ctx.textAlign = 'center';
      ctx.fillText(data.faults.toString(), faultX + barWidth / 2, Math.max(faultY - 5, padding.top + 8));

      // Draw Hits Bar (Emerald/Green)
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(hitX, hitY, barWidth, hitsH, [4, 4, 0, 0]) : ctx.fillRect(hitX, hitY, barWidth, hitsH);
      ctx.fill();

      // Value label on Hits
      ctx.fillStyle = '#6ee7b7';
      ctx.fillText(data.hits.toString(), hitX + barWidth / 2, Math.max(hitY - 5, padding.top + 8));

      // X-Axis Algorithm Name
      ctx.fillStyle = '#f9fafb';
      ctx.font = '600 12px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.fillText(displayNames[key], groupCenter, height - 15);
    });
  }

  /**
   * Render Hit Ratio (%) Comparison Bar Chart.
   * 
   * @param {HTMLCanvasElement} canvas
   * @param {Object} resultsMap - Map of { "FIFO": {...}, "LRU": {...}, "OPTIMAL": {...} }
   */
  function renderHitRatioChart(canvas, resultsMap) {
    if (!canvas || !resultsMap) return;
    const { ctx, width, height } = setupHiDpiCanvas(canvas);

    ctx.clearRect(0, 0, width, height);

    const algos = ['FIFO', 'LRU', 'OPTIMAL'];
    const displayNames = { 'FIFO': 'FIFO', 'LRU': 'LRU', 'OPTIMAL': 'Optimal' };
    const barColors = {
      'FIFO': '#3b82f6',
      'LRU': '#06b6d4',
      'OPTIMAL': '#8b5cf6',
    };

    const padding = { top: 30, right: 20, bottom: 45, left: 45 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Y-Axis: 0% to 100%
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.fillStyle = '#9ca3af';
    ctx.font = '11px ui-monospace, SFMono-Regular, Consolas, monospace';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    const yMarks = [0, 25, 50, 75, 100];
    yMarks.forEach(pct => {
      const y = padding.top + chartH - (pct / 100) * chartH;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartW, y);
      ctx.stroke();

      ctx.fillText(`${pct}%`, padding.left - 6, y);
    });

    const groupWidth = chartW / algos.length;
    const barWidth = Math.min(42, groupWidth - 30);

    algos.forEach((key, index) => {
      const data = resultsMap[key] || { hit_ratio: 0 };
      const pct = (data.hit_ratio * 100);
      const barH = (pct / 100) * chartH;
      const x = padding.left + (index + 0.5) * groupWidth - barWidth / 2;
      const y = padding.top + chartH - barH;

      ctx.fillStyle = barColors[key] || '#3b82f6';
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(x, y, barWidth, barH, [6, 6, 0, 0]) : ctx.fillRect(x, y, barWidth, barH);
      ctx.fill();

      // Percentage label on top of bar
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 11px ui-monospace, Consolas, monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`${pct.toFixed(1)}%`, x + barWidth / 2, Math.max(y - 6, padding.top + 8));

      // Algorithm name
      ctx.fillStyle = '#f9fafb';
      ctx.font = '600 12px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.fillText(displayNames[key], x + barWidth / 2, height - 15);
    });
  }

  return {
    renderFaultsHitsChart,
    renderHitRatioChart,
  };
})();

window.MemoraCharts = MemoraCharts;
