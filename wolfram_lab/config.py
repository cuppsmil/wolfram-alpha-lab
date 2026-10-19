"""Модуль конфигурации: чтение AppID и параметров из config.ini / переменных окружения."""
import configparser
import logging
import os
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


class ConfigError(Exception):
    """Ошибка чтения конфигурации."""


@dataclass
class Config:
    app_id: str
    base_url: str = "https://api.wolframalpha.com/v2/query"
    timeout: float = 20.0       # таймаут одного HTTP-запроса, сек
    retries: int = 3            # число попыток при сетевых ошибках / 5xx
    backoff: float = 2.0        # базовая пауза между повторами, сек
    delay: float = 1.0          # пауза между разными запросами, сек
    output_dir: str = "output"
    log_file: str = "logs/app.log"


def load_config(path: str = "config.ini") -> Config:
    """Читает config.ini. Переменная окружения WOLFRAM_APP_ID имеет приоритет над файлом."""
    parser = configparser.ConfigParser()
    p = Path(path)
    if p.exists():
        parser.read(p, encoding="utf-8")
        log.info("Конфигурация прочитана из %s", p)
    else:
        log.warning("Файл %s не найден, используем только переменные окружения", p)

    section = parser["wolframalpha"] if parser.has_section("wolframalpha") else {}
    app_id = os.environ.get("WOLFRAM_APP_ID") or section.get("app_id", "")
    app_id = app_id.strip()
    if not app_id or app_id == "YOUR-APP-ID-HERE":
        raise ConfigError(
            "AppID не задан. Скопируйте config.ini.example в config.ini и впишите AppID "
            "или задайте переменную окружения WOLFRAM_APP_ID."
        )

    return Config(
        app_id=app_id,
        base_url=section.get("base_url", Config.base_url),
        timeout=float(section.get("timeout", Config.timeout)),
        retries=int(section.get("retries", Config.retries)),
        backoff=float(section.get("backoff", Config.backoff)),
        delay=float(section.get("delay", Config.delay)),
        output_dir=section.get("output_dir", Config.output_dir),
        log_file=section.get("log_file", Config.log_file),
    )
