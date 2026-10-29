"""Dark dashboard skin for the Streamlit advisory desk."""

CSS = """
<style>
:root {
  --bg: #07110d;
  --panel: rgba(16, 32, 24, 0.78);
  --line: rgba(212, 175, 90, 0.35);
  --green: #8ee0a8;
  --gold: #e4c56a;
  --ink: #e7f3ea;
  --muted: #b7c9bc;
}
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 500px at 10% -10%, rgba(46, 125, 80, 0.35), transparent 55%),
    radial-gradient(900px 420px at 100% 0%, rgba(196, 154, 60, 0.16), transparent 50%),
    var(--bg);
  color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
  background: rgba(8, 18, 13, 0.92);
  border-right: 1px solid var(--line);
}
h1, h2, h3, p, label, span { color: var(--ink); }
.hero {
  padding: 8px 4px 18px 4px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 16px;
}
.hero h1 {
  font-size: 2.4rem;
  letter-spacing: 0.08em;
  margin: 0;
  color: var(--gold);
}
.hero p { color: var(--muted); margin: 6px 0 0 0; }
.glass {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
  backdrop-filter: blur(10px);
}
.metric-label { color: var(--muted); font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; }
.metric-value { color: var(--green); font-size: 1.35rem; font-weight: 650; }
.stButton > button {
  background: linear-gradient(180deg, #1f8f55, #14663b);
  color: white;
  border: 1px solid rgba(228, 197, 106, 0.45);
  border-radius: 999px;
  padding: 0.45rem 1rem;
}
.stButton > button:hover { border-color: var(--gold); color: white; }
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea {
  background: rgba(7, 17, 13, 0.8) !important;
  color: var(--ink) !important;
  border-color: rgba(142, 224, 168, 0.25) !important;
}
[data-testid="stMetric"] {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 10px 12px;
}
footer, #MainMenu { visibility: hidden; }
</style>
"""
