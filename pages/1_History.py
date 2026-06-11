import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import db
from styles import inject_css, navbar, hero, section_header, footer

st.set_page_config(
    page_title="Scan History — Reddit Scraper",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_css()
navbar("history")

# ── Helpers ───────────────────────────────────────────────────────────────────

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


# ── Page ──────────────────────────────────────────────────────────────────────

hero(
    title="Scan History",
    badge="Previous Runs",
    subtitle="Browse and re-download every past scrape.",
)

scrapes = db.list_scrapes()

if not scrapes:
    st.info("No history yet — run your first scrape on the home page.")
    st.stop()

# Stats row
total_posts = sum(s["post_count"] for s in scrapes)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="r-stat" style="text-align:left;">'
        f'<span class="r-stat-num" style="font-size:1.8rem;">{len(scrapes)}</span>'
        f'<span class="r-stat-label">Total Runs</span></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="r-stat" style="text-align:left;">'
        f'<span class="r-stat-num" style="font-size:1.8rem;">{total_posts:,}</span>'
        f'<span class="r-stat-label">Total Posts Collected</span></div>',
        unsafe_allow_html=True,
    )
with col3:
    queries = len({s["query"] for s in scrapes})
    st.markdown(
        f'<div class="r-stat" style="text-align:left;">'
        f'<span class="r-stat-num" style="font-size:1.8rem;">{queries}</span>'
        f'<span class="r-stat-label">Unique Queries</span></div>',
        unsafe_allow_html=True,
    )

st.divider()

# Bulk export
all_rows = []
for s in scrapes:
    for p in s["results"]:
        all_rows.append({
            "scrape_query": s["query"],
            "scrape_date":  s["created_at"][:19].replace("T", " "),
            **{k: p.get(k, "") for k in ["title", "subreddit", "author", "score", "url", "selftext"]},
        })

if all_rows:
    section_header("Bulk Export")
    st.download_button(
        "Download all history (CSV)",
        data=pd.DataFrame(all_rows).to_csv(index=False).encode("utf-8"),
        file_name="reddit_history_all.csv",
        mime="text/csv",
    )
    st.divider()

section_header("Run Log", f"{len(scrapes)} Scrapes")

for s in scrapes:
    date_str = s["created_at"][:19].replace("T", " ")
    label = f"{date_str}   ·   \"{s['query']}\"   ·   {s['post_count']} posts"
    with st.expander(label):
        params = s.get("params", {})
        inc = "with comments" if params.get("include_comments") else "posts only"
        st.caption(f"Requested: {params.get('num_posts','?')} posts  ·  {inc}")

        results = s["results"]
        if not results:
            st.write("No results stored.")
            continue

        df = results_to_df(results)
        st.dataframe(
            df[["title", "subreddit", "author", "score"]].head(20),
            use_container_width=True,
        )
        if len(results) > 20:
            st.caption(f"Showing first 20 of {len(results)}. Download for complete data.")

        safe_date = date_str.replace(" ", "_").replace(":", "")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"reddit_{safe_date}.csv",
                mime="text/csv",
                key=f"csv_{s['id']}",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "Download TXT",
                data=results_to_txt(s["query"], results).encode("utf-8"),
                file_name=f"reddit_{safe_date}.txt",
                mime="text/plain",
                key=f"txt_{s['id']}",
                use_container_width=True,
            )

footer()
