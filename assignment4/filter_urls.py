"""
Task 1.2, 1.3

Filtering URLs from HTML
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse


def find_urls(
    html: str,
    base_url: str = "https://en.wikipedia.org",
    output: str | None = None,
) -> set[str]:
    """
    Find all the url links in a html text using regex

    Arguments:
        html (str): html string to parse
        base_url (str): the base url to the wikipedia.org pages
        output (Optional[str]): file to write to if wanted
    Returns:
        urls (Set[str]) : set with all the urls found in html text
    """
    
    anchor_tags = re.compile(r'href="([^"]+)"', flags=re.IGNORECASE)
    matches = re.findall(anchor_tags, html)

    urls = set()
    for match in matches:
        # Handle same-protocol links
        if match.startswith("//"):
            protocol = base_url.split("://")[0]  # Splitting to get the protocol
            full_url = f"{protocol}:{match}"
            urls.add(full_url)
        # Check if the URL starts with 'https://' or 'http://'
        elif match.startswith("https://") or match.startswith("http://"):
            urls.add(match)
        # Handle URLs that are paths on the same host
        elif match.startswith("/"):
            # Use urljoin to correctly handle relative paths
            full_url = urljoin(base_url, match)
            urls.add(full_url)

    
    urls = {url.split('#')[0] for url in urls}

    # Write to file if requested
    if output:
        print(f"Writing to: {output}")
        with open(output, 'w') as file:
            for url in urls:
                file.write(url + '\n')
    
    return urls


def find_articles(
    html: str,
    output: str | None = None,
    base_url: str = "https://en.wikipedia.org",
) -> set[str]:
    """Finds all the wiki articles inside a html text. Make call to find urls, and filter
    arguments:
        - text (str) : the html text to parse
        - output (str, optional): the file to write the output to if wanted
        - base_url (str, optional): the base_url to pass through to find_urls
    returns:
        - (Set[str]) : a set with urls to all the articles found
    """
    
    urls = find_urls(html, base_url=base_url)

    # regex pattern to match 
    article_pattern = re.compile(r"^https?://[a-z]{2,3}\.wikipedia\.org/wiki/([^:#]*)$", re.IGNORECASE)

    # Initialize an empty set 
    articles = set()

    # for loop to filter 
    for url in urls:
        if article_pattern.match(url):
            articles.add(url)

    # Write to file if wanted
    if output:
        with open(output, 'w') as f:
            for article in articles:
                f.write(article + '\n')
    
    return articles


## Regex example
def find_img_src(html: str):
    """Find all src attributes of img tags in an HTML string

    Args:
        html (str): A string containing some HTML.

    Returns:
        src_set (set): A set of strings containing image URLs

    The set contains every found src attribute of an img tag in the given HTML.
    """

    img_pat = re.compile(r"<img[^>]+>", flags=re.IGNORECASE)
    src_pat = re.compile(r'src="([^"]+)"', flags=re.IGNORECASE)
    src_set = set()
    # find all the img tags
    for img_tag in img_pat.findall(html):
        # then find the src attribute
        match = src_pat.search(img_tag)
        if match:
            src_set.add(match.group(1))
    return src_set
