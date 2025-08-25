import requests
from bs4 import BeautifulSoup
import string
import os

BASE_URL = "https://www.nature.com"
URL = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page="


def clean_filename(title: str) -> str:
    return title.translate(str.maketrans('', '', string.punctuation)).strip().replace(' ', '_')


def fetch_page(url: str) -> BeautifulSoup | None:
    response = requests.get(url, headers={"Accept-Language": "en-US,en;q=0.5"})
    return BeautifulSoup(response.content, "html.parser") if response.status_code == 200 else None


def fetch_article(url: str) -> tuple[str, str] | None:
    soup = fetch_page(url)
    if not soup:
        return None

    title_tag = soup.find("h1")
    if not title_tag:
        return None

    title = title_tag.text.strip()
    teaser = soup.find("p", {"class": "article__teaser"})
    if not teaser:
        return None

    body_text = teaser.text.strip()
    return title, body_text


def save_article(title: str, text: str, page_num: int) -> str:
    filename = clean_filename(title) + ".txt"
    folder = f"Page_{page_num}"
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))
    return path


def main():
    pages = int(input().strip())
    article_type = input().strip()

    for i in range(1, pages + 1):
        folder = f"Page_{i}"
        os.makedirs(folder, exist_ok=True)

        url = f"{URL}{i}"
        soup = fetch_page(url)
        if not soup:
            continue

        for art in soup.find_all("article"):
            span = art.find("span", {"data-test": "article.type"})
            if not span or span.text.strip() != article_type:
                continue

            link = art.find("a", {"data-track-action": "view article"})
            if not link:
                continue

            article_url = BASE_URL + link.get("href")
            data = fetch_article(article_url)
            if not data:
                continue

            title, text = data
            save_article(title, text, i)

    print("Saved all articles.")


if __name__ == "__main__":
    main()
