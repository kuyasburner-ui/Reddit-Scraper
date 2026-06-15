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

# ── Subreddit sort → Pullpush params ─────────────────────────────────────────
# (sort_type, sort_dir, fixed_after_seconds or "time_filter" or None)
# "time_filter" = use the user's time_filter selection
# a number       = fixed recent window (e.g. Rising ≈ last 6 hours)
# None           = no time constraint
_SUB_SORT_MAP = {
    "Hot":           ("score",        "desc", None),
    "New":           ("created_utc",  "desc", None),
    "Top":           ("score",        "desc", "time_filter"),
    "Rising":        ("score",        "desc", 21600),
    "Controversial": ("num_comments", "desc", "time_filter"),
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


def _pp_get(path, params, retries=5):
    for attempt in range(retries):
        try:
            resp = requests.get(
                f"{_PP_API}{path}", params=params,
                headers=_PP_HEADERS, timeout=20,
            )
            if resp.status_code == 429:
                _time.sleep((attempt + 1) * 12)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                raise
            _time.sleep((attempt + 1) * 3)
    raise requests.exceptions.RequestException(
        "Pullpush API rate limited — too many requests. Try fewer posts or wait a moment."
    )


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


def search_subreddit(subreddit, limit, sort="Hot", time_filter="All Time", query=""):
    """Subreddit browse via Pullpush archive (cloud-IP safe).
    Optional query= filters posts by keyword within the subreddit."""
    subreddit = subreddit.lstrip("r/").strip()
    sort_type, sort_dir, after_mode = _SUB_SORT_MAP.get(sort, ("score", "desc", None))

    if after_mode == "time_filter":
        after = _after_ts(time_filter)
    elif isinstance(after_mode, int):
        after = int(_time.time()) - after_mode
    else:
        after = None

    all_posts = []
    remaining = limit
    before = None

    while remaining > 0:
        params = {
            "subreddit": subreddit,
            "size":      min(remaining, 100),
            "sort":      sort_dir,
            "sort_type": sort_type,
        }
        if query.strip():
            params["q"] = query.strip()
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        if all_posts:
            _time.sleep(1.5)
        resp = _pp_get("/submission/", params)
        batch = resp.json().get("data", [])
        if not batch:
            break

        all_posts.extend(batch)
        remaining -= len(batch)

        if len(batch) < 100:
            break
        before = batch[-1].get("created_utc")

    return _parse_pp(all_posts, limit)


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
