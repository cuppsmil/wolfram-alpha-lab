# Интеграция Wolfram|Alpha через API (Python)

Учебная программа: подключается к [Wolfram|Alpha Full Results API](https://products.wolframalpha.com/api/documentation),
последовательно выполняет **15 запросов** (10 обязательных + 5 дополнительных), разбирает JSON-ответы
и сохраняет результаты в файлы.

## Структура проекта

```
main.py                  # точка входа (оркестрация, логирование)
wolfram_lab/
  config.py              # конфигурация: чтение AppID и параметров из config.ini / env
  queries.py             # список из 15 запросов
  client.py              # HTTP-клиент: таймауты, повторы, обработка ошибок сети и API
  parser.py              # извлечение ключевых данных из JSON
  storage.py             # сохранение сырых ответов, извлечённых данных и отчёта
tests/test_lab.py        # тесты (без сети)
config.ini.example       # шаблон конфигурации
```

## Запросы

| № | Категория | Запрос |
|---|-----------|--------|
| 1 | Математика | `integrate x^2 sin^3 x dx` |
| 2 | Факты | `population of Russia 2024` |
| 3 | Химия | `molar mass of H2SO4` |
| 4 | Физика | `kinetic energy of 5kg object at 10m/s` |
| 5 | География | `distance between Moscow and Saint Petersburg` |
| 6 | Финансы | `100 USD to RUB` |
| 7 | Время | `current time in Kazan` |
| 8 | Астрономия | `distance to Mars` |
| 9 | Медицина | `body mass index 180cm 75kg` |
| 10 | Лингвистика | `translate hello to Russian` |
| 11 | Алгебра | `solve x^2 - 5x + 6 = 0` |
| 12 | Мат. анализ | `derivative of sin(x) * e^x` |
| 13 | Экономика | `GDP of Germany` |
| 14 | Единицы измерения | `speed of light in km/h` |
| 15 | Даты | `days until January 1 2027` |

## Получение AppID

1. Зарегистрируйтесь на <https://account.wolfram.com/wolframid>.
2. Откройте <https://developer.wolframalpha.com/portal/myapps/> → **Get an AppID**
   (Application name — любое, тип — Full Results API).
3. Скопируйте AppID. Бесплатно доступно 2000 запросов в месяц.

## Запуск

```bash
git clone <URL-вашего-репозитория>
cd wolfram-alpha-lab
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp config.ini.example config.ini # Windows: copy config.ini.example config.ini
# впишите свой AppID в config.ini (или задайте переменную окружения WOLFRAM_APP_ID)

python main.py                   # все 15 запросов
python main.py --only 1 3 6      # только выбранные
python -m unittest discover -s tests -t . -v   # тесты
```

> `config.ini` добавлен в `.gitignore` — **AppID нельзя публиковать на GitHub.**

## Результаты

| Файл | Содержимое |
|------|-----------|
| `output/raw/query_NN.json` | полный JSON-ответ API по каждому запросу |
| `output/extracted.json` | извлечённые данные: ключевой ответ, список подов, статус |
| `output/report.txt` | читаемый отчёт |
| `logs/app.log` | лог выполнения |

## Как работает обработка ошибок

- таймаут / обрыв соединения / HTTP 429, 5xx → повтор с нарастающей паузой (`retries`, `backoff`);
- HTTP 401/403 или ошибка в поле `queryresult.error` → понятное сообщение, без повторов;
- запрос не распознан (`success: false`) → в отчёт попадают подсказки `didyoumeans`;
- сбой одного запроса не останавливает остальные; код возврата `1`, если были ошибки.


