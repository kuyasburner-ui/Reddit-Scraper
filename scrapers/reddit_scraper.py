import requests
import time
import random

_API = "https://api.pullpush.io/reddit/search"
_UA  = "RedditScraper/1.0"
_HEADERS = {"User-Agent": _UA, "Accept": "application/json"}


def _get(path, params, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(
                f"{_API}{path}",
                params=params,
                headers=_HEADERS,
                timeout=20,
            )
            if resp.status_code == 429:
                time.sleep((attempt + 1) * 10)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep((attempt + 1) * 3)


def search_posts(query, limit):
    resp = _get("/submission/", {
        "q":         query,
        "size":      min(limit, 100),
        "sort":      "desc",
        "sort_type": "score",
    })
    posts = []
    for p in resp.json().get("data", [])[:limit]:
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
    return posts


def get_comments(post_id, max_comments=20):
    try:
        resp = _get("/comment/", {
            "link_id":   f"t3_{post_id}",
            "size":      max_comments,
            "sort":      "desc",
            "sort_type": "score",
        })
        comments = []
        for c in resp.json().get("data", [])[:max_comments]:
            body = c.get("body", "")
            if not body or body in ("[deleted]", "[removed]"):
                continue
            comments.append({
                "author": c.get("author", "[deleted]"),
                "score":  str(c.get("score", 0)),
                "body":   body,
            })
        return comments
    except Exception:
        return []


def scrape_stream(query, num_posts, include_comments):
    """Generator yielding (current_index, total, post_dict) for live UI updates."""
    posts = search_posts(query, num_posts)
    total = len(posts)

    for i, post in enumerate(posts, 1):
        if include_comments and post.get("id"):
            time.sleep(random.uniform(0.3, 0.7))
            post["comments"] = get_comments(post["id"])
        else:
            post["comments"] = []

        yield i, total, post
