import math
import logging

# Настройка логирования из Кода 2
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

EPS = 1e-9

def triangle(a, b, c):
    # Проверка на существование треугольника (с учетом EPS из Кода 2)
    if a <= 0 or b <= 0 or c <= 0:
        logging.warning("Результат: не треугольник (стороны должны быть больше 0)")
        return "не треугольник", [(-1, -1)] * 3

    if (a + b <= c + EPS) or (a + c <= b + EPS) or (b + c <= a + EPS):
        logging.warning("Результат: не треугольник (нарушено неравенство треугольника)")
        return "не треугольник", [(-1, -1)] * 3

    # Определение типа треугольника
    if a == b == c:
        t = "равносторонний"
    elif a == b or a == c or b == c:
        t = "равнобедренный"
    else:
        t = "разносторонний"

    logging.info(f"Результат: {t}")

    cx = (a * a + b * b - c * c) / (2 * a)
    cy = math.sqrt(max(0.0, b * b - cx * cx))
    xs, ys = [0, a, cx], [0, 0, cy]

    w, h = max(xs) - min(xs), max(ys) - min(ys)
    s = 80 / max(w, h)
    ox, oy = (100 - w * s) / 2, (100 - h * s) / 2

    coords = [
        (int((x - min(xs)) * s + ox), int((y - min(ys)) * s + oy))
        for x, y in zip(xs, ys)
    ]

    logging.info(f"координаты: {coords}")
    return t, coords


def parse_and_solve(a_str, b_str, c_str):
    try:
        a, b, c = float(a_str), float(b_str), float(c_str)
        logging.info(f"стороны: a={a}, b={b}, c={c}")
        return triangle(a, b, c)
    except Exception as e:
        logging.error(f"Ошибка ввода: Некорректные символы. {str(e)}")
        return "", [(-2, -2)] * 3


if __name__ == "__main__":
    while True:
        logging.info("Новая проверка")

        try:
            raw_a = input("a: ")
            raw_b = input("b: ")
            raw_c = input("c: ")
        except (KeyboardInterrupt, EOFError):
            logging.info("Программа завершена пользователем.")
            break

        res_type, res_coords = parse_and_solve(raw_a, raw_b, raw_c)
        print(res_coords)
