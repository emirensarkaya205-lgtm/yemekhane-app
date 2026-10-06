import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def run():
  # Hedef üniversite SKS yemekhane linki
  url = "https://sks.isparta.edu.tr/tr/yemek-menusu"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  foods = []
  today_str = datetime.now().strftime("%d.%m.%Y")

  try:
    res = requests.get(url, headers=headers, timeout=15)
    res.encoding = "utf-8"

    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      elements = soup.find_all("div", class_="menu-item-text")
      for el in elements[:4]:
        name = el.get_text(strip=True)
        if name:
          foods.append({"name": name, "calories": 250})
  except Exception as e:
    print(f"Scraper uyarısı: {e}")

  if not foods:
    foods = [
        {"name": "Günün Çorbası", "calories": 140},
        {"name": "Ana Yemek", "calories": 380},
        {"name": "Yardımcı Yemek", "calories": 240},
        {"name": "Tatlı / Meyve", "calories": 120},
    ]

  json_path = os.path.join(os.path.dirname(__file__), "data", "menu.json")
  stats = {"rating_average": 4.2, "rating_count": 18, "crowd": "Sıra Yok"}

  if os.path.exists(json_path):
    try:
      with open(json_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)
        if "stats" in old_data:
          stats = old_data["stats"]
    except Exception:
      pass

  payload = {
      "date": today_str,
      "meal_type": "Öğle Yemeği",
      "total_calories": sum(item["calories"] for item in foods),
      "foods": foods,
      "stats": stats,
  }

  os.makedirs(os.path.dirname(json_path), exist_ok=True)
  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

  print("data/menu.json başarıyla güncellendi.")


if __name__ == "__main__":
  run()
