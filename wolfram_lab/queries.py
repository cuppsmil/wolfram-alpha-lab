"""Список запросов: 10 обязательных + 5 дополнительных."""
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryDef:
    id: int
    category: str
    text: str


QUERIES = [
    # --- 10 обязательных запросов из задания ---
    QueryDef(1, "Математический расчёт", "integrate x^2 sin^3 x dx"),
    QueryDef(2, "Фактологический запрос", "population of Russia 2024"),
    QueryDef(3, "Химический расчёт", "molar mass of H2SO4"),
    QueryDef(4, "Физический расчёт", "kinetic energy of 5kg object at 10m/s"),
    QueryDef(5, "Географический", "distance between Moscow and Saint Petersburg"),
    QueryDef(6, "Финансовый", "100 USD to RUB"),
    QueryDef(7, "Временной", "current time in Kazan"),
    QueryDef(8, "Астрономический", "distance to Mars"),
    QueryDef(9, "Медицинский", "body mass index 180cm 75kg"),
    QueryDef(10, "Лингвистический", "translate hello to Russian"),
    # --- 5 дополнительных запросов (на выбор студента) ---
    QueryDef(11, "Алгебра (уравнение)", "solve x^2 - 5x + 6 = 0"),
    QueryDef(12, "Математический анализ", "derivative of sin(x) * e^x"),
    QueryDef(13, "Экономика", "GDP of Germany"),
    QueryDef(14, "Физика / единицы измерения", "speed of light in km/h"),
    QueryDef(15, "Даты и время", "days until January 1 2027"),
]
