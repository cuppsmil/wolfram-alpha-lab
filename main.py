"""Точка входа: последовательно выполняет запросы к Wolfram|Alpha и сохраняет результаты."""
import argparse
import logging
import sys
import time
from pathlib import Path

from wolfram_lab import parser as result_parser
from wolfram_lab import storage
from wolfram_lab.client import WolframAPIError, WolframClient
from wolfram_lab.config import ConfigError, load_config
from wolfram_lab.queries import QUERIES


def setup_logging(log_file: str) -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Лабораторная: Wolfram|Alpha API")
    ap.add_argument("--config", default="config.ini", help="путь к конфигурационному файлу")
    ap.add_argument("--only", type=int, nargs="*", help="выполнить только запросы с этими номерами")
    args = ap.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 2

    setup_logging(cfg.log_file)
    log = logging.getLogger("main")

    client = WolframClient(cfg.app_id, cfg.base_url, cfg.timeout, cfg.retries, cfg.backoff)
    queries = [q for q in QUERIES if not args.only or q.id in args.only]
    log.info("Старт: %d запросов", len(queries))

    results, failed = [], 0
    for i, q in enumerate(queries):
        log.info("--- [%02d] %s: %s", q.id, q.category, q.text)
        try:
            data = client.query(q.text)
            storage.save_raw(cfg.output_dir, q.id, data)
            item = result_parser.extract(q.id, q.category, q.text, data)
            log.info("Ответ: %s", (item["key_answer"] or "нет данных").replace("\n", " | "))
        except WolframAPIError as exc:
            failed += 1
            log.error("Запрос %d не выполнен: %s", q.id, exc)
            item = {"id": q.id, "category": q.category, "query": q.text,
                    "success": False, "error": str(exc), "didyoumeans": []}
        results.append(item)
        if i < len(queries) - 1:
            time.sleep(cfg.delay)  # не превышаем лимиты API

    storage.save_extracted(cfg.output_dir, results)
    storage.save_report(cfg.output_dir, results)
    log.info("Готово. Успешно: %d, с ошибками: %d", len(results) - failed, failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
