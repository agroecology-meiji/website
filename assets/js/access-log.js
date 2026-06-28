(() => {
  const TRACKING_HOSTNAME = "agroecology-meiji.github.io";
  const TRACKING_ENDPOINT = "https://script.google.com/macros/s/AKfycbyT31uXmkw1rh8MFzEmwbet3LHPDDo_-twwaTDNKzyPe9TgNCuXX9XDf5wVOYUznuLD/exec";
  const ACCESS_KEY = "access_log";

  const TOP_PAGE_MAP = {
    "/website": "jp",
    "/website/": "jp",
    "/website/index.html": "jp",
    "/website/en": "en",
    "/website/en/": "en",
    "/website/en/index.html": "en"
  };

  if (window.location.hostname !== TRACKING_HOSTNAME) return;

  const pageName = TOP_PAGE_MAP[window.location.pathname];
  if (!pageName) return;

  const params = new URLSearchParams({
    page: pageName,
    key: ACCESS_KEY,
    t: String(Date.now())
  });

  const ping = new Image();
  ping.referrerPolicy = "no-referrer-when-downgrade";
  ping.src = `${TRACKING_ENDPOINT}?${params.toString()}`;
})();
