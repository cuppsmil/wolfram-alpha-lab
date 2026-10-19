"""Модуль запросов: HTTP-клиент Wolfram|Alpha Full Results API с обработкой ошибок."""
import logging
import time

import requests

log = logging.getLogger(__name__)

RETRY_STATUSES = {429, 500, 502, 503, 504}


class WolframAPIError(Exception):
    """Ошибка сети или API Wolfram|Alpha."""


class WolframClient:
    def __init__(self, app_id, base_url, timeout=20.0, retries=3, backoff=2.0, session=None):
        self.app_id = app_id
        self.base_url = base_url
        self.timeout = timeout
        self.retries = max(1, retries)
        self.backoff = backoff
        self.session = session or requests.Session()

    def query(self, text: str) -> dict:
        """Отправляет запрос и возвращает полный JSON-ответ (dict)."""
        params = {
            "input": text,
            "appid": self.app_id,
            "output": "json",
            "format": "plaintext",
        }
        last_error = None
        for attempt in range(1, self.retries + 1):
            log.info("Запрос %r (попытка %d/%d)", text, attempt, self.retries)
            try:
                resp = self.session.get(self.base_url, params=params, timeout=self.timeout)
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_error = f"сетевая ошибка: {exc}"
                log.warning("%s", last_error)
            except requests.RequestException as exc:
                raise WolframAPIError(f"ошибка запроса: {exc}") from exc
            else:
                if resp.status_code in (401, 403):
                    raise WolframAPIError(
                        f"HTTP {resp.status_code}: AppID недействителен или доступ запрещён"
                    )
                if resp.status_code in RETRY_STATUSES:
                    last_error = f"HTTP {resp.status_code}"
                    log.warning("Временная ошибка сервера: %s", last_error)
                elif resp.status_code != 200:
                    raise WolframAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                else:
                    return self._check_payload(resp)

            if attempt < self.retries:
                pause = self.backoff * attempt
                log.info("Повтор через %.1f c", pause)
                time.sleep(pause)

        raise WolframAPIError(f"запрос не удался после {self.retries} попыток: {last_error}")

    @staticmethod
    def _check_payload(resp) -> dict:
        try:
            data = resp.json()
        except ValueError as exc:
            raise WolframAPIError("ответ не является корректным JSON") from exc

        qr = data.get("queryresult")
        if qr is None:
            raise WolframAPIError("в ответе нет поля 'queryresult'")

        err = qr.get("error")
        if err and err != "false":  # API возвращает false или объект {code, msg}
            msg = err.get("msg") if isinstance(err, dict) else str(err)
            code = err.get("code") if isinstance(err, dict) else "?"
            raise WolframAPIError(f"ошибка API (код {code}): {msg}")
        return data
