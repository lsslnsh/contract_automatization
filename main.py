import json
from pathlib import Path

folder = Path(__file__).resolve().parent

with open(folder / "prices.json", encoding="utf-8-sig") as file:
    prices = json.load(file)

service_options = {
    "лск": "lsk",
    "аудит": "audit",
    "сопровождение": "support"
}

service_name = input("Укажите услугу: лск, аудит или сопровождение: ").strip().lower()

while service_name not in service_options:
    service_name = input("Не удалось найти услугу. Введите лск, аудит или сопровождение: ").strip().lower()

service = service_options[service_name]
base_price = prices["services"][service]["base_price"]
usn_percent = prices["usn_percent"]

final_price = round(base_price * (1 + usn_percent / 100))
