(() => {
  "use strict";

  function validArchiveUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === "https:" && url.hostname === "archive.org" ? url : null;
    } catch {
      return null;
    }
  }

  async function activate(button) {
    const url = validArchiveUrl(button.dataset.audioSrc);
    if (!url) return;

    button.disabled = true;

    const player = document.createElement("audio");
    player.className = "podcast-audio";
    player.controls = true;
    player.preload = "none";
    player.src = url.toString();
    player.setAttribute(
      "aria-label",
      button.dataset.audioLabel || "Podcastaflevering afspelen"
    );

    button.replaceWith(player);
    player.load();

    try {
      await player.play();
    } catch {
      // The native player remains available if the browser blocks autoplay.
    }
  }

  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-podcast-launch]");
    if (button) activate(button);
  });
})();
