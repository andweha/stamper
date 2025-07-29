document.addEventListener('DOMContentLoaded', () => {
  const bar = document.getElementById('progress-container');
  const barFill = document.getElementById('progress-bar');
  const tooltip = document.getElementById('progress-tooltip');
  const heatmapOverlay = document.querySelector('.heatmap-overlay');
  const playBtn = document.getElementById('play-btn');
  const tsInput = document.querySelector('input[name="timestamp"]');
  const showBtn = document.getElementById('showCommentsBtn');
  const dot = document.getElementById('progress-dot');
  const currentTimeDisplay = document.getElementById('current-time');
  const totalTimeDisplay = document.getElementById('total-time');
  const skipBackBtn = document.getElementById('skip-back');
  const skipForwardBtn = document.getElementById('skip-forward');

  if (!bar || !barFill) return;

  const duration = Number(bar.dataset.duration) || 0;
  const mediaId = bar.dataset.epid;
  const STORAGE_KEY = `episode:${mediaId}:${location.pathname}`;

  let elapsed = Number(localStorage.getItem(STORAGE_KEY)) || 0;
  let timerId = null;
  let playing = false;

  const fmt = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = Math.floor(s % 60);

    if (h > 0) {
      return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
    } else {
      return `${m}:${String(sec).padStart(2, '0')}`;
    }
  };

  function updateVisibleComments() {
    document.querySelectorAll('.comment-line').forEach(comment => {
      const time = Number(comment.dataset.secs);
      comment.style.display = (!isNaN(time) && time <= elapsed) ? 'block' : 'none';
    });
  }

  function render() {
    const pct = elapsed / duration;
    const mask = `linear-gradient(to right, white ${pct * 100}%, transparent ${pct * 100}%)`;
    barFill.style.maskImage = mask;
    barFill.style.webkitMaskImage = mask;

    if (dot) {
      dot.style.left = `${pct * 100}%`;
    }

    tooltip.style.left = `${pct * bar.clientWidth}px`;
    tooltip.textContent = fmt(elapsed);
    tooltip.style.display = playing ? 'block' : tooltip.style.display;
    playBtn.textContent = playing ? '❚❚' : '▶';

    if (tsInput) tsInput.value = fmt(elapsed);
    if (currentTimeDisplay) currentTimeDisplay.textContent = fmt(elapsed);
    if (totalTimeDisplay) totalTimeDisplay.textContent = fmt(duration);

    updateVisibleComments();
    localStorage.setItem(STORAGE_KEY, elapsed);
  }

  function tick() {
    elapsed += 1;
    if (elapsed >= duration) {
      elapsed = duration;
      clearInterval(timerId);
      playing = false;
      localStorage.removeItem(STORAGE_KEY);
    }
    render();
  }

  playBtn?.addEventListener('click', () => {
    playing = !playing;
    if (playing) {
      timerId = setInterval(tick, 1000);
    } else {
      clearInterval(timerId);
    }
    render();
  });

  skipBackBtn?.addEventListener('click', () => {
    elapsed = Math.max(elapsed - 15, 0);
    render();
  });

  skipForwardBtn?.addEventListener('click', () => {
    elapsed = Math.min(elapsed + 15, duration);
    render();
  });

  bar.addEventListener('mousemove', (e) => {
    if (playing) return;
    const rect = bar.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    const tooltipX = e.clientX - rect.left;

    tooltip.style.left = `${tooltipX}px`;
    tooltip.textContent = fmt(pct * duration);
    tooltip.style.display = 'block';
  });


  bar.addEventListener('mouseleave', () => {
    if (!playing) tooltip.style.display = 'none';
  });

  bar.addEventListener('click', (e) => {
    const rect = bar.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    elapsed = pct * duration;
    render();
  });

  showBtn?.addEventListener('click', () => {
    updateVisibleComments();
    const overlay = document.getElementById('commentOverlay');
    overlay?.classList.add('hidden');
  });

  // === HEATMAP GENERATION ===
  fetch(`/api/comments/${mediaId}`)
    .then(res => res.json())
    .then(timestamps => {
      // Aim for ~20–30s per bucket
      const secondsPerBucket = 30;
      const bucketCount = Math.min(200, Math.max(10, Math.floor(duration / secondsPerBucket)));
      const bucketSize = duration / bucketCount;
      const density = new Array(bucketCount).fill(0);

      timestamps.forEach(ts => {
        const i = Math.floor(ts / bucketSize);
        if (i < bucketCount) density[i]++;
      });

      const max = Math.max(...density, 1);

      const getGrayscale = (norm) => {
        const lightness = 90 - norm * 60;
        return `hsl(0, 0%, ${lightness}%)`;
      };

      const getColor = (norm) => {
        const lightness = 85 - norm * 60;
        return `hsl(250, 80%, ${lightness}%)`;
      };

      const stopsGray = density.map((count, i) => {
        const pct = (i / bucketCount) * 100;
        return `${getGrayscale(count / max)} ${pct.toFixed(2)}%`;
      });

      const stopsColor = density.map((count, i) => {
        const pct = (i / bucketCount) * 100;
        return `${getColor(count / max)} ${pct.toFixed(2)}%`;
      });

      if (heatmapOverlay) {
        heatmapOverlay.style.background = `linear-gradient(to right, ${stopsGray.join(', ')})`;
      }

      barFill.style.background = `linear-gradient(to right, ${stopsColor.join(', ')})`;
    })
    .catch(err => console.error("Failed to load comment timestamps for heatmap:", err));

  render();
});
