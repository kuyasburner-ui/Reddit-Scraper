import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from scrapers.reddit_scraper import search_posts, search_subreddit, get_comments
from styles import (
    inject_css, navbar, hero, section_header, success_banner,
    how_it_works, stats_bar, footer,
)
import db

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_session_id():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        return ctx.session_id if ctx else "unknown"
    except Exception:
        return "unknown"


def get_or_create_uid():
    uid = st.query_params.get("uid", "")
    if not uid:
        import uuid
        uid = uuid.uuid4().hex[:12]
        st.query_params["uid"] = uid
    return uid


def results_to_df(results):
    return pd.DataFrame([{
        "title":     p.get("title", ""),
        "subreddit": p.get("subreddit", ""),
        "author":    p.get("author", ""),
        "score":     p.get("score", ""),
        "url":       p.get("url", ""),
        "body":      p.get("selftext", ""),
    } for p in results])


def results_to_txt(query, results):
    lines = [
        f"Reddit Search: {query}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Posts retrieved: {len(results)}",
        "=" * 80, "",
    ]
    for i, p in enumerate(results, 1):
        lines += [
            f"POST {i}",
            f"Title:     {p.get('title', '')}",
            f"Subreddit: r/{p.get('subreddit', '')}",
            f"Author:    u/{p.get('author', '')}",
            f"Score:     {p.get('score', '')}",
            f"Link:      {p.get('url', '')}",
        ]
        if p.get("selftext"):
            lines.append(f"\nPost Body:\n{p['selftext']}")
        comments = p.get("comments", [])
        if comments:
            lines.append(f"\nComments ({len(comments)}):")
            for j, c in enumerate(comments, 1):
                lines.append(f"\n  [{j}] u/{c['author']} ({c['score']} points)")
                for line in c["body"].splitlines():
                    lines.append(f"      {line}")
        lines += ["\n" + "-" * 80, ""]
    return "\n".join(lines)


def results_to_md(query, results):
    lines = [
        f"# Reddit Scrape: {query}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Posts:** {len(results)}",
        "",
    ]
    for i, p in enumerate(results, 1):
        lines += [
            f"---",
            f"## {i}. {p.get('title', '')}",
            f"**Subreddit:** r/{p.get('subreddit', '')} &nbsp;|&nbsp; "
            f"**Author:** u/{p.get('author', '')} &nbsp;|&nbsp; "
            f"**Score:** {p.get('score', '')}  ",
            f"**Link:** {p.get('url', '')}",
            "",
        ]
        if p.get("selftext"):
            lines += [f"### Post Body", p["selftext"], ""]
        comments = p.get("comments", [])
        if comments:
            lines.append(f"### Comments ({len(comments)})")
            for j, c in enumerate(comments, 1):
                lines += [
                    f"**{j}. u/{c['author']}** ({c['score']} pts)",
                    f"> {c['body'].replace(chr(10), '  ' + chr(10) + '> ')}",
                    "",
                ]
    return "\n".join(lines)


def safe_filename(query, count):
    import re
    slug = re.sub(r"[^\w\s-]", "", query).strip().replace(" ", "_")
    return f"{slug}_{count}"


def download_buttons(query, results, key_prefix=""):
    if not results:
        return
    df = results_to_df(results)
    base = safe_filename(query, len(results))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{base}.csv",
            mime="text/csv",
            key=f"{key_prefix}_csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download TXT",
            data=results_to_txt(query, results).encode("utf-8"),
            file_name=f"{base}.txt",
            mime="text/plain",
            key=f"{key_prefix}_txt",
            use_container_width=True,
        )
    with col3:
        st.download_button(
            "Download MD",
            data=results_to_md(query, results).encode("utf-8"),
            file_name=f"{base}.md",
            mime="text/markdown",
            key=f"{key_prefix}_md",
            use_container_width=True,
        )


# ── Admin check ───────────────────────────────────────────────────────────────

token = st.query_params.get("token", "")
admin_token = ""
try:
    admin_token = st.secrets.get("ADMIN_TOKEN", "")
except Exception:
    pass
is_admin = bool(token and admin_token and token == admin_token)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Reddit Scraper" if not is_admin else "Admin — Reddit Scraper",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_css()

# ── Admin view ────────────────────────────────────────────────────────────────

if is_admin:
    navbar("home")
    st.markdown(
        '<h1 style="font-size:1.6rem!important;letter-spacing:3px;">Admin Console</h1>',
        unsafe_allow_html=True,
    )
    section_header("ALL ACTIVITY", "Scrape Log — Newest First")

    scrapes = db.list_scrapes()
    if not scrapes:
        st.info("No scrape runs recorded yet.")
        st.stop()

    summary = pd.DataFrame([{
        "Date":     s["created_at"][:19].replace("T", " "),
        "Query":    s["query"],
        "Posts":    s["post_count"],
        "Comments": "yes" if s.get("params", {}).get("include_comments") else "no",
        "Session":  s["session_id"][:8] + "…",
    } for s in scrapes])
    st.dataframe(summary, use_container_width=True)

    all_rows = []
    for s in scrapes:
        for p in s["results"]:
            all_rows.append({"scrape_query": s["query"], "scrape_date": s["created_at"][:19], **p})
    if all_rows:
        st.download_button(
            "Download all results (CSV)",
            data=pd.DataFrame(all_rows).to_csv(index=False).encode("utf-8"),
            file_name="all_scrapes.csv",
            mime="text/csv",
        )

    st.divider()
    section_header("EXPAND RUN", "Individual Run Detail")
    for s in scrapes:
        label = f"{s['created_at'][:19].replace('T',' ')}  |  \"{s['query']}\"  |  {s['post_count']} posts"
        with st.expander(label):
            st.caption(f"Session: {s['session_id']}  |  {s['params']}")
            if s["results"]:
                st.dataframe(results_to_df(s["results"]), use_container_width=True)
                download_buttons(s["query"], s["results"], key_prefix=s["id"])
            else:
                st.write("No results stored.")
    st.stop()

# ── Normal view ───────────────────────────────────────────────────────────────

uid = get_or_create_uid()
navbar("home", uid=uid)

hero(
    title="Reddit Scraper",
    badge="Free Intelligence Tool",
    subtitle="Search Reddit and extract posts with comments in seconds. "
             "No API key required — export to CSV or plain text instantly.",
)

# ── Search form ───────────────────────────────────────────────────────────────

section_header("Configure Scan", "Set Your Search Parameters")

mode = st.radio("Mode", ["Keyword Search", "Subreddit"], horizontal=True,
                label_visibility="collapsed", key="scrape_mode")

with st.form("scrape_form"):
    if mode == "Keyword Search":
        query = st.text_input(
            "Search query",
            placeholder="e.g.  best protein powder  ·  perimenopause symptoms  ·  clogged pores",
        )
        subreddit = ""
        sort = "top"
    else:
        query = ""
        c_label, c_input = st.columns([0.07, 0.93])
        with c_label:
            st.markdown(
                '<div style="padding-top:2.1rem;font-weight:600;color:#00ff41;font-size:1rem;">r/</div>',
                unsafe_allow_html=True,
            )
        with c_input:
            subreddit = st.text_input(
                "Subreddit",
                placeholder="e.g.  wallstreetbets  ·  fitness  ·  AskReddit",
            )
        sort = st.radio("Sort by", ["Top", "New"], horizontal=True, index=0).lower()

    col1, col2 = st.columns([3, 2])
    with col1:
        num_posts = st.slider("Posts to retrieve", min_value=1, max_value=1000, value=25, step=5)
    with col2:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        include_comments = st.toggle("Include comments", value=True)
    submitted = st.form_submit_button("Run Scrape", use_container_width=True)

# ── How it works (shown before any scrape) ────────────────────────────────────

if not submitted:
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    section_header("How It Works")
    how_it_works()
    stats_bar()
    footer()
    st.stop()

# ── Run scrape ────────────────────────────────────────────────────────────────

if mode == "Keyword Search" and not query.strip():
    st.error("Please enter a search query.")
    st.stop()
if mode == "Subreddit" and not subreddit.strip():
    st.error("Please enter a subreddit name.")
    st.stop()

# Use the subreddit name or query as the display label
label = f"r/{subreddit.lstrip('r/').strip()}" if mode == "Subreddit" else query.strip()

results  = []
_status  = st.empty()
_pbar    = st.empty()

_status.markdown(
    '<p style="color:#3a3a5a;font-size:0.85rem;margin:0;">Connecting to Reddit…</p>',
    unsafe_allow_html=True,
)
_pbar.progress(0.0, text="Connecting to Reddit…")

try:
    if mode == "Subreddit":
        posts = search_subreddit(subreddit.strip(), num_posts, sort=sort)
    else:
        posts = search_posts(query.strip(), num_posts)
except Exception as e:
    st.error(f"Scrape failed: {e}")
    st.stop()

if not posts:
    st.warning("No posts found — try a different query.")
    st.stop()

# Phase 2 — fetch comments per post
total = len(posts)
_pbar.progress(0.0, text=f"Found {total} posts — fetching details…")

for i, post in enumerate(posts, 1):
    if include_comments and post.get("id"):
        post["comments"] = get_comments(post["id"])
    else:
        post["comments"] = []
    results.append(post)
    pct  = i / total
    _status.markdown(
        f'<p style="color:#3a3a5a;font-size:0.75rem;margin:0;">&#9656; {post["title"][:80]}</p>',
        unsafe_allow_html=True,
    )
    _pbar.progress(pct, text=f"Post {i} of {total}")

_status.empty()
_pbar.empty()

if not results:
    st.warning("No posts found — try a different query.")
    st.stop()

db.save_scrape(
    query=label,
    params={"num_posts": num_posts, "include_comments": include_comments, "mode": mode},
    results=results,
    session_id=get_session_id(),
    ip_address=uid,
)

success_banner(f"<strong>{len(results)} posts</strong> collected for &ldquo;{label}&rdquo;")

# ── Export ────────────────────────────────────────────────────────────────────

section_header("Export Data")
download_buttons(label, results, key_prefix="main")

# ── Results table ─────────────────────────────────────────────────────────────

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
section_header("Results Table", f"{len(results)} Posts")

df = results_to_df(results)
st.dataframe(df[["title", "subreddit", "author", "score"]], use_container_width=True)

# ── Full detail ───────────────────────────────────────────────────────────────

section_header("Post Detail", "Expand Any Row To Read Full Content")

for i, p in enumerate(results):
    with st.expander(f"{i+1:02d}  ·  {p['title']}", expanded=False):
        # Meta row
        st.markdown(
            f'<div class="r-post-meta">'
            f'<span class="r-tag green">r/{p["subreddit"]}</span>'
            f'<span class="r-tag">u/{p["author"]}</span>'
            f'<span class="r-tag">{p["score"]} pts</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"[View on Reddit ↗]({p['url']})")

        if p.get("selftext"):
            section_header("Post Body")
            st.write(p["selftext"])

        comments = p.get("comments", [])
        if comments:
            section_header(f"Comments ({len(comments)})")
            for j, c in enumerate(comments, 1):
                st.markdown(
                    f'<span class="r-comment-author">u/{c["author"]}</span>'
                    f'<span class="r-tag" style="margin-left:8px;">{c["score"]} pts</span>',
                    unsafe_allow_html=True,
                )
                st.write(c["body"])
                if j < len(comments):
                    st.markdown('<hr class="r-divider">', unsafe_allow_html=True)

footer()
