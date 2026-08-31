"""
General web collector.

Uses DuckDuckGo's HTML search endpoint (no API key required, and it is
explicitly tolerant of simple automated GET requests for its lite/html
interface) to discover publicly indexed pages about the subject, then
fetches and extracts readable text from each permitted page with
BeautifulSoup.

This module strictly avoids anything that looks like scraping behind
authentication or bypassing protections: if a page can't be fetched
cleanly (blocked, requires JS, robots.txt disallows it), it is skipped.
"""
from __future__ import annotations

from urllib.parse import quote_plus, urlparse, parse_qs, unquote

from bs4 import BeautifulSoup

from collectors.base import fetch_url, get_domain, is_valid_url
from core.schemas import CollectedSource

DUCKDUCKGO_HTML = "https://html.duckduckgo.com/html/?q="

                                                                     
                                                             
SKIP_DOMAINS = {
    "youtube.com", "youtu.be", "facebook.com", "instagram.com",
    "twitter.com", "x.com", "tiktok.com", "pinterest.com",
    "amazon.com", "ebay.com",
}


def _extract_ddg_links(html: str, limit: int) -> list[tuple[str, str]]:
    """Parse DuckDuckGo HTML results into (title, url) pairs."""
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str, str]] = []

    for result in soup.select("a.result__a"):
        href = result.get("href", "")
        title = result.get_text(strip=True)
        if not href or not title:
            continue

                                                                    
        real_url = href
        if "duckduckgo.com/l/" in href or href.startswith("//duckduckgo.com/l/"):
            parsed = urlparse(href if href.startswith("http") else "https:" + href)
            qs = parse_qs(parsed.query)
            if "uddg" in qs:
                real_url = unquote(qs["uddg"][0])

        if not is_valid_url(real_url):
            continue
        domain = get_domain(real_url)
        if any(skip in domain for skip in SKIP_DOMAINS):
            continue

        results.append((title, real_url))
        if len(results) >= limit:
            break

    return results


def _extract_readable_text(html: str) -> str:
    """Pull the main readable text out of an HTML page, stripping nav/script/etc."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
        tag.decompose()

    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)

    if len(text) < 200:
                                                                             
                                                            
        body = soup.find("body")
        text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)

    return text[:20000]                                     


def _extract_title(html: str, fallback: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return fallback


def collect(subject: str, max_pages: int = 8) -> list[CollectedSource]:
    """Search the public web for the subject and collect readable pages."""
    sources: list[CollectedSource] = []

    search_url = DUCKDUCKGO_HTML + quote_plus(subject)
    search_html = fetch_url(search_url, use_cache=True)
    if not search_html:
        return sources

    try:
        candidates = _extract_ddg_links(search_html, limit=max_pages)
    except Exception:
                                                                        
                                                                         
        return sources

    for i, (title, url) in enumerate(candidates):
        page_html = fetch_url(url, use_cache=True)
        if not page_html:
            continue
        try:
            text = _extract_readable_text(page_html)
            if len(text) < 100:
                continue                                   
            resolved_title = _extract_title(page_html, fallback=title)
            sources.append(
                CollectedSource(
                    title=resolved_title,
                    url=url,
                    domain=get_domain(url),
                    source_type="web",
                    published_at=None,
                    raw_text=text,
                    summary=text[:400],
                    relevance_score=max(0.25, 0.85 - i * 0.07),
                )
            )
        except Exception:
            continue

    return sources
