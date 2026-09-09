const STORAGE_KEY = "shrinkit_links";

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveHistory(links) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(links.slice(0, 20)));
}

function renderRow(container, link) {
  const template = document.getElementById("link-row-template");
  const row = template.content.cloneNode(true);

  const shortLink = row.querySelector(".short-url");
  shortLink.href = link.short_url;
  shortLink.textContent = link.short_url;

  row.querySelector(".target-url").textContent = link.target_url;

  row.querySelector(".copy-btn").addEventListener("click", async (e) => {
    try {
      await navigator.clipboard.writeText(link.short_url);
      e.target.textContent = "Скопировано";
    } catch {
      e.target.textContent = "Не вышло";
    }
    setTimeout(() => (e.target.textContent = "Копировать"), 1500);
  });

  const statsBtn = row.querySelector(".stats-btn");
  const clicksSpan = row.querySelector(".clicks");
  statsBtn.addEventListener("click", async () => {
    const res = await fetch(`/links/${link.slug}/stats`);
    if (res.ok) {
      const data = await res.json();
      clicksSpan.textContent = data.total_clicks;
    }
  });

  container.prepend(row);
}

function renderHistory() {
  const container = document.getElementById("history");
  container.innerHTML = "";
  loadHistory().forEach((link) => renderRow(container, link));
}

function showError(text) {
  const box = document.getElementById("error-box");
  box.textContent = text;
  box.hidden = false;
}

function hideError() {
  document.getElementById("error-box").hidden = true;
}

document.getElementById("shorten-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();

  const input = document.getElementById("target-url");
  const url = input.value.trim();

  const res = await fetch("/links", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_url: url }),
  });

  if (!res.ok) {
    if (res.status === 429) {
      showError("Слишком много ссылок подряд — подожди немного.");
    } else {
      showError("Не получилось сократить эту ссылку, проверь адрес.");
    }
    return;
  }

  const link = await res.json();
  const history = loadHistory();
  history.unshift(link);
  saveHistory(history);
  renderRow(document.getElementById("history"), link);
  input.value = "";
});

renderHistory();
