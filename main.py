import json
from pathlib import Path
from datetime import datetime, timedelta
from zipfile import BadZipFile

try:
    from docxtpl import DocxTemplate
    from num2words import num2words
    from docx.opc.exceptions import PackageNotFoundError
    from jinja2.exceptions import TemplateError
    from lxml.etree import XMLSyntaxError
except ModuleNotFoundError as error:
    raise SystemExit(
        f"Не установлена библиотека {error.name}. Установите зависимости из requirements.txt."
    )

#функция для чтения JSON файлов с названиями и ценами услуг
def read_json(path):
    with path.open(encoding="utf-8-sig") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(f"В файле {path.name} неверный JSON, строка {error.lineno}.") from error
    
    if not isinstance(data, dict):
        raise ValueError(f"В файле {path.name} нужен JSON-объект в фигурных скобках.")
    
    return data

#функция для проверки наличия правильных названий и цен услуг
def validate_prices(prices):
    for key in ("usn_percent", "additional_hour"):
        value = prices.get(key)
        
        if type(value) is not int or value < 0:
            raise ValueError(f"В prices.json поле {key} должно быть целым неотрицательным числом.")
    services = prices.get("services")
    
    if not isinstance(services, dict):
        raise ValueError("В prices.json отсутствует словарь services.")
    
    for service in ("lsk", "audit", "support"):
        item = services.get(service)
        
        if not isinstance(item, dict):
            raise ValueError(f"В prices.json отсутствует услуга {service}.")
        name = item.get("name")
        
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Не задано название услуги {service}.")
        amount = item.get("base_price")
        
        if type(amount) is not int or amount <= 0:
            raise ValueError(f"Цена услуги {service} должна быть целым числом больше нуля.")

#функция для проверки наличия правильных шаблонов документов
def read_template(path):
    if not path.is_file():
        raise FileNotFoundError(f"Не найден шаблон: {path}")
    try:
        template = DocxTemplate(path)
        fields = template.get_undeclared_template_variables()
    except (BadZipFile, PackageNotFoundError, XMLSyntaxError, KeyError) as error:
        raise ValueError(f"Повреждён шаблон {path.name}. Восстановите корректный файл DOCX.") from error
    return template, fields

#функция для обработки введенных данных от пользователя
def read_client_info():
    client_lines = []

    while True:
        line = input()

        if line.strip() == "КОНЕЦ":
            return client_lines

        client_lines.append(line)

#функция для проверки правильности фио
def is_valid_fio(fio):
    fio_parts = fio.split()

    if len(fio_parts) < 2:
        return False

    return True

#функция для проверки правильности серии и номера паспорта
def is_valid_passport(passport):
    passport_series_number = "".join(passport.split())

    return (
        len(passport_series_number) == 10
        and passport_series_number.isascii()
        and passport_series_number.isdigit()
    )
#функция для проверки правильности кода подразделения, выдавшего паспорт
def is_valid_department_code(code):
    if len(code) == 7 and code[3] == "-":
        code = code[:3] + code[4:]

    return (
        len(code) == 6
        and code.isascii()
        and code.isdigit()
    )

#функция для проверки правильности даты
def read_date(prompt, value=None):
    while True:
        if value is None:
            value = input(prompt).strip()

        try:
            return datetime.strptime(value, "%d.%m.%Y")

        except ValueError:
            print("Введите корректную дату в формате ДД.ММ.ГГГГ.")
            value = None

#функция для проверки правильности телефона
def is_valid_phone(phone):
    phone = "".join(phone.split())

    for symbol in ("(", ")", "-"):
        phone = phone.replace(symbol, "")

    if phone.startswith("+"):
        phone = phone[1:]

    return phone.isascii() and phone.isdigit()

#функция для проверки правильности электронного адреса
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

    if ".." in email:
        return False

    return True

#подготовка текста для договора сопровождения
def support_text(prompt):
    value = input(prompt).strip()

    while not value:
        value = input("Поле не должно быть пустым. Введите значение:\n").strip()

    return value

#функция для проверки длительности программы Сопровождения
def support_lenth(prompt):
    while True:
        value = input(prompt).strip()

        if value.isascii() and value.isdigit():
            number = int(value)

            if number > 0:
                return number

        print("Введите целое число больше нуля.")

#функция для преобразования суммы договора в текст прописью
def ruble_word(amount):
    if 11 <= amount % 100 <= 14:
        return "рублей"

    if amount % 10 == 1:
        return "рубль"

    if amount % 10 in (2, 3, 4):
        return "рубля"

    return "рублей"

#функция для запуска процесса заполнения документа
def main():
    folder = Path(__file__).resolve().parent

    prices = read_json(folder / "input" / "prices.json")
    validate_prices(prices)

    # Чтение вымышленных реквизитов исполнителя
    provider_path = folder / "provider_data" / "provider.example.json"

    provider = read_json(provider_path)
    for field, value in provider.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"В {provider_path.name} поле {field} должно содержать непустой текст.")

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


    #Ввод данных от пользователя
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
        print(f"Ожидается 8 строк, получено {len(client_info)}. Вставьте все данные заново:\n"
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

    while not is_valid_fio(client_data["client_fio"]):
        client_data["client_fio"] = input("Введите корректные фамилию, имя и отчество при наличии:\n").strip()

    #Проверка корректности ввода серии и номера паспорта

    while not is_valid_passport(client_data["client_passport"]):
        client_data["client_passport"] = input(
            "Введите корректные серию и номер паспорта:\n"
        ).strip()

    client_data["client_fio"] = " ".join(client_data["client_fio"].split())

    passport_series_number = "".join(client_data["client_passport"].split())

    client_data["client_passport"] = (
        passport_series_number[:4] + " " + passport_series_number[4:]
    )

    #Проверка корректности ввода даты и органа выдачи паспорта 

    while not client_data["client_passport_issued"].strip():
        client_data["client_passport_issued"] = input(
            "Укажите корректно, кем выдан паспорт:\n"
        ).strip()

    passport_date = read_date(
        "Введите корректную дату выдачи паспорта в формате ДД.ММ.ГГГГ:\n",
        client_data["client_passport_issued_date"]
    )

    client_data["client_passport_issued_date"] = passport_date.strftime("%d.%m.%Y")

    #Проверка телефона

    while not is_valid_phone(client_data["client_phone"]):
        client_data["client_phone"] = input(
            "Введите телефон с кодом страны:\n"
        ).strip()

    #Проверка кода подразделения

    while not is_valid_department_code(client_data["client_code"]):
        client_data["client_code"] = input("Введите корректный код подразделения, в котором выдан паспорт:\n").strip()

    department_code = client_data["client_code"].replace("-", "")

    client_data["client_code"] = (department_code[:3] + "-" + department_code[3:])

    #Проверка адреса
    while not client_data["client_address"].strip():
        client_data["client_address"] = input("Введите коррктный адрес регистрации:\n").strip()


    #Проверка адреса эл почты
    while not is_valid_email(client_data["client_email"]):
        client_data["client_email"] = input("Введите почту в формате name@example.com без пробелов:\n").strip()


    #Выбор нужного шаблона
    template_files = {
        "lsk": "01_Физлицо_ЛСК.docx",
        "audit": "02_Физлицо_HR_аудит.docx",
        "support": "03_Физлицо_Сопровождение.docx"}

    template_path = folder / "templates_fiz" / template_files[service]

    template, template_fields = read_template(template_path)

    #Подготовка данных для полей договора
    contract_fields = client_data.copy()
    contract_fields.update(provider)

    contract_fields["client_signature"] = client_data["client_fio"]
    contract_fields["final_price"] = final_price

    contract_date_correct = read_date("Введите дату договора в формате ДД.ММ.ГГГГ:\n")

    contract_fields["number"] = contract_date_correct.strftime("%d-%m-%Y")
    contract_fields["contract_date_long"] = contract_date_correct.strftime("%d.%m.%Y")
    contract_fields["year"] = contract_date_correct.year

    #Запрос даты проведения услуги
    service_date = read_date("Введите дату проведения услуги в формате ДД.ММ.ГГГГ:\n")

    while service_date < contract_date_correct:
        print("Дата проведения услуги не должна быть ранее даты заключения договора.")
        service_date = read_date("Введите дату проведения или начала услуги, ДД.ММ.ГГГГ:\n")

    contract_fields["service_date_long"] = service_date.strftime("%d.%m.%Y")

    #Подготовка кол-ва встреч в рамках Сопровождения
    if service == "support":
        contract_fields["meeting_count"] = support_lenth("Введите количество встреч по программе сопровождения:\n")

    #Подготовка стоимости прописью
    contract_fields["final_price_words"] = num2words(final_price, lang="ru")
    contract_fields["final_currency"] = ruble_word(final_price)


    if service in ("audit", "support"):
        extra_price = prices["additional_hour"]

        contract_fields["extra_price"] = extra_price
        contract_fields["extra_price_words"] = num2words(extra_price, lang="ru")

    #Подготовка акта проведения услуг
    if service == "support":
        if service_date.month == 12:
            act_date = service_date.replace(
                year=service_date.year + 1,
                month=1,
                day=1
            )
        else:
            act_date = service_date.replace(
                month=service_date.month + 1,
                day=1
            )
    else:
        act_date = service_date + timedelta(days=1)

    while act_date.weekday() >= 5:
        act_date = act_date + timedelta(days=1)

    act_fields = contract_fields.copy()

    act_fields["act_date_long"] = act_date.strftime("%d.%m.%Y")
    act_fields["service_name"] = prices["services"][service]["name"]

#добавление длительности (количества встреч) в договор услуги Сопровождения
    if service == "support":
        act_fields["service_name"] = (
            f"{act_fields['service_name']}. Количество сессий: "
            f"{contract_fields['meeting_count']}. Продолжительность каждой: 1,5 часа."
        )

    act_template_path = folder / "templates_fiz" / "04_Физлицо_АВР.docx"
    act_template, act_template_fields = read_template(act_template_path)

    #Проверка пустых полей шаблона и наличия реквизитов для их заполнения
    missing_contract_fields = template_fields - contract_fields.keys()
    missing_act_fields = act_template_fields - act_fields.keys()

    missing_fields = missing_contract_fields | missing_act_fields

    if missing_fields:
        raise ValueError("Не подготовлены значения полей шаблона: " + ", ".join(sorted(missing_fields)))

#поиск или создание необходимых папок, файлов и их наименование
    output_folder = folder / "output"
    data_folder = folder / "data"
    client_name = client_data["client_fio"]
    service_title = service_short_names[service]
    output_name = f"Договор_{service_title}_{client_name}.docx"

    for symbol in '<>:"/\\|?*':
        output_name = output_name.replace(symbol, "_")

    output_path = output_folder / output_name
    act_name = output_name.replace("Договор_", "Акт_", 1)
    act_path = output_folder / act_name
    data_path = data_folder / (output_path.stem + ".json")

    if output_path.exists() or act_path.exists() or data_path.exists():
        print("Договор, акт или данные заказа с таким именем уже существуют. Файлы не перезаписаны.")
        return

#заполнение пустых полей шаблона данными
    template.render(contract_fields, autoescape=True)
    act_template.render(act_fields, autoescape=True)
    output_folder.mkdir(exist_ok=True)
    data_folder.mkdir(exist_ok=True)
    order = {"service": service, "contract_fields": contract_fields, "act_fields": act_fields}


    #по очереди сохраняется договор, акт и JSON-файл с данными заказа, избегая неполного комплекта
    created_paths = []
    try:
        with output_path.open("xb") as file:
            created_paths.append(output_path)
            template.save(file)
        with act_path.open("xb") as file:
            created_paths.append(act_path)
            act_template.save(file)
        with data_path.open("x", encoding="utf-8") as file:
            created_paths.append(data_path)
            json.dump(order, file, ensure_ascii=False, indent=4)
    
   #При ошибке удаляются созданные данным запуском файлы 
    except OSError:
        for path in created_paths:
            try:
                path.unlink()
            except OSError as error:
                print("Не удалось удалить неполный файл:", path, error)
        raise

    print("Данные договора и акта сохранены:", data_path)
    print("Договор сохранён:", output_path)
    print("Акт сохранён:", act_path)

#функция для запуска основного процесса через функцию main() возвращает объяснения пользователю при наличии ошибок
def run_app():
    try:
        main()
        return 0
    except FileNotFoundError as error:
        print("Не найден необходимый файл или папка:", error)
    except PermissionError as error:
        print("Нет доступа к файлу. Проверьте права и закройте документ в Word:", error)
    except FileExistsError as error:
        print("Файл уже существует и не был перезаписан:", error)
    except UnicodeDecodeError as error:
        print("Сохраните текстовый файл в кодировке UTF-8:", error)
    except ValueError as error:
        print("Ошибка данных:", error)
    except TemplateError as error:
        print("Ошибка в полях шаблона Word. Проверьте фигурные скобки и названия полей:", error)
    except OverflowError:
        print("Не удалось рассчитать дату акта. Укажите дату услуги в поддерживаемом диапазоне.")
    except OSError as error:
        print("Не удалось прочитать или сохранить файл:", error)
    except EOFError:
        print("Ввод не завершён. В примере не хватает ответов на запросы программы.")
    except KeyboardInterrupt:
        print("\nРабота остановлена пользователем.")
    return 1

#запуск всего процесса создания документов из данного файла
if __name__ == "__main__":
    raise SystemExit(run_app())
