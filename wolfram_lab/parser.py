"""Модуль обработки: извлечение ключевых данных из JSON-ответа."""
from typing import Optional

# Идентификаторы «подов», которые чаще всего содержат итоговый ответ
PREFERRED_POD_IDS = ("Result", "Value", "Solution", "IndefiniteIntegral", "Derivative")


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _pod_values(pod: dict) -> list:
    """Непустые plaintext-значения всех подпанелей пода."""
    values = []
    for sub in _as_list(pod.get("subpods")):
        text = (sub.get("plaintext") or "").strip()
        if text:
            values.append(text)
    return values


def _pick_key_pod(pods: list) -> Optional[dict]:
    """Выбирает под с ключевым ответом: primary -> известные id -> первый после Input."""
    for pod in pods:
        if pod.get("primary") and _pod_values(pod):
            return pod
    for pod_id in PREFERRED_POD_IDS:
        for pod in pods:
            if pod.get("id") == pod_id and _pod_values(pod):
                return pod
    for pod in pods:
        if pod.get("id") != "Input" and _pod_values(pod):
            return pod
    return None


def extract(query_id: int, category: str, text: str, data: dict) -> dict:
    """Преобразует сырой ответ в компактную структуру с ключевыми данными."""
    qr = data.get("queryresult", {})
    pods = _as_list(qr.get("pods"))
    key_pod = _pick_key_pod(pods)

    didyoumeans = []
    for item in _as_list(qr.get("didyoumeans")):
        if isinstance(item, dict) and item.get("val"):
            didyoumeans.append(item["val"])

    return {
        "id": query_id,
        "category": category,
        "query": text,
        "success": bool(qr.get("success")),
        "timing_sec": qr.get("timing"),
        "num_pods": len(pods),
        "key_pod_title": key_pod.get("title") if key_pod else None,
        "key_answer": "\n".join(_pod_values(key_pod)) if key_pod else None,
        "pods": [
            {"title": p.get("title"), "id": p.get("id"), "values": _pod_values(p)}
            for p in pods
            if _pod_values(p)
        ],
        "didyoumeans": didyoumeans,
    }
