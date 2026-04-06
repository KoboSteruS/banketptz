"""
Отправка уведомлений о заявках через VK API (messages.send).

Токен и список получателей задаются в переменных окружения.
"""
from __future__ import annotations

import json
import random
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from loguru import logger

VK_API_METHOD_URL = "https://api.vk.com/method/messages.send"
VK_API_VERSION = "5.199"
MAX_MESSAGE_LEN = 4096


def send_booking_to_vk(
    access_token: str,
    peer_ids: list[int],
    message: str,
) -> tuple[bool, list[str]]:
    """
    Отправляет одно и то же сообщение каждому peer_id.

    Returns:
        (успех_хотя_бы_одного, список_ошибок_по_каждому_peer)
    """
    if not access_token.strip():
        return False, ["VK_ACCESS_TOKEN не задан"]
    if not peer_ids:
        return False, ["VK_NOTIFY_USER_IDS пуст"]
    text = message.strip()[:MAX_MESSAGE_LEN]
    errors: list[str] = []
    any_ok = False
    for peer_id in peer_ids:
        err = _messages_send_one(access_token, peer_id, text)
        if err is None:
            any_ok = True
        else:
            errors.append(f"peer {peer_id}: {err}")
            logger.warning("VK messages.send не удалось: {}", err)
    return any_ok, errors


def _messages_send_one(access_token: str, peer_id: int, message: str) -> str | None:
    params: dict[str, Any] = {
        "access_token": access_token,
        "v": VK_API_VERSION,
        "peer_id": peer_id,
        "message": message,
        "random_id": random.randint(1, 2_147_483_647),
    }
    body = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        VK_API_METHOD_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return str(e.reason or e)
    except OSError as e:
        return str(e)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f"некорректный JSON: {raw[:200]}"

    if "error" in data:
        err = data["error"]
        code = err.get("error_code", "?")
        msg = err.get("error_msg", str(err))
        return f"VK error {code}: {msg}"
    if "response" not in data:
        return f"неожиданный ответ: {raw[:200]}"
    return None


def parse_peer_ids(raw: str) -> list[int]:
    """Строка вида «1,2,3» -> список int."""
    out: list[int] = []
    for part in (raw or "").replace(";", ",").split(","):
        p = part.strip()
        if not p:
            continue
        try:
            out.append(int(p))
        except ValueError:
            logger.warning("Пропуск неверного VK id: {}", p)
    return out
