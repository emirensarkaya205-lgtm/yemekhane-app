import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def run():
  # Ağrı İbrahim Çeçen Üniversitesi SKS Yemekhane sayfası
  url = "https://sks.agri.edu.tr/detail.aspx?id=1152"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  foods = []
  today_str = datetime.now().strftime("%d.%m.%Y")

  try:
    res = requests.get(url, headers=headers, timeout=20, verify=False)
    res.encoding = "utf-8"

    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")

      # AİÇÜ detay sayfasındaki tablo satırlarını veya içerik paragraflarını tara
      # Sayfada tablo varsa:
      tables = soup.find_all("table")
      extracted_texts = []

      for table in tables:
        rows = table.find_all("tr")
        for row in rows:
          cols = row.find_all(["td", "th"])
          col_texts = [c.get_text(strip=True) for c in cols if c.get_text(strip=True)]
          for text in col_texts:
            # Sayı veya çok kısa başlık olmayanları yemek olarak kabul et
            if len(text) > 3 and not text.isdigit():
              extracted_texts.append(text)

      # Eğer tabloda bulunamadıysa içerik alanındaki paragrafları / div'leri tara
      if not extracted_texts:
        content_area = soup.find("div", id=re.compile(r"content|icerik|detail", re.I))
        if content_area:
          paragraphs = content_area.find_all(["p", "div", "li"])
          for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 3:
              extracted_texts.append(text)

      # İlk 4 geçerli yemek adını listeye aktar
      for item in extracted_texts[:4]:
        foods.append({
            "name": item,
            "calories": 250  # Sitede kalori belirtilmediyse varsayılan değer
        })

  except Exception as e:
    print(f"Scraper hatası: {e}")

  # Eğer siteden veri çekilemezse mevcut veritabanını bozma
  json_path = os.path.join(os.path.dirname(__file__), "data", "menu.json")
  stats = {"rating_average": 4.5, "rating_count": 12, "crowd": "Normal"}

  if os.path.exists(json_path):
    try:
      with open(json_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
        if not foods and "foods" in old_data:
          foods = old_data["foods"]
        if "stats" in old_data:
          stats = old_data["stats"]
    except Exception:
      pass

  if not foods:
    foods = [
        {"name": "Mercimek Çorbası", "calories": 140},
        {"name": "Etli Kuru Fasulye", "calories": 360},
        {"name": "Pirinç Pilavı", "calories": 280},
        {"name": "Mevsim Salata", "calories": 60}
    ]

  payload = {
      "date": today_str,
      "meal_type": "Öğle Yemeği",
      "total_calories": sum(item.get("calories", 0) for item in foods),
      "foods": foods,
      "stats": stats,
  }

  os.makedirs(os.path.dirname(json_path), exist_ok=True)
  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

  print("data/menu.json başarıyla güncellendi.")


if __name__ == "__main__":
  run()
