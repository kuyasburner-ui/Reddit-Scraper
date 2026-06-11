#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import random

BASE = "https://old.reddit.com"


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    })
    try:
        session.get(f"{BASE}/", timeout=15)
        time.sleep(random.uniform(1.0, 2.0))
    except Exception:
        pass
    return session


def fetch_with_retry(session, url, params=None, retries=3):
    for attempt in range(retries):
        try:
            resp = session.get(url, params=params, timeout=15)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            if resp.status_code in (429, 403):
                wait = (attempt + 1) * 5
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Failed after {retries} retries: {url}")


def search_posts(session, query, limit):
    posts = []
    after = None
    page_size = 100

    while len(posts) < limit:
        fetch = min(page_size, limit - len(posts))
        params = {"q": query, "sort": "relevance", "limit": fetch, "type": "link"}
        if after:
            params["after"] = after

        resp = fetch_with_retry(session, f"{BASE}/search", params=params)
        soup = BeautifulSoup(resp.text, "html.parser")
        divs = soup.select("div.search-result")

        if not divs:
            break

        last_fullname = None
        for div in divs:
            title_el = div.select_one("a.search-title")
            if not title_el:
                continue

            href = title_el.get("href", "")
            if not href.startswith("http"):
                href = BASE + href

            score_el = div.select_one("span.search-score")
            author_el = div.select_one("a.author")
            sub_el = div.select_one("a.search-subreddit-link")
            last_fullname = div.get("data-fullname", "")

            posts.append({
                "title": title_el.get_text(strip=True),
                "url": href,
                "author": author_el.get_text(strip=True) if author_el else "[deleted]",
                "subreddit": sub_el.get_text(strip=True).lstrip("r/") if sub_el else "",
                "score": score_el.get_text(strip=True) if score_el else "?",
            })

            if len(posts) >= limit:
                break

        after = last_fullname
        if not after or len(divs) < fetch:
            break

        time.sleep(random.uniform(1.5, 3.0))

    return posts


def get_post_data(session, url, max_comments=20):
    if "old.reddit.com" not in url:
        url = url.replace("www.reddit.com", "old.reddit.com").replace("reddit.com", "old.reddit.com")

    time.sleep(random.uniform(0.75, 1.5))
    try:
        resp = fetch_with_retry(session, url)
    except Exception:
        return "", []

    soup = BeautifulSoup(resp.text, "html.parser")

    selftext = ""
    post_thing = soup.select_one("div.thing.link")
    if post_thing:
        body_el = post_thing.select_one("div.usertext-body .md")
        if body_el:
            selftext = body_el.get_text(separator="\n", strip=True)

    comments = []
    for comment_div in soup.select("div.thing.comment"):
        author_el = comment_div.select_one("a.author")
        score_el = comment_div.select_one("span.score")
        body_el = comment_div.select_one("div.usertext-body .md")

        if not body_el:
            continue
        body = body_el.get_text(separator="\n", strip=True)
        if not body or body in ("[deleted]", "[removed]"):
            continue

        score_text = score_el.get("title", score_el.get_text(strip=True)) if score_el else "?"
        comments.append({
            "author": author_el.get_text(strip=True) if author_el else "[deleted]",
            "score": score_text,
            "body": body,
        })

        if len(comments) >= max_comments:
            break

    return selftext, comments


def scrape_stream(query, num_posts, include_comments):
    """Generator yielding (current_index, total, post_dict) for live UI updates."""
    session = create_session()
    posts_meta = search_posts(session, query, num_posts)
    total = len(posts_meta)

    for i, post_meta in enumerate(posts_meta, 1):
        selftext, comments = get_post_data(session, post_meta["url"])
        yield i, total, {
            **post_meta,
            "selftext": selftext,
            "comments": comments if include_comments else [],
        }
