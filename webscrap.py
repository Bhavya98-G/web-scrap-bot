import requests
from bs4 import BeautifulSoup
from readability.readability import Document
from collections import OrderedDict
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def extract_meaningful_text(url: str) -> dict:
    # ---------- URL Validation ----------
    if not is_valid_url(url):
        return {
            "status": "error",
            "message": "Invalid URL format",
            "title": "",
            "content": ""
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TextExtractor/1.0)"
    }

    # ---------- Network Handling ----------
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timed out",
            "title": "",
            "content": ""
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Website unreachable",
            "title": "",
            "content": ""
        }
    except requests.exceptions.HTTPError as e:
        return {
            "status": "error",
            "message": f"HTTP error: {e.response.status_code}",
            "title": "",
            "content": ""
        }
    except requests.exceptions.RequestException:
        return {
            "status": "error",
            "message": "Request failed",
            "title": "",
            "content": ""
        }

    # ---------- Content-Type Check ----------
    if "text/html" not in response.headers.get("Content-Type", "").lower():
        return {
            "status": "error",
            "message": "Unsupported content type (HTML only)",
            "title": "",
            "content": ""
        }

    # ---------- Extract Title ----------
    soup_full = BeautifulSoup(response.text, "lxml")
    title = soup_full.title.string.strip() if soup_full.title and soup_full.title.string else "Untitled Page"

    # ---------- Extract Main Content ----------
    try:
        doc = Document(response.text)
        html = doc.summary(html_partial=True)
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        return {
            "status": "error",
            "message": "Failed to parse HTML content",
            "title": title,
            "content": ""
        }

    # ---------- Remove Irrelevant Sections ----------
    for tag in soup([
        "script", "style", "noscript", "header", "footer",
        "nav", "aside", "form", "iframe"
    ]):
        tag.decompose()

    # ---------- Extract Meaningful Text ----------
    lines = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "h4", "h5", "h6"]):
        text = tag.get_text(strip=True)
        if len(text) > 30:
            lines.append(text)

    # ---------- Remove Duplicates ----------
    unique_text = list(OrderedDict.fromkeys(lines))

    if not unique_text:
        return {
            "status": "error",
            "message": "No meaningful content found",
            "title": title,
            "content": ""
        }

    return {
        "status": "success",
        "message": "Content extracted successfully",
        "title": title,
        "content": "\n\n".join(unique_text)
    }


if __name__ == "__main__":
    url = input("Enter website URL: ").strip()
    result = extract_meaningful_text(url)

    print("\nSTATUS:", result["status"].upper())
    print("MESSAGE:", result["message"])
    print("TITLE:", result["title"])

    if result["status"] == "success":
        print("\nEXTRACTED CONTENT (preview):\n")
        print(result["content"][:3000])
