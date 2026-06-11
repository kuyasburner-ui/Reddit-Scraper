import requests
import time
import random

BASE = "https://www.reddit.com"

HEADERS = {
    "User-Agent": "RedditScraper/1.0 (research tool; contact kuyasburner@gmail.com)",
    "Accept": "application/json",
}


def _get(url, params=None, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
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
    posts = []
    after = None

    while len(posts) < limit:
        params = {
            "q": query,
            "sort": "relevance",
            "limit": min(100, limit - len(posts)),
            "type": "link",
            "raw_json": 1,
        }
        if after:
            params["after"] = after

        resp = _get(f"{BASE}/search.json", params=params)
        data = resp.json().get("data", {})
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
                "is_self":   p.get("is_self", False),
            })
            if len(posts) >= limit:
                break

        after = data.get("after")
        if not after:
            break

        time.sleep(random.uniform(1.0, 2.0))

    return posts


def get_comments(permalink, max_comments=20):
    url = f"{BASE}{permalink}.json"
    try:
        resp = _get(url, params={"limit": max_comments, "depth": 2, "raw_json": 1})
        listing = resp.json()
        if len(listing) < 2:
            return []

        comments = []
        for child in listing[1]["data"]["children"]:
            if child.get("kind") != "t1":
                continue
            c = child["data"]
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
    posts = search_posts(query, num_posts)
    total = len(posts)

    for i, post in enumerate(posts, 1):
        if include_comments and post.get("permalink"):
            time.sleep(random.uniform(0.5, 1.0))
            post["comments"] = get_comments(post["permalink"])
        else:
            post["comments"] = []

        yield i, total, post
