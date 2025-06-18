import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import pandas as pd
from typing import List, Dict

BASE_URL = "https://dailymedicalinfo.com"

def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def scrape_categories_list() -> List[Dict]:
    url = f"{BASE_URL}/diseases/?view=category"
    soup = get_soup(url)
    cats = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/disease-category/" in href:
            name = a.get_text(strip=True)
            full = urljoin(BASE_URL, href)
            cats.append({"name": name, "url": full})

    seen = set()
    unique = []
    for c in cats:
        if c["url"] not in seen:
            seen.add(c["url"])
            unique.append(c)

    return unique

def extract_content_clean(content_div) -> str:
    if not content_div:
        return ""

    toc_selectors = [
        "div[class*='toc']",
        "div[id*='toc']",
        "ul[class*='toc']",
        "nav",
        "div[class*='navigation']",
        "div[class*='breadcrumb']",
        "div[class*='menu']",
        "div[class*='sidebar']"
    ]

    irrelevant_phrases = [
        "سنتحدث", "في هذا المقال", "من خلال هذا المقال",
        "تعرف على", "يمكنك معرفة", "للمزيد من المعلومات",
        "اقرأ أيضًا", "تابع معنا", "تم النشر", "آخر تحديث",
        "المزيد من المقالات", "شارك المقال", "إخلاء", "تنويه",
        "المصادر", "فهرس المحتويات", "المحتويات", "انتقل إلى",
        "الفهرس", "مواضيع ذات صلة", "محتويات المقال",
        "سنتعرف عليها", "سنتعرف على", "سنعرف ما هي", "سنعرف",
        "كما سنعرف", "سنناقش", "سنتحدث عن", "سنستعرض", "سنستعرضها",
        "سنستعرضها لكم", "سنتناول", "سنتناولها", "سنتناولها لكم",
        "تعرفوا من","في هذا المقال سنتناول", "سنقوم بشرح", "سنوضح لكم","سنستعرض لكم", "سنقوم بشرح","تعرفوا","سنقوم بشرحها", "سنقوم بشرحها لكم","هل", "كيف", "كيف يمكننا", "كيف يمكننا التعامل مع", "كيف يمكننا علاج", "كيف يمكننا الوقاية من",
    ]

    soup_copy = BeautifulSoup(str(content_div), 'html.parser')

    for selector in toc_selectors:
        for element in soup_copy.select(selector):
            element.decompose()

    content_elements = soup_copy.find_all(["p", "h2", "h3", "h4", "li"])

    cleaned_paragraphs = []
    for element in content_elements:
        text = element.get_text(strip=True)

        if not text or len(text) < 20:
            continue

        if any(phrase in text for phrase in irrelevant_phrases):
            continue

        if element.name == "li":
            links = element.find_all("a")
            if len(links) > 0 and len(text) < 100:
                continue

        if text.count('.') > 3 and any(char.isdigit() for char in text[:10]):
            continue

        cleaned_paragraphs.append(text)

    return "\n".join(cleaned_paragraphs)

def scrape_articles(cat_url: str) -> List[Dict]:
    try:
        soup = get_soup(cat_url)
    except Exception as e:
        print(f"Error fetching category page: {e}")
        return []

    results = []
    article_count = 0

    possible_selectors = [
        "h2 a[href*='/']",
        "h3 a[href*='/']",
        ".entry-title a",
        "article h2 a",
        "article h3 a"
    ]

    for selector in possible_selectors:
        if article_count >= 20:
            break

        for a in soup.select(selector):
            if article_count >= 20:
                break

            href = a.get("href")
            if not href or "dailymedicalinfo.com" not in urljoin(BASE_URL, href):
                continue

            title = a.get_text(strip=True)
            if not title:
                continue

            link = urljoin(BASE_URL, href)

            try:
                print(f"  Scraping: {title[:50]}...")
                art_soup = get_soup(link)

                content_div = (
                    art_soup.find("div", class_="entry-content") or
                    art_soup.find("div", class_="post-content") or
                    art_soup.find("article") or
                    art_soup.find("main")
                )

                doc = extract_content_clean(content_div)

                if doc and len(doc) > 200:
                    results.append({
                        "title": title,
                        "doc": doc,
                        "url": link
                    })
                    article_count += 1

            except Exception as e:
                print(f"    Error scraping article {title}: {e}")
                continue

            time.sleep(1)

    return results

def main():
    output: List[Dict] = []
    categories = scrape_categories_list()

    print(f"Found {len(categories)} categories")

    for i, cat in enumerate(categories, 1):
        print(f"\n[{i}/{len(categories)}] Processing category: {cat['name']}")

        try:
            articles = scrape_articles(cat["url"])
            if not articles:
                print("  (no articles found)")
                continue

            output.append({
                "category": cat["name"],
                "articles": articles
            })

            print(f"  Found {len(articles)} articles")

        except Exception as e:
            print(f"  Error processing category: {e}")
            continue

    with open("scraped_articles.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nWrote scraped_articles.json with {len(output)} categories")

    rows = []
    for cat_block in output:
        cat_name = cat_block["category"]
        for art in cat_block["articles"]:
            rows.append({
                "category": cat_name,
                "title": art["title"],
                "doc": art["doc"],
                "url": art["url"]
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df.insert(0, "QID", range(1, len(df) + 1))
        df.to_csv("QAjenin4.csv", index=False, encoding="utf-8-sig")
        print(f"Wrote QAjenin4.csv with {len(df)} articles")
    else:
        print("No articles found to save")

if __name__ == "__main__":
    main()
