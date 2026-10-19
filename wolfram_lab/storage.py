"""Модуль сохранения результатов: сырые ответы, извлечённые данные, текстовый отчёт."""
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def save_raw(output_dir: str, query_id: int, data: dict) -> Path:
    """Полный ответ API -> output/raw/query_01.json"""
    path = Path(output_dir) / "raw" / f"query_{query_id:02d}.json"
    _write_json(path, data)
    log.info("Сырой ответ сохранён: %s", path)
    return path


def save_extracted(output_dir: str, items: list) -> Path:
    """Извлечённые данные всех запросов -> output/extracted.json"""
    path = Path(output_dir) / "extracted.json"
    _write_json(path, items)
    log.info("Извлечённые данные сохранены: %s", path)
    return path


def save_report(output_dir: str, items: list) -> Path:
    """Читаемый отчёт -> output/report.txt"""
    lines = []
    for it in items:
        lines.append("=" * 70)
        lines.append(f"[{it['id']:02d}] {it['category']}")
        lines.append(f"Запрос: {it['query']}")
        if it.get("error"):
            lines.append(f"ОШИБКА: {it['error']}")
        elif not it["success"]:
            hint = f" Возможно, вы имели в виду: {', '.join(it['didyoumeans'])}" if it["didyoumeans"] else ""
            lines.append("Wolfram|Alpha не смог интерпретировать запрос." + hint)
        else:
            lines.append(f"Ключевой ответ ({it['key_pod_title']}):")
            lines.append(it["key_answer"] or "—")
        lines.append("")
    path = Path(output_dir) / "report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Отчёт сохранён: %s", path)
    return path
