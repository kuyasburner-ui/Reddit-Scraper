import requests
import time
import random
import streamlit as st

_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
_API_BASE  = "https://oauth.reddit.com"
_UA        = "RedditScraper/1.0 (Streamlit app; contact kuyasburner@gmail.com)"


def _token():
    cid    = st.secrets.get("REDDIT_CLIENT_ID", "")
    secret = st.secrets.get("REDDIT_CLIENT_SECRET", "")
    if not cid or not secret:
        raise RuntimeError(
            "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in Streamlit secrets. "
            "Create a free Reddit app at reddit.com/prefs/apps (script type)."
        )
    resp = requests.post(
        _TOKEN_URL,
        auth=(cid, secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": _UA},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _get(token, path, params=None, retries=3):
    headers = {"Authorization": f"Bearer {token}", "User-Agent": _UA}
    url = f"{_API_BASE}{path}"
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 429:
                time.sleep((attempt + 1) * 10)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep((attempt + 1) * 3)


def search_posts(token, query, limit):
    posts = []
    after = None

    while len(posts) < limit:
        params = {
            "q":        query,
            "sort":     "relevance",
            "limit":    min(100, limit - len(posts)),
            "type":     "link",
            "raw_json": 1,
        }
        if after:
            params["after"] = after

        resp     = _get(token, "/search", params=params)
        data     = resp.json().get("data", {})
        children = data.get("children", [])

        if not children:
            break

        for child in children:
            p = child.get("data", {})
            posts.append({
                "id":        p.get("id", ""),
                "title":     p.get("title", ""),
                "url":       p.get("url", ""),
                "permalink": p.get("permalink", ""),
                "author":    p.get("author", "[deleted]"),
                "subreddit": p.get("subreddit", ""),
                "score":     str(p.get("score", 0)),
                "selftext":  p.get("selftext", ""),
            })
            if len(posts) >= limit:
                break

        after = data.get("after")
        if not after:
            break

        time.sleep(random.uniform(0.5, 1.0))

    return posts


def get_comments(token, permalink, max_comments=20):
    try:
        resp = _get(token, f"{permalink}.json",
                    params={"limit": max_comments, "depth": 2, "raw_json": 1})
        listing = resp.json()
        if len(listing) < 2:
            return []

        comments = []
        for child in listing[1]["data"]["children"]:
            if child.get("kind") != "t1":
                continue
            c    = child["data"]
            body = c.get("body", "")
            if not body or body in ("[deleted]", "[removed]"):
                continue
            comments.append({
                "author": c.get("author", "[deleted]"),
                "score":  str(c.get("score", 0)),
                "body":   body,
            })
            if len(comments) >= max_comments:
                break
        return comments
    except Exception:
        return []


def scrape_stream(query, num_posts, include_comments):
    """Generator yielding (current_index, total, post_dict) for live UI updates."""
    token = _token()
    posts = search_posts(token, query, num_posts)
    total = len(posts)

    for i, post in enumerate(posts, 1):
        if include_comments and post.get("permalink"):
            time.sleep(random.uniform(0.3, 0.7))
            post["comments"] = get_comments(token, post["permalink"])
        else:
            post["comments"] = []

        yield i, total, post
