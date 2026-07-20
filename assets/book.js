document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-code");
  if (!button) return;

  const listing = button.closest(".code-listing");
  const code = listing?.querySelector("pre:not(.code-output) > code");
  if (!code) return;

  const originalLabel = button.textContent;
  try {
    let copied = false;
    if (navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(code.textContent);
        copied = true;
      } catch {
        copied = false;
      }
    }
    if (!copied) {
      const fallback = document.createElement("textarea");
      fallback.value = code.textContent;
      fallback.setAttribute("readonly", "");
      fallback.style.position = "fixed";
      fallback.style.opacity = "0";
      document.body.append(fallback);
      fallback.select();
      if (!document.execCommand("copy")) throw new Error("copy command failed");
      fallback.remove();
    }
    button.textContent = "已复制";
  } catch {
    button.textContent = "复制失败";
  }
  window.setTimeout(() => {
    button.textContent = originalLabel;
  }, 1400);
});

const AUDIO_STORAGE_PREFIX = "statistical-rethinking-zh:audio:";

function formatAudioTime(value) {
  if (!Number.isFinite(value) || value < 0) return "--:--";
  const total = Math.floor(value);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const seconds = total % 60;
  if (hours) return `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function readAudioState(key) {
  try {
    return JSON.parse(window.localStorage.getItem(key) || "null");
  } catch {
    return null;
  }
}

function writeAudioState(key, state) {
  try {
    window.localStorage.setItem(key, JSON.stringify(state));
  } catch {
    // Playback remains functional when storage is unavailable.
  }
}

function clearAudioState(key) {
  try {
    window.localStorage.removeItem(key);
  } catch {
    // Playback remains functional when storage is unavailable.
  }
}

document.querySelectorAll(".audio-reader").forEach((player) => {
  const audio = player.querySelector("audio");
  const toggle = player.querySelector("[data-audio-toggle]");
  const seek = player.querySelector("[data-audio-seek]");
  const current = player.querySelector("[data-audio-current]");
  const duration = player.querySelector("[data-audio-duration]");
  const rate = player.querySelector("[data-audio-rate]");
  const reset = player.querySelector("[data-audio-reset]");
  const status = player.querySelector("[data-audio-status]");
  if (!audio || !toggle || !seek || !current || !duration || !rate || !reset || !status) return;

  const storageKey = `${AUDIO_STORAGE_PREFIX}${player.dataset.audioId}`;
  let lastSavedSecond = -1;

  const updateTimeline = () => {
    current.textContent = formatAudioTime(audio.currentTime);
    duration.textContent = formatAudioTime(audio.duration);
    const fraction = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.currentTime / audio.duration : 0;
    const progress = Math.max(0, Math.min(1, fraction));
    seek.value = String(Math.round(progress * 1000));
    seek.style.setProperty("--audio-progress", `${progress * 100}%`);
  };

  const updatePlayState = () => {
    const playing = !audio.paused && !audio.ended;
    toggle.textContent = playing ? "暂停" : "播放";
    toggle.setAttribute("aria-pressed", String(playing));
    player.classList.toggle("is-playing", playing);
  };

  const persist = () => {
    if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
    if (audio.ended || audio.currentTime >= audio.duration - 3) {
      clearAudioState(storageKey);
      return;
    }
    writeAudioState(storageKey, {
      currentTime: audio.currentTime,
      playbackRate: audio.playbackRate,
      updatedAt: Date.now(),
    });
    lastSavedSecond = Math.floor(audio.currentTime);
  };

  player.classList.add("is-enhanced");
  audio.removeAttribute("controls");

  audio.addEventListener("loadedmetadata", () => {
    const saved = readAudioState(storageKey);
    if (saved && Number.isFinite(saved.playbackRate)) {
      const savedRate = String(saved.playbackRate);
      if ([...rate.options].some((option) => option.value === savedRate)) {
        rate.value = savedRate;
        audio.playbackRate = saved.playbackRate;
      }
    }
    if (saved && Number.isFinite(saved.currentTime) && saved.currentTime > 3 && saved.currentTime < audio.duration - 10) {
      audio.currentTime = saved.currentTime;
      status.textContent = `已恢复到 ${formatAudioTime(saved.currentTime)}。`;
    }
    updateTimeline();
  });

  audio.addEventListener("timeupdate", () => {
    updateTimeline();
    if (Math.abs(Math.floor(audio.currentTime) - lastSavedSecond) >= 5) persist();
  });
  audio.addEventListener("play", updatePlayState);
  audio.addEventListener("pause", () => {
    updatePlayState();
    persist();
  });
  audio.addEventListener("ended", () => {
    updatePlayState();
    clearAudioState(storageKey);
    status.textContent = "本章已播放完毕。";
  });
  audio.addEventListener("error", () => {
    status.textContent = "音频暂时无法加载，请刷新后重试。";
    toggle.disabled = true;
    seek.disabled = true;
  });

  toggle.addEventListener("click", async () => {
    if (audio.paused) {
      try {
        await audio.play();
        status.textContent = "正在播放，进度会自动保存。";
      } catch {
        status.textContent = "浏览器阻止了播放，请再试一次。";
      }
    } else {
      audio.pause();
      status.textContent = "已暂停并保存进度。";
    }
  });

  seek.addEventListener("input", () => {
    if (!Number.isFinite(audio.duration)) return;
    audio.currentTime = (Number(seek.value) / 1000) * audio.duration;
    updateTimeline();
  });
  seek.addEventListener("change", persist);

  player.querySelectorAll("[data-audio-skip]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!Number.isFinite(audio.duration)) return;
      const next = audio.currentTime + Number(button.dataset.audioSkip);
      audio.currentTime = Math.max(0, Math.min(audio.duration, next));
      updateTimeline();
      persist();
    });
  });

  rate.addEventListener("change", () => {
    audio.playbackRate = Number(rate.value);
    status.textContent = `播放速度已设为 ${rate.options[rate.selectedIndex].textContent}。`;
    persist();
  });

  reset.addEventListener("click", () => {
    audio.pause();
    audio.currentTime = 0;
    clearAudioState(storageKey);
    updateTimeline();
    updatePlayState();
    status.textContent = "本章播放进度已清除。";
  });

  window.addEventListener("pagehide", persist);
  updatePlayState();
  updateTimeline();
});
