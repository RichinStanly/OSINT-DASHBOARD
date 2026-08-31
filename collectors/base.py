"""
Base collector functionality shared by all data source collectors:
- polite, retried, rate-limited HTTP requests
- robots.txt checking
- simple on-disk response caching
- URL validation helpers
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.robotparser
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

from config.settings import settings

_last_request_time: dict[str, float] = {}
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}

CACHE_DIR = settings.DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class CollectorError(Exception):
    """Raised for collector-specific failures. Always caught by callers."""


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def _cache_key(url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _read_cache(url: str) -> Optional[str]:
    path = _cache_key(url)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - payload["cached_at"] > settings.CACHE_TTL_SECONDS:
            return None
        return payload["body"]
    except Exception:
        return None


def _write_cache(url: str, body: str) -> None:
    path = _cache_key(url)
    try:
        path.write_text(
            json.dumps({"cached_at": time.time(), "body": body}),
            encoding="utf-8",
        )
    except Exception:
                                                                                
        pass


def _respect_rate_limit(domain: str) -> None:
    last = _last_request_time.get(domain)
    if last is not None:
        elapsed = time.time() - last
        if elapsed < settings.REQUEST_DELAY_SECONDS:
            time.sleep(settings.REQUEST_DELAY_SECONDS - elapsed)
    _last_request_time[domain] = time.time()


def is_allowed_by_robots(url: str) -> bool:
    """Check robots.txt for the given URL. Fails open (allows) if robots.txt
    cannot be fetched, since many sites simply don't publish one."""
    if not settings.RESPECT_ROBOTS_TXT:
        return True
    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in _robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
            except Exception:
                                                             
                _robots_cache[base] = None                
                return True
            _robots_cache[base] = rp
        rp = _robots_cache[base]
        if rp is None:
            return True
        return rp.can_fetch(settings.USER_AGENT, url)
    except Exception:
        return True


def fetch_url(url: str, use_cache: bool = True) -> Optional[str]:
    """Fetch a URL politely: checks validity, robots.txt, rate limits, cache,
    and retries. Returns the response body as text, or None on failure.
    Never raises — collectors must be able to continue past a single
    failed source.
    """
    if not is_valid_url(url):
        return None

    if not is_allowed_by_robots(url):
        return None

    if use_cache:
        cached = _read_cache(url)
        if cached is not None:
            return cached

    domain = get_domain(url)
    headers = {"User-Agent": settings.USER_AGENT}

    for attempt in range(settings.MAX_RETRIES + 1):
        try:
            _respect_rate_limit(domain)
            response = requests.get(
                url, headers=headers, timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            if response.status_code == 200:
                text = response.text
                if use_cache:
                    _write_cache(url, text)
                return text
            if response.status_code == 429:
                                                             
                time.sleep(2.0 * (attempt + 1))
                continue
            if response.status_code in (403, 404, 401):
                return None
        except requests.RequestException:
            time.sleep(0.5 * (attempt + 1))
            continue
    return None


def fetch_json(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> Optional[dict]:
    """Fetch and parse a JSON API endpoint politely. Returns None on any failure."""
    if not is_valid_url(url):
        return None
    domain = get_domain(url)
    req_headers = {"User-Agent": settings.USER_AGENT}
    if headers:
        req_headers.update(headers)

    for attempt in range(settings.MAX_RETRIES + 1):
        try:
            _respect_rate_limit(domain)
            response = requests.get(
                url, params=params, headers=req_headers, timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                time.sleep(2.0 * (attempt + 1))
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(0.5 * (attempt + 1))
            continue
    return None
