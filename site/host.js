const columns = [
  { key: "name", label: "Name" },
  { key: "score", label: "Score" },
  { key: "playedAt", label: "Played" },
];

const PASSWORD_KEY = "host-password";

const state = {
  scores: [],
  sortKey: "playedAt",
  sortDir: "desc",
};

const host = document.querySelector("#host");

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function playedLabel(value) {
  const date = new Date(value.replace(" ", "T") + "Z");
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function compare(a, b) {
  const key = state.sortKey;
  if (key === "score") return a.score - b.score;
  if (key === "playedAt") return a.playedAt.localeCompare(b.playedAt);
  return a.name.localeCompare(b.name, undefined, { sensitivity: "base" });
}

function sortedScores() {
  const rows = state.scores.slice().sort(compare);
  if (state.sortDir === "desc") rows.reverse();
  return rows;
}

function render(message) {
  const top = el("div", "top");
  top.append(el("p", "eyebrow", "Host"));
  const refresh = el("button", "btn btn-quiet", "Refresh");
  refresh.type = "button";
  refresh.addEventListener("click", load);
  top.append(refresh);

  const title = el("h1", null, "Scores");
  const lede = el(
    "p",
    "lede",
    state.scores.length === 1 ? "1 play saved." : state.scores.length + " plays saved."
  );

  const table = document.createElement("table");
  table.className = "scores";
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((column) => {
    const cell = document.createElement("th");
    const button = el("button", "sort", column.label);
    button.type = "button";
    const active = state.sortKey === column.key;
    if (active) {
      cell.setAttribute("aria-sort", state.sortDir === "asc" ? "ascending" : "descending");
      button.append(el("span", "dir", state.sortDir === "asc" ? "↑" : "↓"));
    } else {
      cell.setAttribute("aria-sort", "none");
    }
    button.addEventListener("click", () => {
      if (state.sortKey === column.key) {
        state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
      } else {
        state.sortKey = column.key;
        state.sortDir = column.key === "name" ? "asc" : "desc";
      }
      render();
    });
    cell.append(button);
    headRow.append(cell);
  });
  thead.append(headRow);

  const tbody = document.createElement("tbody");
  if (!state.scores.length) {
    const row = document.createElement("tr");
    const cell = el("td", null, message || "No scores yet.");
    cell.colSpan = columns.length;
    row.append(cell);
    tbody.append(row);
  } else {
    sortedScores().forEach((score) => {
      const row = document.createElement("tr");
      row.append(el("td", null, score.name));
      row.append(el("td", "num", score.score + " / 5"));
      row.append(el("td", null, playedLabel(score.playedAt)));
      tbody.append(row);
    });
  }
  table.append(thead, tbody);
  host.replaceChildren(top, title, lede, table);
}

function renderGate(errorText) {
  const eyebrow = el("p", "eyebrow", "Host");
  const title = el("h1", null, "Scores");
  const lede = el("p", "lede", "Enter the host password to see saved plays.");
  const form = el("form", "name-form");
  const label = el("label", null, "Password");
  const input = document.createElement("input");
  input.type = "password";
  input.id = "host-password";
  input.autocomplete = "current-password";
  input.required = true;
  label.htmlFor = input.id;
  const button = el("button", "btn", "Open scores");
  button.type = "submit";
  const error = el("p", "prompt", errorText || "");
  form.append(label, input, button, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const password = input.value;
    if (!password) {
      error.textContent = "Enter the host password.";
      input.focus();
      return;
    }
    sessionStorage.setItem(PASSWORD_KEY, password);
    load();
  });
  host.replaceChildren(eyebrow, title, lede, form);
  input.focus();
}

function load() {
  const password = sessionStorage.getItem(PASSWORD_KEY) || "";
  if (!password) {
    renderGate();
    return;
  }
  fetch("/api/scores", { headers: { "X-Host-Password": password } })
    .then((res) => {
      if (res.status === 401) {
        sessionStorage.removeItem(PASSWORD_KEY);
        renderGate("That password is not right.");
        return null;
      }
      if (!res.ok) throw new Error("load failed");
      return res.json();
    })
    .then((data) => {
      if (!data) return;
      state.scores = data.scores || [];
      render();
    })
    .catch(() => {
      state.scores = [];
      render("Scores could not be loaded.");
    });
}

load();
