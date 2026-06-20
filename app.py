import streamlit as st
import re
from google import genai
from google.genai import types
import json
import os
import time

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

@st.cache_data
def load_spidey_vault():
    watch_orders = {
        "Cinematic Timeline": ["1. Spider-Man (2002)", "2. Spider-Man 2", "3. Spider-Man 3", "4. The Amazing Spider-Man", "5. The Amazing Spider-Man 2", "6. Captain America: Civil War", "7. Spider-Man: Homecoming", "8. Into the Spider-Verse", "9. Spider-Man: Far From Home", "10. Spider-Man: No Way Home", "11. Across the Spider-Verse"]
    }
    comics_order = {
        "Classic Era": ["Amazing Fantasy #15", "The Amazing Spider-Man #1-38"], 
        "Modern Era": ["Ultimate Spider-Man #1-160", "Superior Spider-Man"],
        "Brand New Day Era": ["The Amazing Spider-Man #546-647 (Brand New Day)"]
    }
    games_database = {
        "Marvel's Spider-Man Remastered": {"year": "2022", "minimum_specs": "Intel i3 / 8GB RAM / GTX 950", "store_link": "https://store.steampowered.com/app/1817070/"},
        "Marvel's Spider-Man 2": {"year": "2025 (PC)", "minimum_specs": "Intel i3-8100 / 16GB RAM / GTX 1650", "store_link": "https://store.steampowered.com/app/2651280/"}
    }
    music_tracks = [{"title": "Sunflower", "artist": "Post Malone", "movie": "Into the Spider-Verse", "query": "Sunflower+Post+Malone"}]
    
    multiverse_bios = {
        "Peter Parker (Earth-616)": {"origin": "Bitten by a radioactive spider.", "powers": "Strength, speed, Spider-Sense, wall-crawling.", "fun_fact": "Invented his own web-shooters."},
        "Miles Morales (Earth-1610)": {"origin": "Bitten by a genetically engineered spider.", "powers": "Venom blasts and invisibility.", "fun_fact": "Took up the mantle after the original Peter Parker died."},
        "Spider-Gwen (Earth-65)": {"origin": "Gwen Stacy bitten instead of Peter.", "powers": "Standard Spider-powers.", "fun_fact": "Plays drums in 'The Mary Janes'."},
        "Spider-Man 2099 (Earth-928)": {"origin": "Futuristic genetic experiment.", "powers": "Organic webbing, venom fangs, talons.", "fun_fact": "Costume is made of Unstable Molecule Fabric."},
        "Spider-Ham (Earth-8311)": {"origin": "Spider bitten by a radioactive pig.", "powers": "Cartoon physics.", "fun_fact": "Enemies include Ducktor Doom."},
        "Spider-Man Noir (Earth-90214)": {"origin": "1930s spider-god idol.", "powers": "Organic dark webbing.", "fun_fact": "Investigative reporter who uses firearms."}
    }
    
    upcoming_schedule = [
        {"title": "Spider-Man: Brand New Day (MCU Spider-Man 4)", "date": "July 31, 2026", "type": "Live Action Movie"},
        {"title": "Spider-Man: Beyond the Spider-Verse", "date": "TBD", "type": "Animated Movie"},
        {"title": "Spider-Noir", "date": "Late 2026", "type": "Live Action Series (Amazon)"}
    ]
    
    return watch_orders, comics_order, games_database, music_tracks, multiverse_bios, upcoming_schedule

WATCH_ORDERS, COMICS_ORDER, GAMES_DB, MUSIC_TRACKS, MULTIVERSE_BIOS, UPCOMING_RELEASES = load_spidey_vault()


st.set_page_config(page_title="Spider-Verse Hub", page_icon="🕷️", layout="centered")
st.markdown("<style>.stApp { background-image: url('https://www.transparenttextures.com/patterns/cobweb.png'); background-color: #0E1117; }</style>", unsafe_allow_html=True)
if os.path.exists("spiderman.png"):
    st.image("spiderman.png", width=150)

st.markdown("<h1 style='text-align: center;'>🕷️ Spider-Verse Hub AI</h1>", unsafe_allow_html=True)

# Intro button
if "intro_counter" not in st.session_state:
    st.session_state.intro_counter = 0
if st.button("🔊 Play Intro"):

    st.session_state.intro_counter += 1

    st.components.v1.html(
        f"""
        <script>
        speechSynthesis.cancel();

        const msg = new SpeechSynthesisUtterance(
    "Hey there. I'm your friendly neighborhood Spider-Man. What can I help you with today?"
);

const voices = speechSynthesis.getVoices();

msg.voice =
    msg.voice =
    msg.voice =
    voices.find(v => v.name === "Google UK English Male") ||
    voices.find(v => v.name === "Microsoft George") ||
    voices.find(v => v.name === "Google US English");

msg.rate = 1.02;
msg.pitch = 1.20;
msg.volume = 1.0;

        speechSynthesis.speak(msg);
        </script>

        <div style="display:none">
            {st.session_state.intro_counter}
        </div>
        """,
        height=0,
    )

MEMORY_FILE = "spidey_memory.json"
st.markdown("""
<style>
div[data-testid="stButton"] button {
    width:auto !important;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([10,1])

with col2:
    if st.button("🗑"):
        st.session_state.history = []

        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if "history" not in st.session_state:

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            st.session_state.history = json.load(f)
    else:
        st.session_state.history = []
for msg in st.session_state.history:

    avatar = "🕷️" if msg["role"] == "assistant" else "👤"

    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

conversation_context = "\n".join(
    f"{msg['role']}: {msg['content']}"
    for msg in st.session_state.history[-100:]
)


if query_str := st.chat_input("Ask about Spider-Man..."):

    st.session_state.history.append({
        "role": "user",
        "content": query_str
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(query_str)

    with st.spinner("Swinging through the web..."):

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
               contents=f""" You are Peter Parker from The Amazing Spider-Man.

Rules:
1. Answer the question directly first.
2. Then add a short Spider-Man style comment.
3. Never give long roleplay introductions.
4. Use Google Search results whenever available.
5. Remember previous conversations.
6. Be concise and accurate.
               Conversation History: 
               {conversation_context} 
               Current User Question: 
               {query_str} 
""",
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}]
                )
            )

            ai_out = response.text
            with st.chat_message("assistant"):
                st.markdown(ai_out)
            with st.chat_message("assistant", avatar="🕷️"):
                st.markdown(ai_out)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🔊 Speak", key=f"speak_{len(st.session_state.history)}"):
                        st.components.v1.html(
                            f"""
                            <script>
                            speechSynthesis.cancel();

                            const msg = new SpeechSynthesisUtterance(`{ai_out}`);

                            msg.rate = 0.92;
                            msg.pitch = 1.02;
                            msg.volume = 1;

                            speechSynthesis.speak(msg);
                            </script>
                            """,
                            height=0,
                        )

                with col2:
                    if st.button("⏹ Stop", key=f"stop_{len(st.session_state.history)}"):
                        st.components.v1.html(
                            f"""
                            <script>
                            speechSynthesis.cancel();
                            ...
                            speechSynthesis.speak(msg);
                            </script>
                            """,
                            height=0
)


        except Exception as e:
                ai_out = f"❌ Error: {str(e)}"

    st.session_state.history.append({
        "role": "assistant",
        "content": ai_out
    })
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.history, f, indent=2, ensure_ascii=False)

        st.rerun()
