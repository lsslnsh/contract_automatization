import json
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from num2words import num2words

folder = Path(__file__).resolve().parent

with open(folder / "prices.json", encoding="utf-8-sig") as file:
    prices = json.load(file)

#Выбор услуги договора и актуальной стоимости
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

service_short_names = {
    "lsk": "ЛСК",
    "audit": "Аудит",
    "support": "Сопровождение"}

def read_client_info():
    client_lines = []

    while True:
        line = input()

        if line.strip() == "КОНЕЦ":
            return client_lines

        client_lines.append(line)

#Ввод данных от менеджера
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

clean_client_info = []

for info in client_info:
    clean_client_info.append(info.strip())

client_data = {
    "client_fio": clean_client_info[0],
    "client_passport": clean_client_info[1],
    "client_passport_issued": clean_client_info[2],
    "client_passport_issued_date": clean_client_info[3],
    "client_code": clean_client_info[4],
    "client_address": clean_client_info[5],
    "client_phone": clean_client_info[6],
    "client_email": clean_client_info[7]
}

#Проверка коррктности ввода фио
def is_valid_fio(fio):
    fio_parts = fio.split()

    if len(fio_parts) < 2:
        return False

    return True

while not is_valid_fio(client_data["client_fio"]):
    client_data["client_fio"] = input("Введите корректные фамилию, имя и отчество при наличии:\n").strip()

#Проверка корректности ввода серии и номера паспорта
def is_valid_passport(passport):
    passport_series_number = "".join(passport.split())

    return (
        len(passport_series_number) == 10
        and passport_series_number.isascii()
        and passport_series_number.isdigit()
    )

while not is_valid_passport(client_data["client_passport"]):
    client_data["client_passport"] = input(
        "Введите корректные серию и номер паспорта:\n"
    ).strip()

passport_series_number = "".join(client_data["client_passport"].split())

client_data["client_passport"] = (
    passport_series_number[:4] + " " + passport_series_number[4:]
)

#Проверка корректности ввода даты и органа выдачи паспорта 
def is_valid_date(value):
    try:
        datetime.strptime(value, "%d.%m.%Y")
    except ValueError:
        return False

    return True

while not client_data["client_passport_issued"].strip():
    client_data["client_passport_issued"] = input(
        "Укажите корректно, кем выдан паспорт:\n"
    ).strip()

while not is_valid_date(client_data["client_passport_issued_date"]):
    client_data["client_passport_issued_date"] = input(
        "Введите корректную дату выдачи в формате ДД.ММ.ГГГГ:\n"
    ).strip()

#Проверка телефона
def is_valid_phone(phone):
    phone = "".join(phone.split())

    for symbol in ("(", ")", "-"):
        phone = phone.replace(symbol, "")

    if phone.startswith("+"):
        phone = phone[1:]

    return phone.isascii() and phone.isdigit()

while not is_valid_phone(client_data["client_phone"]):
    client_data["client_phone"] = input(
        "Введите телефон с кодом страны:\n"
    ).strip()

#Проверка кода подразделения
def is_valid_department_code(code):
    if len(code) == 7 and code[3] == "-":
        code = code[:3] + code[4:]

    return (
        len(code) == 6
        and code.isascii()
        and code.isdigit()
    )

while not is_valid_department_code(client_data["client_code"]):
    client_data["client_code"] = input("Введите корректный код подразделения, в котором выдан паспорт:\n").strip()

department_code = client_data["client_code"].replace("-", "")

client_data["client_code"] = (department_code[:3] + "-" + department_code[3:])

#Проверка адреса
while not client_data["client_address"].strip():
    client_data["client_address"] = input("Введите коррктный адрес регистрации:\n").strip()


#Проверка адреса эл почты
def is_valid_email(email):
    if email.count("@") != 1:
        return False

    for symbol in email:
        if symbol.isspace():
            return False

    email_parts = email.split("@")
    email_name = email_parts[0]
    email_domain = email_parts[1]

    if not email_name:
        return False

    if "." not in email_domain:
        return False

    if email_domain.startswith(".") or email_domain.endswith("."):
        return False

    return True

while not is_valid_email(client_data["client_email"]):
    client_data["client_email"] = input("Введите почту в формате name@example.com без пробелов:\n").strip()


#Выбор нужного шаблона
template_files = {
    "lsk": "01_Физлицо_ЛСК.docx",
    "audit": "02_Физлицо_HR_аудит.docx",
    "support": "03_Физлицо_Сопровождение.docx"}

template_path = folder / "templates_fiz" / template_files[service]

template = DocxTemplate(template_path)

template_fields = template.get_undeclared_template_variables()

for field in sorted(template_fields):
    print(field)

#Подготовка данных для полей договора
contract_fields = client_data.copy()

contract_fields["client_signature"] = client_data["client_fio"]
contract_fields["final_price"] = final_price

contract_date = input("Введите дату договора в формате ДД.ММ.ГГГГ:\n").strip()

while not is_valid_date(contract_date):
    contract_date = input("Введите корректную дату договора в формате ДД.ММ.ГГГГ:\n").strip()

contract_date_correct = datetime.strptime(contract_date, "%d.%m.%Y")

contract_fields["number"] = contract_date_correct.strftime("%d-%m-%Y")
contract_fields["contract_date_long"] = contract_date_correct.strftime("%d.%m.%Y")
contract_fields["year"] = contract_date_correct.year


#Подготовка даты проведения услуги
if service in ("lsk", "audit"):
    service_date = input(
        "Введите дату проведения услуги в формате ДД.ММ.ГГГГ:\n"
    ).strip()

    while not is_valid_date(service_date):
        service_date = input(
            "Введите корректную дату проведения услуги в формате ДД.ММ.ГГГГ:\n"
        ).strip()

    service_date_object = datetime.strptime(service_date, "%d.%m.%Y")

    contract_fields["service_date_long"] = service_date_object.strftime("%d.%m.%Y")

#Подготовка стоимости прописью
def ruble_word(amount):
    if 11 <= amount % 100 <= 14:
        return "рублей"

    if amount % 10 == 1:
        return "рубль"

    if amount % 10 in (2, 3, 4):
        return "рубля"

    return "рублей"


contract_fields["final_price_words"] = num2words(final_price, lang="ru")
contract_fields["final_currency"] = ruble_word(final_price)

#Заполнение полей договора данными от пользователя и сохранение договора
template_fields = template.get_undeclared_template_variables()
missing_fields = template_fields - contract_fields.keys()

if missing_fields:
    print("Документ пока не создан. Заполните поля:")

    for field in sorted(missing_fields):
        print(field)
else:
    output_folder = folder / "output"
    output_folder.mkdir(exist_ok=True)

    client_name = client_data["client_fio"]
    service_title = service_short_names[service]

    output_name = f"Договор_{service_title}_{client_name}.docx"

    for symbol in '<>:"/\\|?*':
        output_name = output_name.replace(symbol, "_")

    output_path = output_folder / output_name

    if output_path.exists():
        print("Документ с таким именем уже существует:", output_path)
    else:
        template.render(contract_fields, autoescape=True)
        template.save(output_path)
        data_folder = folder / "data"
        data_folder.mkdir(exist_ok=True)

        data_path = data_folder / (output_path.stem + ".json")

        order_data = {"service": service,"contract_fields": contract_fields}

        with open(data_path, "w", encoding="utf-8") as file:
            json.dump(order_data, file, ensure_ascii=False, indent=4)

        print("Данные договора сохранены:", data_path)

        print("Договор сохранён:", output_path)






    