(() => {
  const TRACKING_HOSTNAME = "agroecology-meiji.github.io";
  const TRACKING_ENDPOINT = "https://script.google.com/macros/s/AKfycbyT31uXmkw1rh8MFzEmwbet3LHPDDo_-twwaTDNKzyPe9TgNCuXX9XDf5wVOYUznuLD/exec";
  const ACCESS_KEY = "access_log";
  const PAGE_NAME = "top";

  const TOP_PATHS = new Set([
    "/website",
    "/website/",
    "/website/index.html",
    "/website/en",
    "/website/en/",
    "/website/en/index.html"
  ]);

  if (window.location.hostname !== TRACKING_HOSTNAME) return;
  if (!TOP_PATHS.has(window.location.pathname)) return;

  const params = new URLSearchParams({
    page: PAGE_NAME,
    key: ACCESS_KEY,
    t: String(Date.now())
  });

  const ping = new Image();
  ping.referrerPolicy = "no-referrer-when-downgrade";
  ping.src = `${TRACKING_ENDPOINT}?${params.toString()}`;
})();
