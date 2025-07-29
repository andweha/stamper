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
  const comments = document.getElementById('comments-container');

  if (!bar || !barFill) return;

  const duration = Number(bar.dataset.duration) || 0;
  const mediaId = bar.dataset.epid;
  const mediaType = bar.dataset.mediaType;
  const STORAGE_KEY = `episode:${mediaId}:${location.pathname}`;

  let elapsed = Number(localStorage.getItem(STORAGE_KEY)) || 0;
  let timerId = null;
  let playing = false;
  let watchedTimeThisSession = 0;
  const WATCH_TIME_UPDATE_INTERVAL = 10;

  const fmt = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = Math.floor(s % 60);
    return h > 0
      ? `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
      : `${m}:${String(sec).padStart(2, '0')}`;
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

    if (dot) dot.style.left = `${pct * 100}%`;
    if (tooltip) {
      tooltip.textContent = fmt(elapsed);
      tooltip.style.left = `${pct * bar.clientWidth}px`;
      tooltip.style.display = playing ? 'block' : tooltip.style.display;
    }

    if (tsInput) tsInput.value = fmt(elapsed);
    if (currentTimeDisplay) currentTimeDisplay.textContent = fmt(elapsed);
    if (totalTimeDisplay) totalTimeDisplay.textContent = fmt(duration);

    updateVisibleComments();
    localStorage.setItem(STORAGE_KEY, elapsed);
    playBtn.textContent = playing ? '❚❚' : '▶';
  }

  function tick() {
    elapsed += 1;
    watchedTimeThisSession += 1;

    if (watchedTimeThisSession >= WATCH_TIME_UPDATE_INTERVAL) {
      sendWatchTimeToServer(watchedTimeThisSession);
      watchedTimeThisSession = 0;
    }

    if (elapsed >= duration) {
      elapsed = duration;
      clearInterval(timerId);
      playing = false;
      localStorage.removeItem(STORAGE_KEY);
      if (watchedTimeThisSession > 0) {
        sendWatchTimeToServer(watchedTimeThisSession);
        watchedTimeThisSession = 0;
      }
    }

    render();
  }

  function sendWatchTimeToServer(seconds) {
    if (!mediaType || !mediaId || seconds <= 0 || !Number.isFinite(seconds)) {
      console.warn("Cannot send watch time: invalid input.", { mediaType, mediaId, seconds });
      return;
    }

    const payload = {
      watched_seconds: seconds,
      media_type: mediaType,
      media_id: mediaId
    };

    if (navigator.sendBeacon) {
      const formData = new FormData();
      for (const key in payload) formData.append(key, payload[key]);
      navigator.sendBeacon('/update_watch_time_beacon', formData);
    } else {
      fetch('/update_watch_time', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true
      }).catch(err => console.error('Error sending watch time:', err));
    }
  }

  playBtn?.addEventListener('click', () => {
    playing = !playing;
    if (playing) {
      timerId = setInterval(tick, 1000);
    } else {
      clearInterval(timerId);
      if (watchedTimeThisSession > 0) {
        sendWatchTimeToServer(watchedTimeThisSession);
        watchedTimeThisSession = 0;
      }
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
    tooltip.style.left = `${e.clientX - rect.left}px`;
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
    if (playing) {
      clearInterval(timerId);
      timerId = setInterval(tick, 1000);
    }
  });

  showBtn?.addEventListener('click', () => {
    updateVisibleComments();
    const overlay = document.getElementById('commentOverlay');
    overlay?.classList.add('hidden');
  });

  window.addEventListener('beforeunload', () => {
    if (watchedTimeThisSession > 0) {
      sendWatchTimeToServer(watchedTimeThisSession);
    }
  });

  // HEATMAP
  fetch(`/api/comments/${mediaId}`)
    .then(res => res.json())
    .then(timestamps => {
      const secondsPerBucket = 30;
      const bucketCount = Math.min(200, Math.max(10, Math.floor(duration / secondsPerBucket)));
      const bucketSize = duration / bucketCount;
      const density = new Array(bucketCount).fill(0);

      timestamps.forEach(ts => {
        const i = Math.floor(ts / bucketSize);
        if (i < bucketCount) density[i]++;
      });

      const max = Math.max(...density, 1);
      const getGrayscale = norm => `hsl(0, 0%, ${90 - norm * 60}%)`;
      const getColor = norm => `hsl(250, 80%, ${85 - norm * 60}%)`;

      const stopsGray = density.map((count, i) =>
        `${getGrayscale(count / max)} ${(i / bucketCount) * 100}%`);
      const stopsColor = density.map((count, i) =>
        `${getColor(count / max)} ${(i / bucketCount) * 100}%`);

      if (heatmapOverlay) {
        heatmapOverlay.style.background = `linear-gradient(to right, ${stopsGray.join(', ')})`;
      }
      barFill.style.background = `linear-gradient(to right, ${stopsColor.join(', ')})`;
    })
    .catch(err => console.error("Failed to load heatmap data:", err));

  render();
});
