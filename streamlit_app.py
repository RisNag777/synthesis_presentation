"""Beyond the label, served by Streamlit and stored in Turso."""

import hmac
import os
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
HOST_PASSWORD_DEFAULT = "SpaceJam"

BEATS = [
    {
        "day": "Day 1",
        "kicker": "Arrival",
        "scene": "First period. Jordan, a 7th grader with an IEP, comes in eight minutes late, hood up, and sits without opening a notebook.",
        "practice": "Predictable routines, plus a quiet check-in",
        "choices": [
            {
                "id": "office",
                "kind": "label",
                "label": "Send Jordan to the office for being late.",
                "happens": "Jordan leaves the seat they just took. First period goes on without them.",
            },
            {
                "id": "checkin",
                "kind": "repair",
                "label": "Start the warm-up on the board. Check in once the class is working.",
                "happens": "The warm-up starts on time. Once the class is working, you stop by Jordan’s desk and ask what would help the next few minutes.",
            },
            {
                "id": "warning",
                "kind": "label",
                "label": "Tell Jordan to take his hood off. He is late, and already on a warning.",
                "happens": "Jordan doesn’t take the hood off. The notebook stays shut, and the class watches him instead of the warm-up.",
            },
        ],
    },
    {
        "day": "Day 1",
        "kicker": "The snap",
        "scene": "A classmate says, “Nice of you to show up.” Jordan shoves the paper off the desk. “Leave me alone.”",
        "practice": "A cool-down corner inside the room",
        "choices": [
            {
                "id": "corner",
                "kind": "repair",
                "label": "Tell the class to start the warm-up. Let Jordan know the cool-down corner is open, and stay nearby.",
                "happens": "Jordan takes the corner, still in the room, and comes back four minutes later. The paper goes back on the desk.",
            },
            {
                "id": "referral",
                "kind": "label",
                "label": "Write the referral in front of everyone. Tell Jordan he does not talk to people that way.",
                "happens": "You write while the class watches. No one has asked Jordan about his day but he's already heard a lot about disrespect",
            },
            {
                "id": "hallway",
                "kind": "label",
                "label": "Jordan, hallway. Now.",
                "happens": "Jordan is in the hall. The classmate stays. The paper is still on the floor.",
            },
        ],
    },
    {
        "day": "Day 1",
        "kicker": "The note",
        "scene": "The class moves on. You still have to write down what Jordan did.",
        "practice": "An asset-based note that names the unmet need",
        "choices": [
            {
                "id": "skip",
                "kind": "label",
                "label": "Skip the note. If it isn't written down, it didn't happen.",
                "happens": "You skip the note. Tomorrow’s teacher gets a repeat of the same attitude without any knowledge of a potential pattern.",
            },
            {
                "id": "defiant",
                "kind": "label",
                "label": "“Defiant. Refused work. Disrespectful to a peer.”",
                "happens": "The next adult who opens the file meets a potential troublemaker. This may set the template for Jordan's mornings going forward.",
            },
            {
                "id": "need",
                "kind": "repair",
                "label": "”Late arrival. Used the corner for four minutes. Finished two problems.”",
                "happens": "The note that a new adult would read is about a need and a support.",
            },
        ],
    },
    {
        "day": "Days 2–11",
        "kicker": "Ten days",
        "scene": "All week, Jordan shuts down at the same point in first period.",
        "practice": "The 2×10: two minutes a day for ten days",
        "choices": [
            {
                "id": "twobytwo",
                "kind": "repair",
                "label": "You spend two minutes talking to Jordan everyday for ten days - about the bus, a show, anything except the work and his attitude.",
                "happens": "By day seven Jordan starts the conversation. His mood isn't fixed but you can see a shift in his behavior.",
            },
            {
                "id": "chart",
                "kind": "label",
                "label": "Put a behavior chart on the desk and mark it every period.",
                "happens": "Jordan watches you mark the chart. You don't see any change in his behavior.",
            },
            {
                "id": "group",
                "kind": "label",
                "label": "Have the counselor pull Jordan from the class and put him in a separate behavior group.",
                "happens": "Jordan is now kept away from his peers. His attitude gets worse.",
            },
        ],
    },
    {
        "day": "Day 12",
        "kicker": "The call",
        "scene": "Jordan’s aunt says mornings fall apart because an older brother leaves for work before anyone is up, and the bus is loud.",
        "practice": "Ask what helps at home, and put it in the plan",
        "choices": [
            {
                "id": "isolation",
                "kind": "label",
                "label": "Name the isolation room as a backup if this keeps happening.",
                "happens": "The aunt goes quiet. She doesn't agree with the plan but doesn't know how to rebut.",
            },
            {
                "id": "home",
                "kind": "label",
                "label": "Ask the adults to punish Jordan at home so that he takes first period seriously.",
                "happens": "The call ends with a punishment at home but it doesn't fix the problem. The bus is still just as loud tomorrow.",
            },
            {
                "id": "helps",
                "kind": "repair",
                "label": "Ask what the adults do at home to help Jordan settle, and add a note along with Jordan's IEP.",
                "happens": "The aunt tells you that Jordan loves helping out. You assign Jordan to a class job. You see a steady improvement in his behavior.",
            },
        ],
    },
]


def secret(key, default=None):
    try:
        if key in st.secrets and st.secrets[key]:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key) or default


def host_password():
    return secret("HOST_PASSWORD", HOST_PASSWORD_DEFAULT)


def password_ok(given):
    expected = host_password().strip().encode()
    return hmac.compare_digest((given or "").strip().encode(), expected)


def database_configured():
    return bool(secret("TURSO_DATABASE_URL") and secret("TURSO_AUTH_TOKEN"))


def connect():
    url = secret("TURSO_DATABASE_URL")
    token = secret("TURSO_AUTH_TOKEN")
    if not url or not token:
        raise RuntimeError("Turso is not configured.")
    if url.startswith("turso://"):
        import turso_serverless

        return turso_serverless.connect(url, auth_token=token)
    import libsql

    return libsql.connect(database=url, auth_token=token)


def fetchall(cursor):
    if hasattr(cursor, "fetchall"):
        return cursor.fetchall()
    return list(cursor)


def with_db(work):
    conn = connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                played_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        result = work(conn)
        conn.commit()
        return result
    finally:
        conn.close()


def save_score(name, score):
    def work(conn):
        conn.execute(
            "INSERT INTO scores (name, score) VALUES (?, ?)",
            (name, score),
        )

    with_db(work)


def list_scores():
    def work(conn):
        cursor = conn.execute(
            "SELECT name, score, played_at FROM scores ORDER BY played_at DESC, id DESC"
        )
        return fetchall(cursor)

    return with_db(work)


def delete_player(name):
    def work(conn):
        cursor = conn.execute("DELETE FROM scores WHERE name = ?", (name,))
        return cursor.rowcount if hasattr(cursor, "rowcount") else None

    return with_db(work)


def choice_by_id(beat, choice_id):
    for choice in beat["choices"]:
        if choice["id"] == choice_id:
            return choice
    return None


def repair_count():
    total = 0
    for index, choice_id in enumerate(st.session_state.picks):
        choice = choice_by_id(BEATS[index], choice_id)
        if choice and choice["kind"] == "repair":
            total += 1
    return total


def outcome(repair):
    if repair >= 4:
        return (
            "Jordan eventually settles in!",
            "Jordan is settled into first period. You have added notes to the IEP regarding Jordan's morning routine, the corner, and the ten-day check-in, and the class job. A new adult who opens the file will know exactly what Jordan needs to succeed.",
        )
    if repair >= 2:
        return (
            "Jordan is in and out of the classroom",
            "Jordan is still mostly in the classroom but he isn't completely engaged. You made some good calls, but also some bad ones. A new adult who opens the file will know that Jordan needs some more support.",
        )
    return (
        "Jordan is barely in the classroom",
        "Jordan is not engaged at all. The file says that he is defiant and disrespectful. A new adult will not know how to proceed.",
    )


def ending_image(repair):
    if repair >= 4:
        return SITE / "right-choice.png", "Michael Jordan smiling"
    if repair >= 2:
        return SITE / "mixed-choice.png", "Michael Jordan saying stop it, get some help"
    return SITE / "wrong-choice.jpg", "Michael Jordan crying"


def init_state():
    defaults = {
        "player": "",
        "started": False,
        "step": 0,
        "picks": [],
        "locked": False,
        "saved": False,
        "save_message": "",
        "host_ok": False,
        "confirm_delete": "",
        "host_error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_theme():
    st.markdown(
        """
        <style>
          .stApp { background: #f6f4f1; color: #1c1917; }
          .block-container { max-width: 760px; padding-top: 2.5rem; }
          .eyebrow {
            margin: 0 0 0.4rem;
            color: #1f4e5f;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }
          .scene { font-size: 1.15rem; line-height: 1.45; }
          div[data-testid="stButton"] > button {
            width: 100%;
            border: 1px solid #ddd8d2;
            background: #ffffff;
            color: #1c1917;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            text-align: left;
            line-height: 1.4;
          }
          div[data-testid="stButton"] > button:hover {
            border-color: #1f4e5f;
            color: #1f4e5f;
          }
          div[data-testid="stButton"] > button[kind="primary"],
          div[data-testid="stFormSubmitButton"] > button {
            background: #1f4e5f;
            color: #ffffff;
            border-color: #1f4e5f;
            text-align: center;
          }
          footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_name():
    st.markdown('<p class="eyebrow">Beyond the label</p>', unsafe_allow_html=True)
    st.title("What does this student need?")
    st.write("Enter your name to start first period with Jordan.")
    with st.form("player-form"):
        name = st.text_input("Your name", max_chars=60)
        start = st.form_submit_button("Start first period")
    if start:
        cleaned = " ".join(name.split())
        if not cleaned:
            st.write("Enter your name.")
            return
        st.session_state.player = cleaned
        st.session_state.started = True
        st.rerun()


def render_play():
    step = st.session_state.step
    beat = BEATS[step]
    picks = st.session_state.picks
    chosen = choice_by_id(beat, picks[step]) if step < len(picks) and picks[step] else None

    left, right = st.columns([4, 1])
    left.markdown('<p class="eyebrow">Beyond the label</p>', unsafe_allow_html=True)
    right.markdown(f"{step + 1} of {len(BEATS)}")
    done = "● " * step
    now = "● "
    later = "○ " * (len(BEATS) - step - 1)
    st.markdown(f"<p style='color:#1f4e5f; letter-spacing:0.15em'>{done}{now}{later}</p>", unsafe_allow_html=True)
    st.title("What does this student need?")
    st.markdown(f"**{beat['kicker']}** · {beat['day']}")
    st.markdown(f"<p class='scene'>{beat['scene']}</p>", unsafe_allow_html=True)

    for choice in beat["choices"]:
        selected = chosen and chosen["id"] == choice["id"]
        label = choice["label"]
        if selected:
            label = "●  " + label
        if st.button(
            label,
            key=f"choice-{step}-{choice['id']}",
            disabled=st.session_state.locked,
        ):
            while len(st.session_state.picks) <= step:
                st.session_state.picks.append(None)
            st.session_state.picks[step] = choice["id"]
            st.session_state.locked = True
            st.rerun()

    if not chosen:
        st.caption("Choose the move you would make in the room.")
        return

    st.subheader("What happens next")
    st.write(chosen["happens"])
    photo = SITE / ("right-choice.png" if chosen["kind"] == "repair" else "wrong-choice.jpg")
    caption = "Michael Jordan smiling" if chosen["kind"] == "repair" else "Michael Jordan crying"
    st.image(str(photo), caption=caption, width=280)
    label = "See the period" if step == len(BEATS) - 1 else "Next moment"
    if st.button(label, type="primary", key=f"next-{step}"):
        st.session_state.locked = False
        st.session_state.step += 1
        st.rerun()


def render_end():
    repair = repair_count()
    title, body = outcome(repair)
    st.markdown('<p class="eyebrow">Beyond the label</p>', unsafe_allow_html=True)
    st.title(title)
    st.write(body)
    photo, caption = ending_image(repair)
    st.image(str(photo), caption=caption, width=420)
    kept, missed = st.columns(2)
    kept.metric("In the classroom", f"{repair} / 5")
    missed.metric("Out of the classroom", f"{len(BEATS) - repair} / 5")
    st.divider()
    st.subheader("What the deck calls these moves")
    for index, beat in enumerate(BEATS):
        choice = choice_by_id(beat, st.session_state.picks[index])
        kept_move = choice and choice["kind"] == "repair"
        mark = "Your choice" if kept_move else "Still available next time"
        st.markdown(f"**{beat['day']} · {beat['kicker']}** · {mark}")
        st.caption(beat["practice"])
        if choice:
            st.write(choice["label"])

    if not st.session_state.saved:
        try:
            save_score(st.session_state.player, repair)
            st.session_state.save_message = f"Saved for {st.session_state.player}."
        except Exception:
            st.session_state.save_message = "Your score could not be saved."
        st.session_state.saved = True

    st.write(st.session_state.save_message)
    if st.button("Play first period again", type="primary"):
        st.session_state.step = 0
        st.session_state.picks = []
        st.session_state.locked = False
        st.session_state.saved = False
        st.session_state.save_message = ""
        st.rerun()


def render_game():
    if not st.session_state.started:
        render_name()
    elif st.session_state.step >= len(BEATS):
        render_end()
    else:
        render_play()


def render_host():
    st.markdown('<p class="eyebrow">Host</p>', unsafe_allow_html=True)
    st.title("Scores")
    if not database_configured():
        st.write("Turso is not connected yet. Add TURSO_DATABASE_URL and TURSO_AUTH_TOKEN to the Streamlit secrets.")
        return
    if not st.session_state.host_ok:
        st.write("Enter the host password to see saved plays.")
        with st.form("host-gate"):
            password = st.text_input("Password", type="password")
            open_scores = st.form_submit_button("Open scores")
        if open_scores:
            if password_ok(password):
                st.session_state.host_ok = True
                st.session_state.host_error = ""
                st.rerun()
            st.session_state.host_error = "That password is not right."
        if st.session_state.host_error:
            st.write(st.session_state.host_error)
        return

    try:
        rows = list_scores()
    except Exception:
        st.write("Scores could not be loaded.")
        return

    count = len(rows)
    st.write("1 play saved." if count == 1 else f"{count} plays saved.")
    if rows:
        frame = pd.DataFrame(rows, columns=["Name", "Score", "Played"])
        frame["Score"] = frame["Score"].map(lambda score: f"{score} / 5")
        st.dataframe(frame, hide_index=True, use_container_width=True)
        names = sorted({row[0] for row in rows}, key=str.lower)
        selected = st.selectbox("Player", names)
        if st.button("Delete", key="ask-delete"):
            st.session_state.confirm_delete = selected
        if st.session_state.confirm_delete:
            st.write(f"Delete {st.session_state.confirm_delete} and every saved play for that name?")
            yes, no = st.columns(2)
            if yes.button("Delete player", type="primary"):
                try:
                    delete_player(st.session_state.confirm_delete)
                    st.session_state.confirm_delete = ""
                    st.rerun()
                except Exception:
                    st.write("That player could not be deleted.")
            if no.button("Keep player"):
                st.session_state.confirm_delete = ""
                st.rerun()
    else:
        st.write("No scores yet.")


def main():
    st.set_page_config(page_title="Beyond the label", layout="centered")
    init_state()
    apply_theme()
    if st.query_params.get("host") == "1":
        render_host()
    else:
        render_game()


main()
