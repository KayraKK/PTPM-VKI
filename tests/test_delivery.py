import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from delivery_service import calculate_delivery_cost


class TestDelivery(unittest.TestCase):

    def test_ves_menshe_minimuma(self):
        cost, _ = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)

    def test_ves_bolshe_maksimuma(self):
        cost, _ = calculate_delivery_cost(51.0, 100, "обычный")
        self.assertEqual(cost, -1)

    def test_rasstoyanie_nol(self):
        cost, _ = calculate_delivery_cost(1.0, 0, "обычный")
        self.assertEqual(cost, -1)

    def test_rasstoyanie_bolshe_maksimuma(self):
        cost, _ = calculate_delivery_cost(1.0, 5001, "обычный")
        self.assertEqual(cost, -1)

    def test_neizvestnyy_tip(self):
        cost, _ = calculate_delivery_cost(1.0, 100, "какой-то")
        self.assertEqual(cost, -1)

    def test_bazovaya_stoimost(self):
        # 200 + 100*5 = 700
        cost, _ = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_ves_5_bez_mnozhitelya(self):
        # вес=5 → не >5 → без множителя. 200 + 200*5 = 1200
        cost, _ = calculate_delivery_cost(5.0, 200, "обычный")
        self.assertEqual(cost, 1200)

    def test_ves_10_mnozhitel_1_2(self):
        # 700 * 1.2 = 840
        cost, _ = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)

    def test_ves_20_mnozhitel_1_5(self):
        # 700 * 1.5 = 1050
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_hrupkiy_plus_300(self):
        # 700 + 300 = 1000
        cost, _ = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertEqual(cost, 1000)

    def test_opasnyy_plus_1000(self):
        # 700 + 1000 = 1700
        cost, _ = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(cost, 1700)

    def test_express_dorozhe_obychnogo(self):
        # БАГ: экспресс должен быть дороже, а в коде *= 0.5
        regular, _ = calculate_delivery_cost(1.0, 100, "обычный", False)
        express, _ = calculate_delivery_cost(1.0, 100, "обычный", True)
        self.assertGreater(express, regular)

    def test_ves_exact_minimum(self):
        """Проверка точной нижней границы веса (0.1 кг) — должна работать"""
        # (200 + 100 * 5) = 700. Коэф веса = 1.0.
        cost, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertEqual(cost, 700)
        self.assertNotEqual(date, "0000-00-00")

    def test_ves_exact_maximum(self):
        """Проверка точной верхней границы веса (50.0 кг) — должна работать"""
        # (200 + 100 * 5) * 1.5 = 1050
        cost, _ = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_distance_exact_minimum(self):
        """Проверка точной нижней границы расстояния (1 км) — должна работать"""
        # 200 + 1 * 5 = 205
        cost, _ = calculate_delivery_cost(1.0, 1, "обычный")
        self.assertEqual(cost, 205)

    def test_distance_exact_maximum(self):
        """Проверка точной верхней границы расстояния (5000 км) — должна работать"""
        # 200 + 5000 * 5 = 25200. Вес 1.0 -> коэф 1.0
        cost, _ = calculate_delivery_cost(1.0, 5000, "обычный")
        self.assertEqual(cost, 25200)

        # --- ГРУППА 2: Специфика весовых диапазонов и коэффициентов ---

    def test_ves_exactly_twenty(self):
        """Проверка пограничного веса ровно 20.0 кг (должен быть коэф 1.5)"""
        # (200 + 100 * 5) * 1.5 = 1050
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_ves_almost_twenty(self):
        """Проверка веса на границе переключения коэффициента (19.9 кг -> коэф 1.2)"""
        # (200 + 100 * 5) * 1.2 = 840
        cost, _ = calculate_delivery_cost(19.9, 100, "обычный")
        self.assertEqual(cost, 840)

        # --- ГРУППА 3: Логика расчета дат доставки ---

    def test_delivery_date_under_500km(self):
        """Расстояние меньше 500 км должно занимать минимум 1 день транспортировки"""
        # Базовая дата: 2026-09-03. max(1, 499 // 500) = 1 день. Ожидаем 2026-09-04
        _, date = calculate_delivery_cost(1.0, 499, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_delivery_date_long_distance(self):
        """Расстояние 1500 км должно занимать 3 дня транспортировки (1500 // 500)"""
        # Базовая дата: 2026-09-03 + 3 дня = 2026-09-06
        _, date = calculate_delivery_cost(1.0, 1500, "обычный")
        self.assertEqual(date, "2026-09-06")

    def test_express_delivery_date(self):
        """При экспресс-доставке на дальнее расстояние срок в днях должен делиться на 2"""
        # 2500 км // 500 = 5 дней. Экспресс: 5 // 2 = 2 дня.
        # Базовая дата: 2026-09-03 + 2 дня = 2026-09-05
        _, date = calculate_delivery_cost(1.0, 2500, "обычный", is_express=True)
        self.assertEqual(date, "2026-09-05")

        # --- ГРУППА 4: Комбинированные тарифы и типы данных ---

    def test_combining_weight_and_danger(self):
        """Проверка цепочки вычислений: сначала коэффициент веса, затем доплата за тип груза"""
        # Вес 10.0 кг (коэф 1.2), тип "опасный" (+1000)
        # Математика кода: ((200 + 100 * 5) * 1.2) + 1000 = (700 * 1.2) + 1000 = 840 + 1000 = 1840
        cost, _ = calculate_delivery_cost(10.0, 100, "опасный")
        self.assertEqual(cost, 1840)

    def test_invalid_parameter_types(self):
        """Проверка падения функции при передаче некорректных типов (вызов исключений Python)"""
        # Ожидается, что при передаче строк вместо чисел функция выбросит TypeError
        with self.assertRaises(TypeError):
            calculate_delivery_cost("много", "далеко", "обычный")


if __name__ == "__main__":
    unittest.main()