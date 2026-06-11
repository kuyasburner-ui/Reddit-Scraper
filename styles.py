import streamlit as st

_CSS = """
<style>
/* ================================================================
   REDDIT SCRAPER — Dark SaaS Theme
   ================================================================ */

/* ── Font imports ──────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=Space+Mono:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block');

/* ── Material Symbols — must come first, before any font override ── */
.material-symbols-rounded,
span[class*="material-symbol"],
span[class*="material-icon"],
i[class*="material"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    font-feature-settings: 'liga' 1 !important;
    -webkit-font-feature-settings: 'liga' 1 !important;
    font-size: 20px !important;
}

/* ── Hide Streamlit chrome + sidebar completely ────────────────── */
/* Suppress everything that flashes before custom CSS settles */
#MainMenu, footer, .stDeployButton,
header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    overflow: hidden !important;
}

/* Expand main content to full width (no sidebar gap) */
.main .block-container {
    max-width: 820px !important;
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin: 0 auto !important;
}

/* ── Base background ───────────────────────────────────────────── */
.stApp {
    background-color: #07070f !important;
}
.stApp > .main {
    background-image: radial-gradient(rgba(0,255,65,0.055) 1px, transparent 1px);
    background-size: 30px 30px;
}

/* ── Typography — scoped to avoid icon-font collisions ────────── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"] p,
[data-testid="stText"] p,
.stApp label {
    font-family: 'DM Sans', system-ui, sans-serif !important;
    color: #7070a0 !important;
    font-size: 0.9rem;
    line-height: 1.65;
}

h1 {
    font-family: 'Orbitron', sans-serif !important;
    color: #00ff41 !important;
    font-size: 2.4rem !important;
    letter-spacing: 2px !important;
    text-shadow: 0 0 28px rgba(0,255,65,0.38), 0 0 60px rgba(0,255,65,0.12) !important;
    animation: title-glow 3s ease-in-out infinite;
}
h2 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ffffff !important;
    font-size: 1.5rem !important;
    letter-spacing: 1px !important;
}
h3 {
    font-family: 'DM Sans', system-ui, sans-serif !important;
    color: #d0d0e8 !important;
    font-weight: 600 !important;
}
a { color: #00ff41 !important; }
a:hover { opacity: 0.8; }

@keyframes title-glow {
    0%,100% { text-shadow: 0 0 28px rgba(0,255,65,0.38), 0 0 60px rgba(0,255,65,0.12); }
    50%      { text-shadow: 0 0 40px rgba(0,255,65,0.56), 0 0 80px rgba(0,255,65,0.2); }
}

/* ── Form ──────────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: #0c0c18 !important;
    border: 1px solid rgba(0,255,65,0.12) !important;
    border-radius: 14px !important;
    padding: 2rem !important;
    box-shadow: 0 2px 40px rgba(0,0,0,0.4) !important;
}

/* ── Text input ────────────────────────────────────────────────── */
[data-testid="stTextInputRootElement"] {
    background: #060612 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInputRootElement"]:focus-within {
    border-color: #00ff41 !important;
    box-shadow: 0 0 0 3px rgba(0,255,65,0.08) !important;
}
[data-testid="stTextInputRootElement"] input {
    color: #ffffff !important;
    background: transparent !important;
    font-family: 'DM Sans', system-ui, sans-serif !important;
    font-size: 0.9rem !important;
    caret-color: #00ff41 !important;
}
input::placeholder { color: #252538 !important; }

/* ── Slider ────────────────────────────────────────────────────── */
[data-testid="stSlider"] p {
    color: #7070a0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSlider"] [role="slider"] {
    box-shadow: 0 0 10px rgba(0,255,65,0.7) !important;
}

/* ── Toggle ────────────────────────────────────────────────────── */
[data-testid="stToggle"] p {
    color: #7070a0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Buttons ───────────────────────────────────────────────────── */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: rgba(0,255,65,0.07) !important;
    color: #00ff41 !important;
    border: 1px solid rgba(0,255,65,0.4) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background: #00ff41 !important;
    color: #07070f !important;
    border-color: #00ff41 !important;
    box-shadow: 0 0 24px rgba(0,255,65,0.3) !important;
}
[data-testid="stFormSubmitButton"] > button {
    font-size: 0.95rem !important;
    padding: 0.65rem 2.5rem !important;
}

/* ── Download button ───────────────────────────────────────────── */
.stDownloadButton > button {
    background: transparent !important;
    color: #40bf70 !important;
    border: 1px solid rgba(64,191,112,0.35) !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(64,191,112,0.08) !important;
    border-color: #40bf70 !important;
    box-shadow: 0 0 16px rgba(64,191,112,0.2) !important;
}

/* ── Progress ──────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: #0c0c18 !important;
    border-radius: 6px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #00aa33, #00ff41) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 14px rgba(0,255,65,0.4) !important;
}
[data-testid="stProgressBar"] p {
    color: #7070a0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
}

/* ── Dataframe ─────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] th {
    background: #0c0c18 !important;
    color: #00ff41 !important;
    border: none !important;
    border-bottom: 1px solid rgba(0,255,65,0.12) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td {
    background: #060612 !important;
    color: #7070a0 !important;
    border: none !important;
    border-bottom: 1px solid rgba(255,255,255,0.03) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: #0d0d20 !important;
    color: #a0a0c0 !important;
}

/* ── Expanders ─────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    background: #0a0a14 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(0,255,65,0.2) !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3) !important;
}
[data-testid="stExpander"] summary {
    color: #a0a0c0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stExpander"] summary:hover { color: #ffffff !important; }
[data-testid="stExpander"] svg { fill: #4a4a6a !important; }

/* ── Alerts ────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #0c0c18 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] p {
    color: #a0a0c0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Divider ───────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.05) !important; }

/* ── Scrollbar ─────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #07070f; }
::-webkit-scrollbar-thumb { background: #1a1a2e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #00ff41; }
::selection { background: rgba(0,255,65,0.18); color: #ffffff; }

/* ================================================================
   CUSTOM COMPONENT STYLES
   ================================================================ */

/* ── Fixed top navbar ──────────────────────────────────────────── */
.r-navbar {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 62px;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    padding: 0 2.5rem;
    background: rgba(7,7,15,0.96);
    border-bottom: 1px solid rgba(0,255,65,0.1);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    z-index: 99999;
    box-shadow: 0 2px 24px rgba(0,0,0,0.6);
}
.r-nav-brand {
    grid-column: 2;
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none !important;
    color: inherit !important;
}
.r-nav-brand-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #00ff41;
    letter-spacing: 2.5px;
    text-shadow: 0 0 14px rgba(0,255,65,0.45);
}
.r-nav-links {
    grid-column: 3;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 2.5rem;
}
.r-nav-link {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    color: #4a4a6a;
    text-decoration: none !important;
    transition: color 0.2s;
    letter-spacing: 0.3px;
    position: relative;
    padding-bottom: 3px;
}
.r-nav-link:hover { color: #c0c0e0 !important; opacity: 1; }
.r-nav-link.active { color: #ffffff !important; }
.r-nav-link.active::after {
    content: '';
    position: absolute;
    bottom: -3px; left: 0; right: 0;
    height: 2px;
    background: #00ff41;
    border-radius: 2px;
    box-shadow: 0 0 8px rgba(0,255,65,0.6);
}
.r-nav-spacer { height: 78px; }

/* ── Badge pill ────────────────────────────────────────────────── */
.r-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid rgba(0,255,65,0.28);
    border-radius: 20px;
    color: #00ff41;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 2.5px;
    padding: 4px 14px;
    background: rgba(0,255,65,0.05);
    text-transform: uppercase;
    margin-bottom: 14px;
}

/* ── Hero ──────────────────────────────────────────────────────── */
.r-hero {
    text-align: center;
    padding: 2.5rem 1rem 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 2rem;
}
.r-hero h1 { margin: 0.4rem 0 0.75rem; font-size: 2.6rem !important; }
.r-hero .subtitle {
    color: #4a4a6a;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── How-it-works steps ────────────────────────────────────────── */
.r-steps {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.r-step {
    flex: 1;
    background: #0c0c18;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1.5rem 1rem 1.25rem;
    text-align: center;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.r-step:hover {
    border-color: rgba(0,255,65,0.2);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.r-step-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: rgba(0,255,65,0.2);
    line-height: 1;
    margin-bottom: 10px;
}
.r-step-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #d0d0e8;
    font-size: 0.9rem;
    margin-bottom: 5px;
}
.r-step-desc {
    font-family: 'DM Sans', sans-serif;
    color: #3a3a5a;
    font-size: 0.76rem;
    line-height: 1.55;
}

/* ── Stats bar ─────────────────────────────────────────────────── */
.r-stats {
    display: flex;
    justify-content: space-around;
    padding: 2rem 1rem;
    background: #0a0a14;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    margin: 1.5rem 0;
}
.r-stat { text-align: center; }
.r-stat-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.4);
    line-height: 1;
    display: block;
    margin-bottom: 7px;
}
.r-stat-label {
    font-family: 'DM Sans', sans-serif;
    color: #3a3a5a;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Success banner ────────────────────────────────────────────── */
.r-success {
    background: #090914;
    border: 1px solid rgba(0,255,65,0.18);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0.75rem 0;
}
.r-success-dot {
    width: 8px; height: 8px;
    background: #00ff41;
    border-radius: 50%;
    box-shadow: 0 0 8px #00ff41;
    flex-shrink: 0;
    animation: dot-pulse 2s ease-in-out infinite;
}
@keyframes dot-pulse {
    0%,100% { box-shadow: 0 0 6px #00ff41; }
    50%      { box-shadow: 0 0 14px #00ff41, 0 0 28px rgba(0,255,65,0.4); }
}
.r-success-text {
    font-family: 'DM Sans', sans-serif;
    color: #a0a0c0;
    font-size: 0.88rem;
}
.r-success-text strong { color: #00ff41; }

/* ── Section header ────────────────────────────────────────────── */
.r-section-header { margin: 2rem 0 1rem; }
.r-section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.6rem;
    font-weight: 600;
    color: #00ff41;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.r-section-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    color: #ffffff;
    letter-spacing: 1px;
    font-weight: 600;
}

/* ── Post detail components ────────────────────────────────────── */
.r-post-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}
.r-tag {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    color: #4a4a6a;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 4px;
    padding: 2px 8px;
}
.r-tag.green {
    color: #00cc44;
    background: rgba(0,204,68,0.06);
    border-color: rgba(0,204,68,0.2);
}
.r-comment-author {
    font-family: 'Space Mono', monospace;
    color: #40a060;
    font-size: 0.78rem;
}
.r-divider { border: none; border-top: 1px solid rgba(255,255,255,0.04); margin: 10px 0; }

/* ── Footer ────────────────────────────────────────────────────── */
.r-footer {
    text-align: center;
    padding: 2rem 0 1rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 3rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    color: #22223a;
    letter-spacing: 0.3px;
}

/* ── CSS radar logo (pure divs — no SVG to sanitise) ──────────── */
.r-radar {
    width: 30px; height: 30px;
    position: relative;
    flex-shrink: 0;
}
.r-radar-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid #00ff41;
}
.r-radar-ring-outer { inset: 0;    opacity: 0.18; }
.r-radar-ring-mid   { inset: 5px;  opacity: 0.35; }
.r-radar-ring-inner { inset: 10px; opacity: 0.65; }
.r-radar-dot {
    position: absolute;
    width: 5px; height: 5px;
    background: #00ff41;
    border-radius: 50%;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 7px #00ff41;
}
.r-radar-sweep {
    position: absolute;
    top: 50%; left: 50%;
    width: 44%; height: 1.5px;
    transform-origin: 0 50%;
    background: linear-gradient(90deg, rgba(0,255,65,0.9), transparent);
    animation: r-spin 3.5s linear infinite;
}
@keyframes r-spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


_RADAR_HTML = (
    '<div class="r-radar">'
    '<div class="r-radar-ring r-radar-ring-outer"></div>'
    '<div class="r-radar-ring r-radar-ring-mid"></div>'
    '<div class="r-radar-ring r-radar-ring-inner"></div>'
    '<div class="r-radar-dot"></div>'
    '<div class="r-radar-sweep"></div>'
    '</div>'
)


def navbar(current: str = "home", uid: str = ""):
    history_href = f"/History?uid={uid}" if uid else "/History"
    links = [
        ("home",    "/",           "Home"),
        ("history", history_href,  "Scan History"),
    ]
    links_html = "".join(
        f'<a href="{href}" class="r-nav-link {"active" if key == current else ""}"'
        f' target="_self">{label}</a>'
        for key, href, label in links
    )
    st.markdown(
        f'<div class="r-navbar">'
        f'  <a href="/" class="r-nav-brand" target="_self">'
        f'    {_RADAR_HTML}'
        f'    <span class="r-nav-brand-text">Reddit Scraper</span>'
        f'  </a>'
        f'  <nav class="r-nav-links">{links_html}</nav>'
        f'</div>'
        f'<div class="r-nav-spacer"></div>',
        unsafe_allow_html=True,
    )


def hero(title: str, badge: str = "", subtitle: str = ""):
    badge_html = f'<div class="r-badge">&#9632; {badge} &#9632;</div>' if badge else ""
    sub_html   = f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="r-hero">{badge_html}<h1>{title}</h1>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def section_header(label: str, title: str = ""):
    title_html = f'<div class="r-section-title">{title}</div>' if title else ""
    st.markdown(
        f'<div class="r-section-header">'
        f'<div class="r-section-label">// {label}</div>'
        f'{title_html}</div>',
        unsafe_allow_html=True,
    )


def success_banner(text: str):
    st.markdown(
        f'<div class="r-success">'
        f'<div class="r-success-dot"></div>'
        f'<div class="r-success-text">{text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def how_it_works():
    st.markdown(
        """
        <div class="r-steps">
          <div class="r-step">
            <div class="r-step-num">01</div>
            <div class="r-step-title">Enter Query</div>
            <div class="r-step-desc">Type any topic, keyword, or phrase to search across Reddit</div>
          </div>
          <div class="r-step">
            <div class="r-step-num">02</div>
            <div class="r-step-title">Scrape</div>
            <div class="r-step-desc">Posts and comments are fetched live — no API key needed</div>
          </div>
          <div class="r-step">
            <div class="r-step-num">03</div>
            <div class="r-step-title">Export</div>
            <div class="r-step-desc">Download results as CSV or plain text for analysis</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stats_bar():
    st.markdown(
        """
        <div class="r-stats">
          <div class="r-stat">
            <span class="r-stat-num">1,000</span>
            <span class="r-stat-label">Max Posts Per Run</span>
          </div>
          <div class="r-stat">
            <span class="r-stat-num">20</span>
            <span class="r-stat-label">Comments Per Post</span>
          </div>
          <div class="r-stat">
            <span class="r-stat-num">100%</span>
            <span class="r-stat-label">Free — No API Key</span>
          </div>
          <div class="r-stat">
            <span class="r-stat-num">CSV</span>
            <span class="r-stat-label">+ TXT Export</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        '<div class="r-footer">'
        'Reddit Scraper &nbsp;&middot;&nbsp; Free Intelligence Tool'
        ' &nbsp;&middot;&nbsp; No Data Stored Permanently'
        '</div>',
        unsafe_allow_html=True,
    )
