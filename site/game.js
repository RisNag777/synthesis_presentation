const beats = [
  {
    day: "Day 1",
    kicker: "Arrival",
    scene:
      "First period. Jordan, a 7th grader with an IEP, comes in eight minutes late, hood up, and sits without opening a notebook.",
    practice: "Predictable routines, plus a quiet check-in",
    choices: [
      {
        id: "office",
        kind: "label",
        label: "Send Jordan to the office for being late.",
        happens: "Jordan leaves the seat they just took. First period goes on without them.",
      },
      {
        id: "checkin",
        kind: "repair",
        label: "Start the warm-up on the board. Check in once the class is working.",
        happens:
          "The warm-up starts on time. Once the class is working, you stop by Jordan’s desk and ask what would help the next few minutes.",
      },
      {
        id: "warning",
        kind: "label",
        label: "Tell Jordan to take his hood off. He is late, and already on a warning.",
        happens: "Jordan doesn’t take the hood off. The notebook stays shut, and the class watches him instead of the warm-up.",
      },
    ],
  },
  {
    day: "Day 1",
    kicker: "The snap",
    scene:
      "A classmate says, “Nice of you to show up.” Jordan shoves the paper off the desk. “Leave me alone.”",
    practice: "A cool-down corner inside the room",
    choices: [
      {
        id: "corner",
        kind: "repair",
        label: "Tell the class to start the warm-up. Let Jordan know the cool-down corner is open, and stay nearby.",
        happens:
          "Jordan takes the corner, still in the room, and comes back four minutes later. The paper goes back on the desk.",
      },
      {
        id: "referral",
        kind: "label",
        label: "Write the referral in front of everyone. Tell Jordan he does not talk to people that way.",
        happens:
          "You write while the class watches. No one has asked Jordan about his day but he's already heard a lot about disrespect",
      },
      {
        id: "hallway",
        kind: "label",
        label: "Jordan, hallway. Now.",
        happens: "Jordan is in the hall. The classmate stays. The paper is still on the floor.",
      },
    ],
  },
  {
    day: "Day 1",
    kicker: "The note",
    scene: "The class moves on. You still have to write down what Jordan did.",
    practice: "An asset-based note that names the unmet need",
    choices: [
      {
        id: "skip",
        kind: "label",
        label: "Skip the note. If it isn't written down, it didn't happen.",
        happens:
          "You skip the note. Tomorrow’s teacher gets a repeat of the same attitude without any knowledge of a potential pattern.",
      },
      {
        id: "defiant",
        kind: "label",
        label: "“Defiant. Refused work. Disrespectful to a peer.”",
        happens: "The next adult who opens the file meets a potential troublemaker. This may set the template for Jordan's mornings going forward.",
      },
      {
        id: "need",
        kind: "repair",
        label: "”Late arrival. Used the corner for four minutes. Finished two problems.”",
        happens:
          "The note that a new adult would read is about a need and a support.",
      },
    ],
  },
  {
    day: "Days 2–11",
    kicker: "Ten days",
    scene: "All week, Jordan shuts down at the same point in first period.",
    practice: "The 2×10: two minutes a day for ten days",
    choices: [
      {
        id: "twobytwo",
        kind: "repair",
        label:
          "You spend two minutes talking to Jordan everyday for ten days - about the bus, a show, anything except the work and his attitude.",
        happens:
          "By day seven Jordan starts the conversation. His mood isn't fixed but you can see a shift in his behavior.",
      },
      {
        id: "chart",
        kind: "label",
        label: "Put a behavior chart on the desk and mark it every period.",
        happens: "Jordan watches you mark the chart. You don't see any change in his behavior.",
      },
      {
        id: "group",
        kind: "label",
        label: "Have the counselor pull Jordan from the class and put him in a separate behavior group.",
        happens: "Jordan is now kept away from his peers. His attitude gets worse.",
      },
    ],
  },
  {
    day: "Day 12",
    kicker: "The call",
    scene:
      "Jordan’s aunt says mornings fall apart because an older brother leaves for work before anyone is up, and the bus is loud.",
    practice: "Ask what helps at home, and put it in the plan",
    choices: [
      {
        id: "isolation",
        kind: "label",
        label: "Name the isolation room as a backup if this keeps happening.",
        happens: "The aunt goes quiet. She doesn't agree with the plan but doesn't know how to rebut.",
      },
      {
        id: "home",
        kind: "label",
        label: "Ask the adults to punish Jordan at home so that he takes first period seriously.",
        happens: "The call ends with a punishment at home but it doesn't fix the problem. The bus is still just as loud tomorrow.",
      },
      {
        id: "helps",
        kind: "repair",
        label:
          "Ask what the adults do at home to help Jordan settle, and add a note along with Jordan's IEP.",
        happens:
          "The aunt tells you that Jordan loves helping out. You assign Jordan to a class job. You see a steady improvement in his behavior.",
      },
    ],
  },
];

const state = {
  name: "",
  started: false,
  step: 0,
  picks: [],
  locked: false,
};

const app = document.querySelector("#app");

function choiceById(beat, id) {
  return beat.choices.find((choice) => choice.id === id);
}

function repairCount() {
  return state.picks.reduce((sum, id, index) => {
    const choice = choiceById(beats[index], id);
    return sum + (choice && choice.kind === "repair" ? 1 : 0);
  }, 0);
}

function outcome(repair) {
  if (repair >= 4) {
    return {
      title: "Jordan eventually settles in!",
      body: "Jordan is settled into first period. You have added notes to the IEP regarding Jordan's morning routine, the corner, and the ten-day check-in, and the class job. A new adult who opens the file will know exactly what Jordan needs to succeed.",
    };
  }
  if (repair >= 2) {
    return {
      title: "Jordan is in and out of the classroom",
      body: "Jordan is still mostly in the classroom but he isn't completely engaged. You made some good calls, but also some bad ones. A new adult who opens the file will know that Jordan needs some more support.",
    };
  }
  return {
    title: "Jordan is barely in the classroom",
    body: "Jordan is not engaged at all. The file says that he is defiant and disrespectful. A new adult will not know how to proceed.",
  };
}

function endingImage(repair) {
  if (repair >= 4) {
    return { src: "right-choice.png", alt: "Michael Jordan smiling" };
  }
  if (repair >= 2) {
    return { src: "mixed-choice.png", alt: "Michael Jordan saying stop it, get some help" };
  }
  return { src: "wrong-choice.jpg", alt: "Michael Jordan crying" };
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function progress(index) {
  const row = el("div", "progress");
  row.setAttribute("aria-hidden", "true");
  beats.forEach((_, i) => {
    const mark = document.createElement("span");
    if (i < index) mark.className = "is-done";
    if (i === index) mark.className = "is-now";
    row.append(mark);
  });
  return row;
}

function renderName() {
  const eyebrow = el("p", "eyebrow", "Beyond the label");
  const title = el("h1", null, "What does this student need?");
  const lede = el("p", "lede", "Enter your name to start first period with Jordan.");
  const form = el("form", "name-form");
  const label = el("label", null, "Your name");
  const input = document.createElement("input");
  input.type = "text";
  input.name = "player";
  input.maxLength = 60;
  input.required = true;
  input.autocomplete = "name";
  input.value = state.name;
  label.htmlFor = "player-name";
  input.id = "player-name";
  const start = el("button", "btn", "Start first period");
  start.type = "submit";
  const error = el("p", "prompt");
  form.append(label, input, start, error);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const name = input.value.trim().replace(/\s+/g, " ");
    if (!name) {
      error.textContent = "Enter your name.";
      input.focus();
      return;
    }
    state.name = name;
    state.started = true;
    render();
  });
  app.replaceChildren(eyebrow, title, lede, form);
  input.focus();
}

function renderPlay() {
  const beat = beats[state.step];
  const chosen = choiceById(beat, state.picks[state.step]);

  const top = el("div", "top");
  top.append(el("p", "eyebrow", "Beyond the label"));
  top.append(el("p", "count", state.step + 1 + " of " + beats.length));

  const title = el("h1", null, "What does this student need?");
  const kicker = el("p", "kicker");
  kicker.append(el("span", null, beat.kicker), el("span", "day", beat.day));
  const scene = el("p", "scene", beat.scene);

  const list = el("ul", "choices");
  beat.choices.forEach((choice) => {
    const item = document.createElement("li");
    const button = el("button", "choice", choice.label);
    button.type = "button";
    button.disabled = state.locked;
    if (chosen && chosen.id === choice.id) button.classList.add("is-selected");
    button.addEventListener("click", () => pick(choice.id));
    item.append(button);
    list.append(item);
  });

  app.replaceChildren(top, progress(state.step), title, kicker, scene, list);

  if (chosen) {
    const box = el("section", "happens " + chosen.kind);
    box.setAttribute("aria-live", "polite");
    box.append(el("h2", null, "What happens next"));
    box.append(el("p", null, chosen.happens));
    if (chosen.kind === "repair") {
      const photo = document.createElement("img");
      photo.className = "choice-photo";
      photo.src = "right-choice.png";
      photo.alt = "Michael Jordan smiling";
      box.append(photo);
    } else {
      const photo = document.createElement("img");
      photo.className = "choice-photo";
      photo.src = "wrong-choice.jpg";
      photo.alt = "Michael Jordan crying";
      box.append(photo);
    }
    const actions = el("div", "actions");
    const next = el(
      "button",
      "btn",
      state.step === beats.length - 1 ? "See the period" : "Next moment"
    );
    next.type = "button";
    next.addEventListener("click", () => {
      state.locked = false;
      state.step += 1;
      render();
    });
    actions.append(next);
    app.append(box, actions);
    next.focus();
  } else {
    app.append(el("p", "prompt", "Choose the move you would make in the room."));
  }
}

function renderEnd() {
  const repair = repairCount();
  const end = outcome(repair);

  const eyebrow = el("p", "eyebrow", "Beyond the label");
  const title = el("h1", null, end.title);
  const lede = el("p", "lede", end.body);
  const picture = endingImage(repair);
  const photo = document.createElement("img");
  photo.className = "ending-photo";
  photo.src = picture.src;
  photo.alt = picture.alt;

  const stats = el("div", "stats");
  const kept = el("div", "stat kept");
  kept.append(el("strong", null, String(repair)));
  kept.append(el("span", null, "Moves that kept Jordan in the classroom"));
  const labeled = el("div", "stat");
  labeled.append(el("strong", null, String(beats.length - repair)));
  labeled.append(el("span", null, "Moves that kept Jordan out of the classroom"));
  stats.append(kept, labeled);

  const heading = el("h2", "section", "What the deck calls these moves");
  const list = el("ol", "moves");
  beats.forEach((beat, index) => {
    const choice = choiceById(beat, state.picks[index]);
    const keptMove = choice && choice.kind === "repair";
    const item = document.createElement("li");
    const name = el("h3");
    name.append(document.createTextNode(beat.day + " · " + beat.kicker));
    name.append(
      el("span", null, "  ·  " + (keptMove ? "Your choice" : "Still available next time"))
    );
    item.append(name, el("p", null, beat.practice), el("p", "yours", choice ? choice.label : ""));
    list.append(item);
  });

  const saved = el("p", "prompt", "Saving your score…");
  const actions = el("div", "actions");
  const again = el("button", "btn", "Play first period again");
  again.type = "button";
  again.addEventListener("click", () => {
    state.step = 0;
    state.picks = [];
    state.locked = false;
    render();
  });
  actions.append(again);

  title.tabIndex = -1;
  app.replaceChildren(eyebrow, title, lede, photo, stats, document.createElement("hr"), heading, list, saved, actions);
  title.focus();
  saveScore(repair, saved);
}

function saveScore(score, node) {
  fetch("/api/scores", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: state.name, score: score }),
  })
    .then((res) => {
      if (!res.ok) throw new Error("save failed");
      node.textContent = "Saved for " + state.name + ".";
    })
    .catch(() => {
      node.textContent = "Your score could not be saved.";
    });
}

function pick(id) {
  if (state.locked) return;
  state.picks[state.step] = id;
  state.locked = true;
  render();
}

function render() {
  if (!state.started) renderName();
  else if (state.step >= beats.length) renderEnd();
  else renderPlay();
  window.scrollTo(0, 0);
}

render();
