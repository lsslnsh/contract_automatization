import subprocess
import sys
from pathlib import Path


example_files = {
    "lsk": "lsk.txt",
    "audit": "audit.txt",
    "support": "support.txt",
    "dirty": "dirty.txt"
}


def run_example(example_name):
    folder = Path(__file__).resolve().parent
    example_path = folder / "input" / "examples" / example_files[example_name]

    try:
        example_data = example_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print("Не найден файл примера:", example_path)
        return 1
    except UnicodeDecodeError:
        print("Сохраните файл примера в кодировке UTF-8:", example_path)
        return 1
    except OSError as error:
        print("Не удалось прочитать файл примера:", error)
        return 1

    print("Запускается пример:", example_path.name, flush=True)

    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(folder / "main.py")],
            input=example_data,
            text=True,
            encoding="utf-8",
            cwd=folder
        )
    except OSError as error:
        print("Не удалось запустить main.py:", error)
        return 1

    if result.returncode != 0:
        print("Программа завершилась с ошибкой. Проверьте сообщение выше.")

    return result.returncode


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in example_files:
        print("Запуск: python run_example.py lsk / audit / support / dirty")
        print("Например: python run_example.py support")
        return 1

    return run_example(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
