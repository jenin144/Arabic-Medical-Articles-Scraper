# 🩺 Arabic Medical Articles Scraper

A Python-based web scraping tool designed to collect and clean Arabic medical articles from [dailymedicalinfo.com](https://dailymedicalinfo.com). It extracts high-quality content across +600 medical categories, stores it in both JSON and CSV formats, and prepares it for Arabic NLP applications.

The script written as part of Arabic QA System project for medical and healthcare domains using NLP Tasks.



## 📌 Features

- Scrapes **600 medical categories** automatically
- Cleans content from noise like:
  - Navigation menus
  - Promotional text
  - Irrelevant phrases (e.g., "سنتحدث عن", "تابع معنا")
- Extracts:
  - Article titles
  - Cleaned article body
  - Source URLs
- Saves output to:
  - `scraped_articles.json` → structured by category
  - `QAjenin4.csv` → flat format with QID and fields

---

## 🚀 How It Works

1. **Category Discovery**  
   Extracts all disease-related category pages dynamically.

2. **Article Extraction**  
   For each category, scrapes up to **20 articles**:
   - Parses HTML using BeautifulSoup
   - Removes noise (sidebars, TOCs, disclaimers)
   - Retains only informative content blocks (p, h2-h4, li)

3. **Output Generation**
   - JSON: structured per category
   - CSV: flat file with all articles for easy use in QA/NLP systems

---

Install all required libraries using: pip install requests beautifulsoup4 pandas

▶️ Running the Scraper: python get_links.py

## 🧪 Example Output

```json
{
  "category": "امراض القلب",
  "articles": [
    {
      "title": "ما هو الذبحة الصدرية؟",
      "doc": "الذبحة الصدرية هي نوع من ألم الصدر ...",
      "url": "https://dailymedicalinfo.com/view/..."
    },
    ...
  ]
}
