import re
from io import BytesIO
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pypdf import PdfReader

# =========================================================
# SkillMatch AI — Streamlit career companion
# Run: streamlit run app.py
# =========================================================

st.set_page_config(
    page_title="SkillMatch AI | Career Companion",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- DATA ---------------------------

SKILLS = [
    "python", "java", "c++", "c", "javascript", "typescript", "html",
    "css", "react", "node.js", "sql", "mysql", "postgresql", "mongodb",
    "streamlit", "flask", "django", "fastapi", "machine learning",
    "deep learning", "data analysis", "data visualization", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "power bi",
    "tableau", "excel", "git", "github", "docker", "kubernetes",
    "aws", "azure", "gcp", "linux", "rest api", "api", "communication",
    "leadership", "problem solving", "teamwork", "project management",
    "figma", "ui/ux", "computer vision", "nlp", "statistics",
]

CAREER_ROLES = {
    "Python Developer": ["python", "django", "flask", "fastapi", "sql", "git", "rest api"],
    "Data Analyst": ["python", "sql", "excel", "power bi", "tableau", "pandas", "statistics", "data visualization"],
    "Machine Learning Engineer": ["python", "machine learning", "deep learning", "scikit-learn", "tensorflow", "pytorch", "statistics"],
    "Frontend Developer": ["html", "css", "javascript", "typescript", "react", "figma", "git"],
    "Full Stack Developer": ["html", "css", "javascript", "react", "node.js", "sql", "mongodb", "rest api", "git"],
    "Cloud / DevOps Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "linux", "git"],
    "Business Intelligence Analyst": ["sql", "power bi", "tableau", "excel", "data visualization", "statistics"],
}

LEARNING_RESOURCES = {
    "python": "https://www.python.org/about/gettingstarted/",
    "java": "https://dev.java/learn/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
    "html": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
    "css": "https://developer.mozilla.org/en-US/docs/Learn/CSS",
    "react": "https://react.dev/learn",
    "sql": "https://www.w3schools.com/sql/",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "deep learning": "https://www.deeplearning.ai/",
    "pandas": "https://pandas.pydata.org/docs/getting_started/index.html",
    "numpy": "https://numpy.org/learn/",
    "power bi": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
    "tableau": "https://www.tableau.com/learn/training",
    "git": "https://git-scm.com/doc",
    "docker": "https://docs.docker.com/get-started/",
    "aws": "https://skillbuilder.aws/",
    "communication": "https://www.coursera.org/learn/wharton-communication-skills",
    "data analysis": "https://www.kaggle.com/learn",
    "streamlit": "https://docs.streamlit.io/",
    "flask": "https://flask.palletsprojects.com/en/stable/tutorial/",
    "django": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
    "mongodb": "https://learn.mongodb.com/",
    "postgresql": "https://www.postgresql.org/docs/",
    "typescript": "https://www.typescriptlang.org/docs/",
    "node.js": "https://nodejs.org/en/learn",
    "linux": "https://linuxjourney.com/",
}

TECH_QUESTIONS = {
    "Python": [
        "What is the difference between a list and a tuple?",
        "Explain Python decorators and give a practical use case.",
        "What is the difference between == and is?",
        "How does exception handling work in Python?",
        "What are list comprehensions?",
    ],
    "Data Analysis": [
        "How would you handle missing values in a dataset?",
        "Explain the difference between a JOIN and a UNION in SQL.",
        "When would you use a bar chart instead of a line chart?",
        "What is the difference between correlation and causation?",
        "How would you explain an analytical finding to a non-technical stakeholder?",
    ],
    "Web Development": [
        "What happens when a user enters a URL in a browser?",
        "Explain the difference between frontend and backend validation.",
        "What is a REST API?",
        "How do you make a web page responsive?",
        "How would you debug a slow web application?",
    ],
    "Machine Learning": [
        "Explain supervised and unsupervised learning.",
        "What is overfitting, and how can you reduce it?",
        "Why do we split data into training and testing sets?",
        "What is the purpose of feature scaling?",
        "How would you select an evaluation metric for a model?",
    ],
    "General": [
        "Walk me through a project you are proud of.",
        "How do you approach debugging an unfamiliar codebase?",
        "How do you learn a new technology?",
        "Describe a technical challenge you solved.",
        "How do you prioritize tasks under a deadline?",
    ],
}

HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why are you interested in this role?",
    "What is one strength you would bring to this team?",
    "Describe a time you received difficult feedback.",
    "Tell me about a challenge you faced and how you handled it.",
    "Where would you like to develop professionally over the next few years?",
]

# ------------------------- STYLING ------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --ink: #241b3a;
    --muted: #77718b;
    --purple: #7655d9;
    --purple-dark: #5c3db8;
    --lavender: #f1edff;
    --line: #e9e4f5;
    --surface: #ffffff;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f8f7fc; color: var(--ink); }
.block-container { max-width: 1440px; padding-top: 1.7rem; padding-bottom: 3rem; }
h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: var(--ink); letter-spacing: -0.5px; }
h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 700 !important; }
h1 a, h2 a, h3 a { display: none !important; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--muted); }
[data-testid="stRadio"] label { padding: 7px 10px; border-radius: 10px; }
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    border-radius: 11px !important; border: 1px solid #ded5fa !important;
    font-weight: 700 !important; transition: .2s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--purple) !important; transform: translateY(-1px);
}
.stProgress > div > div > div > div { background: linear-gradient(90deg,#9a7cf0,#6d4bd1); }
.hero {
    background: radial-gradient(circle at 85% 20%, rgba(255,255,255,.28), transparent 25%),
                linear-gradient(120deg,#6c4bc5 0%,#8c70e8 55%,#b19af4 100%);
    color: white; border-radius: 24px; padding: 42px 44px; margin: 4px 0 26px;
    box-shadow: 0 16px 40px rgba(105,76,190,.18);
}
.hero h1 { color: white !important; font-size: clamp(2rem,4vw,3.15rem) !important; margin: 12px 0 10px; }
.hero p { color: rgba(255,255,255,.9); font-size: 1.05rem; max-width: 760px; line-height: 1.7; }
.hero-badge { display:inline-block; background:rgba(255,255,255,.17); border:1px solid rgba(255,255,255,.28);
    border-radius:30px; padding:7px 13px; color:white; font-size:.75rem; font-weight:700; letter-spacing:1px; }
.feature-card, .panel, .metric-card {
    background:white; border:1px solid var(--line); border-radius:18px;
    box-shadow:0 5px 20px rgba(44,31,78,.035);
}
.feature-card { padding:22px; min-height:175px; margin-bottom:14px; }
.feature-icon { font-size:1.8rem; margin-bottom:12px; }
.feature-card h3 { font-size:1.05rem; margin:0 0 8px; }
.feature-card p { color:var(--muted); font-size:.9rem; line-height:1.55; margin:0; }
.panel { padding:22px; margin-bottom:18px; }
.metric-card { padding:18px 20px; min-height:112px; }
.metric-label { color:var(--muted); font-size:.82rem; font-weight:600; }
.metric-value { color:var(--ink); font-family:'Manrope'; font-size:1.8rem; font-weight:800; margin-top:5px; }
.metric-note { color:var(--muted); font-size:.78rem; margin-top:2px; }
.section-eyebrow { color:var(--purple); font-size:.75rem; font-weight:800; letter-spacing:1.3px; text-transform:uppercase; }
.muted { color:var(--muted); }
.skill-chip { display:inline-block; padding:7px 12px; margin:4px 5px 4px 0; border-radius:30px;
    font-size:.82rem; font-weight:600; background:#f0ebff; color:#6244b8; border:1px solid #e2d9ff; }
.missing-chip { background:#fff1f1; color:#b44b5a; border-color:#f8dadd; }
.success-chip { background:#eaf8f1; color:#25835b; border-color:#d3f0e1; }
.roadmap-item { border-left:3px solid #a58aef; padding:2px 0 18px 18px; margin-left:8px; }
.roadmap-item:last-child { border-left-color:transparent; }
.roadmap-week { color:var(--purple); font-weight:800; font-size:.8rem; letter-spacing:.5px; }
hr { border-color:var(--line); }
div[data-testid="stAlert"] { border-radius:12px; }
footer { visibility:hidden; }
@media(max-width:700px) {
    .hero { padding:28px 23px; border-radius:18px; }
    .feature-card { min-height:unset; }
    .block-container { padding-left:1rem; padding-right:1rem; }
}
</style>
""", unsafe_allow_html=True)

# ------------------------- HELPERS -----------------------

def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        st.error(f"Could not read this PDF: {exc}")
        return ""

def detect_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILLS:
        # Word boundaries avoid accidental matches such as "c" inside unrelated words.
        pattern = re.escape(skill)
        if re.search(r"(?<![a-z0-9])" + pattern + r"(?![a-z0-9])", text_lower):
            found.append(skill)
    return sorted(set(found))

def calculate_analysis(resume_text, job_description):
    resume_skills = detect_skills(resume_text)
    job_skills = detect_skills(job_description)
    matched = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))
    if job_skills:
        match_score = round((len(matched) / len(job_skills)) * 100)
    else:
        match_score = 0
    ats_score = min(100, match_score + min(15, len(resume_skills) * 2))
    return resume_skills, job_skills, matched, missing, match_score, ats_score

def recommend_roles(resume_skills):
    skills_set = set(resume_skills)
    results = []
    for role, required in CAREER_ROLES.items():
        overlap = skills_set.intersection(required)
        score = round(len(overlap) / len(required) * 100)
        results.append((role, score, sorted(overlap), sorted(set(required) - overlap)))
    return sorted(results, key=lambda item: item[1], reverse=True)

def make_report(data):
    resume_skills, job_skills, matched, missing, match_score, ats_score = data
    lines = [
        "SKILLMATCH AI — RESUME ANALYSIS REPORT",
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        "",
        f"Job skill match: {match_score}%",
        f"Estimated ATS score: {ats_score}%",
        "",
        "RESUME SKILLS:",
        ", ".join(resume_skills) or "No skills detected",
        "",
        "MATCHED SKILLS:",
        ", ".join(matched) or "None",
        "",
        "SKILLS TO DEVELOP:",
        ", ".join(missing) or "No missing skills detected",
        "",
        "Note: Scores are heuristic keyword-based estimates, not results from a real ATS.",
    ]
    return "\n".join(lines)

def show_metric(label, value, note):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

def show_chips(items, css_class=""):
    if not items:
        st.markdown('<span class="muted">Nothing to show yet.</span>', unsafe_allow_html=True)
        return
    html = "".join(
        f'<span class="skill-chip {css_class}">{skill.title()}</span>'
        for skill in items
    )
    st.markdown(html, unsafe_allow_html=True)

def score_gauge(score):
    fig = go.Figure(go.Pie(
        values=[score, 100-score],
        hole=.78,
        sort=False,
        direction="clockwise",
        marker=dict(colors=["#7655d9", "#eeeaf7"], line=dict(width=0)),
        textinfo="none",
        hoverinfo="skip",
    ))
    fig.add_annotation(
        text=f"<b>{score}%</b><br><span style='font-size:12px;color:#89839a'>ESTIMATED ATS</span>",
        x=.5, y=.5, showarrow=False, font=dict(size=29, color="#281d43")
    )
    fig.update_layout(
        height=245, margin=dict(t=8,b=8,l=8,r=8), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# ------------------------- SESSION STATE -----------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# ------------------------- SIDEBAR -----------------------

with st.sidebar:
    st.markdown("""
    <div style="padding:4px 4px 20px">
      <div style="font-size:2rem">🎯</div>
      <div style="font-family:Manrope;font-size:1.35rem;font-weight:800;color:#2b2044">SkillMatch <span style="color:#7655d9">AI</span></div>
      <div style="font-size:.78rem;color:#8b849d">Your intelligent career companion</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        ["🏠  Home", "📄  Resume Analysis", "🧭  Career Explorer",
         "🎤  Interview Preparation", "📚  Learning Hub"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("**YOUR WORKSPACE**")
    if st.session_state.analysis:
        st.markdown('<span class="success-chip">● Analysis available</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="skill-chip">○ No analysis yet</span>', unsafe_allow_html=True)
    st.markdown("<div style='height:25px'></div><div class='muted' style='font-size:.75rem'>SKILLMATCH AI · PORTFOLIO EDITION<br>Built with Python + Streamlit</div>", unsafe_allow_html=True)

# ------------------------- HOME ---------------------------

if page.startswith("🏠"):
    st.markdown("""
    <div class="hero">
      <span class="hero-badge">✨ YOUR AI-POWERED CAREER COMPANION</span>
      <h1>Build your next career move<br>with confidence.</h1>
      <p>Understand how your skills match a role, discover career paths, prepare for interviews,
      and create a focused learning plan — all from one workspace.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-eyebrow">Everything you need to move forward</div>', unsafe_allow_html=True)
    st.markdown("## Your career toolkit")
    cards = [
        ("📄", "Resume Analysis", "Compare your resume with a job description and identify strengths and skill gaps."),
        ("📊", "ATS Insights", "Review a keyword-based match estimate and explore your detected skills."),
        ("🧭", "Career Explorer", "Discover roles that align with your current skill set."),
        ("🎤", "Interview Preparation", "Practice technical and HR questions before your next interview."),
        ("🗺️", "Learning Roadmap", "Turn missing skills into a simple, actionable learning plan."),
        ("📚", "Learning Hub", "Find curated documentation and learning resources for key skills."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(
                f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
                f'<h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("### Start with a resume analysis")
        st.markdown('<p class="muted">Upload your resume and paste a target job description to get a skill-gap report.</p>', unsafe_allow_html=True)
        if st.button("✨ Analyze my resume", type="primary", use_container_width=True):
            st.session_state.go_analysis = True
            st.rerun()
    with right:
        st.markdown("""
        <div class="panel">
          <div class="section-eyebrow">Simple workflow</div>
          <p><b>01</b> &nbsp; Add your resume</p>
          <p><b>02</b> &nbsp; Choose a target role</p>
          <p><b>03</b> &nbsp; Review your skill gaps</p>
          <p><b>04</b> &nbsp; Follow your roadmap</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------- RESUME ANALYSIS ----------------

elif page.startswith("📄"):
    st.markdown('<div class="section-eyebrow">Resume intelligence</div>', unsafe_allow_html=True)
    st.title("Resume Analysis")
    st.markdown('<p class="muted">Compare your resume with a target job description and discover where to focus.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if uploaded_file:
            extracted = extract_pdf_text(uploaded_file)
            if extracted:
                st.session_state.resume_text = extracted
                st.success("PDF text extracted successfully.")
            else:
                st.warning("No readable text found. Try another PDF or paste your resume below.")
        resume_text = st.text_area(
            "Resume text",
            value=st.session_state.resume_text,
            height=260,
            placeholder="Paste your resume text here...",
            help="You can paste text directly or upload a text-based PDF above.",
        )
        st.session_state.resume_text = resume_text

    with col2:
        job_description = st.text_area(
            "Target job description",
            height=260,
            placeholder="Paste the job description here...",
        )
        st.markdown('<p class="muted" style="font-size:.8rem">Tip: Include responsibilities and required skills for a more useful comparison.</p>', unsafe_allow_html=True)

    if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
        if not resume_text.strip():
            st.warning("Please upload a PDF or paste your resume text.")
        elif not job_description.strip():
            st.warning("Please paste a target job description.")
        else:
            st.session_state.analysis = calculate_analysis(resume_text, job_description)
            st.session_state.last_job_description = job_description
            st.success("Your resume analysis is ready.")

    if st.session_state.analysis:
        data = st.session_state.analysis
        resume_skills, job_skills, matched, missing, match_score, ats_score = data
        st.markdown("---")
        st.markdown("### Your analysis overview")
        metrics = st.columns(4)
        with metrics[0]: show_metric("Job match", f"{match_score}%", "Target skill coverage")
        with metrics[1]: show_metric("Estimated ATS", f"{ats_score}%", "Keyword-based estimate")
        with metrics[2]: show_metric("Skills detected", len(resume_skills), "In your resume")
        with metrics[3]: show_metric("Skill gaps", len(missing), "Skills not detected")

        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns([1, 1.5])
        with a:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("#### Estimated ATS score")
            st.plotly_chart(score_gauge(ats_score), use_container_width=True, config={"displayModeBar": False})
            st.markdown('<p class="muted" style="font-size:.78rem">This is a simplified keyword estimate, not a score from an actual applicant tracking system.</p>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with b:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("#### Skill match breakdown")
            st.progress(match_score / 100)
            st.markdown(f"**{len(matched)} of {len(job_skills)}** detected job-description skills found in your resume.")
            st.markdown("**Matched skills**")
            show_chips(matched, "success-chip")
            st.markdown("**Skills to develop or highlight**")
            show_chips(missing, "missing-chip")
            st.markdown("</div>", unsafe_allow_html=True)

        chart_col, skills_col = st.columns(2)
        with chart_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("#### Skill coverage")
            chart_df = pd.DataFrame({
                "Category": ["Matched", "Missing"],
                "Skills": [len(matched), len(missing)]
            })
            fig = px.bar(chart_df, x="Category", y="Skills", color="Category",
                         color_discrete_map={"Matched": "#7655d9", "Missing": "#e6a0ae"})
            fig.update_layout(height=280, showlegend=False, margin=dict(t=15,b=10,l=5,r=5),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        with skills_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("#### Your detected skills")
            show_chips(resume_skills)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### Your 4-week improvement roadmap")
        roadmap = [
            ("WEEK 01 · FOUNDATION", "Choose the two most important missing skills. Learn the fundamentals and take notes."),
            ("WEEK 02 · PRACTICE", "Complete guided exercises and build small examples using those skills."),
            ("WEEK 03 · PROJECT", "Create a practical project that demonstrates the skills in a realistic scenario."),
            ("WEEK 04 · PRESENTATION", "Update your resume with evidence, project outcomes, and relevant keywords."),
        ]
        for week, task in roadmap:
            st.markdown(f'<div class="roadmap-item"><div class="roadmap-week">{week}</div><div>{task}</div></div>', unsafe_allow_html=True)

        if missing:
            st.markdown("### Learning resources for your skill gaps")
            resource_cols = st.columns(2)
            for i, skill in enumerate(missing[:8]):
                url = LEARNING_RESOURCES.get(skill, f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial")
                with resource_cols[i % 2]:
                    st.link_button(f"📘 Learn {skill.title()}", url, use_container_width=True)

        report = make_report(data)
        st.download_button(
            "⬇️ Download analysis report",
            data=report,
            file_name="skillmatch_resume_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ------------------------- CAREER EXPLORER ----------------

elif page.startswith("🧭"):
    st.markdown('<div class="section-eyebrow">Find your direction</div>', unsafe_allow_html=True)
    st.title("Career Explorer")
    st.markdown('<p class="muted">Explore roles based on the skills you already have and identify what to learn next.</p>', unsafe_allow_html=True)

    if st.session_state.analysis:
        current_skills = st.session_state.analysis[0]
        st.info("Using skills detected from your latest resume analysis.")
    else:
        manual = st.multiselect("Select your current skills", SKILLS)
        current_skills = manual
        st.caption("You can also run Resume Analysis first to use your detected skills here.")

    if current_skills:
        recommendations = recommend_roles(current_skills)
        for role, score, overlap, gaps in recommendations:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {role}")
                    st.markdown(f'<span class="muted">{len(overlap)} relevant skills found · {len(gaps)} skills to develop</span>', unsafe_allow_html=True)
                    st.progress(score / 100)
                with c2:
                    st.metric("Skill alignment", f"{score}%")
                with st.expander("View role skill details"):
                    st.markdown("**Skills you have**")
                    show_chips(overlap, "success-chip")
                    st.markdown("**Skills to consider learning**")
                    show_chips(gaps, "missing-chip")
    else:
        st.info("Select some skills or complete a resume analysis to see career recommendations.")

# ------------------------- INTERVIEW PREPARATION ----------

elif page.startswith("🎤"):
    st.markdown('<div class="section-eyebrow">Practice with purpose</div>', unsafe_allow_html=True)
    st.title("Interview Preparation")
    st.markdown('<p class="muted">Use these prompts to structure your practice. Explain your answers aloud and support them with examples.</p>', unsafe_allow_html=True)

    topic = st.selectbox("Choose an interview area", list(TECH_QUESTIONS.keys()))
    st.markdown("### Technical and role-based questions")
    for i, question in enumerate(TECH_QUESTIONS[topic], 1):
        with st.expander(f"Question {i}: {question}"):
            st.text_area("Your practice answer", key=f"tech_{topic}_{i}", height=110,
                         placeholder="Write or outline your answer here...")
    st.markdown("### HR and behavioral questions")
    for i, question in enumerate(HR_QUESTIONS, 1):
        with st.expander(f"HR Question {i}: {question}"):
            st.text_area("Your practice answer", key=f"hr_{i}", height=110,
                         placeholder="Use the STAR method: Situation, Task, Action, Result.")
    st.info("Practice tip: Keep answers structured, specific, and focused on your own contribution.")

# ------------------------- LEARNING HUB -------------------

elif page.startswith("📚"):
    st.markdown('<div class="section-eyebrow">Keep growing</div>', unsafe_allow_html=True)
    st.title("Learning Hub")
    st.markdown('<p class="muted">Find a starting point for the skills that can strengthen your career profile.</p>', unsafe_allow_html=True)

    if st.session_state.analysis:
        suggested = st.session_state.analysis[3]
        if suggested:
            st.markdown("### Suggested from your latest analysis")
            st.markdown("These are skills from the target job description that were not detected in your resume.")
            show_chips(suggested, "missing-chip")
    chosen_skill = st.selectbox("Choose a skill to learn", sorted(LEARNING_RESOURCES.keys()))
    url = LEARNING_RESOURCES[chosen_skill]
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f"### 📘 {chosen_skill.title()}")
    st.markdown("Open this curated learning resource to start building the skill.")
    st.link_button("🚀 Open learning resource", url, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### A simple learning routine")
    routine = [
        ("Learn", "Study one focused concept and write down the key ideas."),
        ("Practice", "Complete a short exercise without copying the solution."),
        ("Build", "Apply the concept in a small project or portfolio example."),
        ("Reflect", "Record what you learned and what you want to improve next."),
    ]
    cols = st.columns(4)
    for col, (title, desc) in zip(cols, routine):
        with col:
            st.markdown(f'<div class="feature-card"><div class="section-eyebrow">{title}</div><p>{desc}</p></div>', unsafe_allow_html=True)

# ------------------------- FOOTER -------------------------

st.markdown("""
<div style="text-align:center;padding:28px 0 8px;color:#928ba3;font-size:.78rem">
    <b style="color:#7655d9">SkillMatch AI</b> · Build skills. Find direction. Move forward.<br>
    <span>Career insights are guidance only. Always review job requirements and verify learning resources.</span>
</div>
""", unsafe_allow_html=True)
