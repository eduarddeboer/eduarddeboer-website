document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-privacy-video]");
  if (!button) return;

  const provider = button.dataset.provider;
  const videoId = button.dataset.videoId;
  if (provider !== "youtube" || !videoId) return;

  const wrapper = button.closest(".privacy-video");
  if (!wrapper) return;

  const iframe = document.createElement("iframe");
  iframe.src =
    "https://www.youtube-nocookie.com/embed/" +
    encodeURIComponent(videoId) +
    "?autoplay=1&rel=0";
  iframe.title = button.dataset.title || "Video";
  iframe.loading = "lazy";
  iframe.allow =
    "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share";
  iframe.allowFullscreen = true;
  iframe.referrerPolicy = "strict-origin-when-cross-origin";

  wrapper.classList.add("privacy-video--active");
  wrapper.replaceChildren(iframe);
});
