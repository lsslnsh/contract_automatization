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

def read_client_info():
    client_lines = []

    while True:
        line = input()

        if line.strip() == "КОНЕЦ":
            return client_lines

        client_lines.append(line)


print("Вставьте следующие данные в том же порядке, каждую составляющую с новой строки:\n"
    "ФИО\n"
    "Серия и номер паспорта\n"
    "Кем выдан\n"
    "Дата выдачи\n"
    "Код подразделения\n"
    "Адрес регистрации\n"
    "Телефон\n"
    "Почта\n"
    "Введите КОНЕЦ на отдельной строке после окончания.")

client_info = read_client_info()

while len(client_info) != 8:
    print("Нужно ввести недостающие данные. Вставьте полностью все данные, каждую составляющую с новой строки: " \
        "ФИО\n"
        "Серия и номер паспорта\n"
        "Кем выдан\n"
        "Дата выдачи\n"
        "Код подразделения\n"
        "Адрес регистрации\n"
        "Телефон\n"
        "Почта\n"
        "Напишите КОНЕЦ на последней строке.")
    
    client_info = read_client_info()

    