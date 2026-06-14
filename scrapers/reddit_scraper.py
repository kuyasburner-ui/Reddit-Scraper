import requests
import time as _time

# ── Pullpush (archive) — used for keyword search ──────────────────────────────
_PP_API     = "https://api.pullpush.io/reddit/search"
_PP_HEADERS = {"User-Agent": "RedditScraper/1.0", "Accept": "application/json"}

_SEARCH_SORT_MAP = {
    "Top":           ("score",        "desc"),
    "New":           ("created_utc",  "desc"),
    "Old":           ("created_utc",  "asc"),
    "Most Comments": ("num_comments", "desc"),
}

# ── Reddit native — used for subreddit browsing ───────────────────────────────
_RD_BASE    = "https://www.reddit.com"
_RD_HEADERS = {"User-Agent": "RedditScraper/1.0 (Streamlit cloud app)", "Accept": "application/json"}

_SUB_SORT_ENDPOINT = {
    "Hot":           "hot",
    "New":           "new",
    "Top":           "top",
    "Rising":        "rising",
    "Controversial": "controversial",
}

_TIME_PERIOD = {
    "Last Hour":  "hour",
    "Today":      "day",
    "This Week":  "week",
    "This Month": "month",
    "This Year":  "year",
    "All Time":   "all",
}

_TIME_DELTA = {
    "Last Hour":  3600,
    "Today":      86400,
    "This Week":  604800,
    "This Month": 2592000,
    "This Year":  31536000,
    "All Time":   None,
}


def _after_ts(period):
    delta = _TIME_DELTA.get(period)
    return int(_time.time()) - delta if delta else None


def _pp_get(path, params, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(
                f"{_PP_API}{path}", params=params,
                headers=_PP_HEADERS, timeout=20,
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


def _rd_get(url, params, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(
                url, params=params,
                headers=_RD_HEADERS, timeout=20,
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


def _parse_pp(data, limit):
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


def _parse_rd(children, limit):
    posts = []
    for child in children[:limit]:
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
    return posts


# ── Public API ────────────────────────────────────────────────────────────────

def search_posts(query, limit, sort="Top", time_filter="All Time"):
    """Keyword search via Pullpush archive."""
    sort_type, sort_dir = _SEARCH_SORT_MAP.get(sort, ("score", "desc"))
    params = {
        "q":         query,
        "size":      min(limit, 100),
        "sort":      sort_dir,
        "sort_type": sort_type,
    }
    after = _after_ts(time_filter)
    if after:
        params["after"] = after
    resp = _pp_get("/submission/", params)
    return _parse_pp(resp.json().get("data", []), limit)


def search_subreddit(subreddit, limit, sort="Hot", time_filter="All Time"):
    """Subreddit browse via Reddit's native JSON API (real-time data)."""
    subreddit    = subreddit.lstrip("r/").strip()
    endpoint     = _SUB_SORT_ENDPOINT.get(sort, "hot")
    url          = f"{_RD_BASE}/r/{subreddit}/{endpoint}.json"
    params       = {"limit": min(limit, 100), "raw_json": 1}
    if sort in ("Top", "Controversial"):
        params["t"] = _TIME_PERIOD.get(time_filter, "all")
    resp         = _rd_get(url, params)
    children     = resp.json().get("data", {}).get("children", [])
    return _parse_rd(children, limit)


def get_comments(post_id, max_comments=20):
    """Fetch top comments via Pullpush."""
    try:
        resp = _pp_get("/comment/", {
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
