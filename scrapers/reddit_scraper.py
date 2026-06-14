import requests
import time as _time

_API     = "https://api.pullpush.io/reddit/search"
_UA      = "RedditScraper/1.0"
_HEADERS = {"User-Agent": _UA, "Accept": "application/json"}

_SORT_MAP = {
    "Top":           ("score",       "desc"),
    "New":           ("created_utc", "desc"),
    "Old":           ("created_utc", "asc"),
    "Most Comments": ("num_comments","desc"),
}

_TIME_MAP = {
    "Last Hour":  3600,
    "Today":      86400,
    "This Week":  604800,
    "This Month": 2592000,
    "This Year":  31536000,
    "All Time":   None,
}


def _after_ts(period):
    delta = _TIME_MAP.get(period)
    return int(_time.time()) - delta if delta else None


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
                _time.sleep((attempt + 1) * 10)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                raise
            _time.sleep((attempt + 1) * 3)


def _parse_posts(data, limit):
    posts = []
    for p in data[:limit]:
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


def search_posts(query, limit, sort="Top", time_filter="All Time"):
    sort_type, sort_dir = _SORT_MAP.get(sort, ("score", "desc"))
    params = {
        "q":         query,
        "size":      min(limit, 100),
        "sort":      sort_dir,
        "sort_type": sort_type,
    }
    after = _after_ts(time_filter)
    if after:
        params["after"] = after
    resp = _get("/submission/", params)
    return _parse_posts(resp.json().get("data", []), limit)


def search_subreddit(subreddit, limit, sort="Top", time_filter="All Time"):
    subreddit = subreddit.lstrip("r/").strip()
    sort_type, sort_dir = _SORT_MAP.get(sort, ("score", "desc"))
    params = {
        "subreddit": subreddit,
        "size":      min(limit, 100),
        "sort":      sort_dir,
        "sort_type": sort_type,
    }
    after = _after_ts(time_filter)
    if after:
        params["after"] = after
    resp = _get("/submission/", params)
    return _parse_posts(resp.json().get("data", []), limit)


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
