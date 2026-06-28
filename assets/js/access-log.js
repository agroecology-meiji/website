(() => {
  const TRACKING_HOSTNAME = "agroecology-meiji.github.io";
  const TRACKING_ENDPOINT = "https://script.google.com/macros/s/AKfycbyT31uXmkw1rh8MFzEmwbet3LHPDDo_-twwaTDNKzyPe9TgNCuXX9XDf5wVOYUznuLD/exec";
  const ACCESS_KEY = "access_log";
  const CLIENT_ID_KEY = "agroecology_access_client_id_v1";

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

  const clientId = getOrCreateClientId();
  if (!clientId) return;

  const params = new URLSearchParams({
    page: pageName,
    key: ACCESS_KEY,
    client_id: clientId,
    t: String(Date.now())
  });

  const ping = new Image();
  ping.referrerPolicy = "no-referrer-when-downgrade";
  ping.src = `${TRACKING_ENDPOINT}?${params.toString()}`;

  function getOrCreateClientId() {
    const existing = readStorage(localStorage, CLIENT_ID_KEY) || readStorage(sessionStorage, CLIENT_ID_KEY);
    if (existing) return existing;

    const id = createClientId();

    if (writeStorage(localStorage, CLIENT_ID_KEY, id)) return id;
    if (writeStorage(sessionStorage, CLIENT_ID_KEY, id)) return id;

    return id;
  }

  function createClientId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }

    const randomValues = new Uint32Array(4);
    if (window.crypto && typeof window.crypto.getRandomValues === "function") {
      window.crypto.getRandomValues(randomValues);
      return Array.from(randomValues, value => value.toString(16).padStart(8, "0")).join("");
    }

    return `client_${Date.now()}_${Math.random().toString(36).slice(2)}`;
  }

  function readStorage(storage, key) {
    try {
      return storage.getItem(key);
    } catch (error) {
      return "";
    }
  }

  function writeStorage(storage, key, value) {
    try {
      storage.setItem(key, value);
      return true;
    } catch (error) {
      return false;
    }
  }
})();
