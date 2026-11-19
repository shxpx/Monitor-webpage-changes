import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import quote

import requests


# GitLab 配置
GITLAB_BASE_URL = "https://gitlab.com"
PROJECT_PATH = "zhifan999/fq"
WIKI_SLUG = "v2ray免费账号"

# 保存正文哈希的本地文件
SNAPSHOT_FILE = Path("snapshot.txt")

# 项目路径和 Wiki slug 都需要进行 URL 编码
API_URL = (
    f"{GITLAB_BASE_URL}/api/v4/projects/"
    f"{quote(PROJECT_PATH, safe='')}/wikis/"
    f"{quote(WIKI_SLUG, safe='')}"
)


def fetch_web_content():
    """通过 GitLab API 获取 Wiki 原始正文。"""
    headers = {
        "User-Agent": "GitLab-Wiki-Monitor/1.0",
        "Accept": "application/json",
    }

    # 如接口需要身份验证，可设置此环境变量
    token = os.environ.get("GITLAB_TOKEN", "").strip()
    if token:
        headers["PRIVATE-TOKEN"] = token

    try:
        response = requests.get(
            API_URL,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("content")

        if not isinstance(content, str) or not content.strip():
            print("抓取失败：API 未返回有效的 Wiki 正文。")
            return None

        # 统一换行符，避免仅换行格式不同造成误报
        return content.replace("\r\n", "\n").replace("\r", "\n")

    except requests.RequestException as exc:
        # 不打印请求详情，避免意外泄露认证信息
        print(f"抓取 Wiki 失败：{type(exc).__name__}")
        if exc.response is not None:
            print(f"HTTP 状态码：{exc.response.status_code}")
        return None

    except ValueError:
        print("抓取失败：接口返回的内容不是有效 JSON。")
        return None


def trigger_webhook():
    """触发 Webhook；仅 HTTP 2xx 视为成功。"""
    webhook_url = os.environ.get("WEBHOOK_URL", "").strip()

    if not webhook_url:
        print("警告：未检测到 WEBHOOK_URL 环境变量，不更新快照。")
        return False

    try:
        response = requests.get(webhook_url, timeout=15)

        if not 200 <= response.status_code < 300:
            print(f"Webhook 触发失败，状态码：{response.status_code}")
            return False

        print(f"Webhook 触发成功，状态码：{response.status_code}")
        return True

    except requests.RequestException as exc:
        # Webhook URL 可能包含密钥，因此不输出完整异常消息
        print(f"Webhook 请求失败：{type(exc).__name__}")
        return False


def save_snapshot(content_hash):
    """先写临时文件，再替换快照。"""
    temp_file = SNAPSHOT_FILE.with_suffix(".tmp")
    temp_file.write_text(content_hash + "\n", encoding="utf-8")
    temp_file.replace(SNAPSHOT_FILE)


def main():
    current_content = fetch_web_content()
    if current_content is None:
        return 1

    current_hash = hashlib.sha256(
        current_content.encode("utf-8")
    ).hexdigest()

    old_hash = ""
    if SNAPSHOT_FILE.exists():
        old_hash = SNAPSHOT_FILE.read_text(
            encoding="utf-8"
        ).strip()

    if current_hash == old_hash:
        print("Wiki 正文无变化。")
        return 0

    if old_hash:
        print("检测到 Wiki 正文发生变化，正在触发 Webhook...")
    else:
        print("未找到历史快照，首次运行，正在触发 Webhook...")

    if not trigger_webhook():
        print("保留原快照，下次运行将继续尝试通知。")
        return 1

    save_snapshot(current_hash)
    print("本地快照已更新。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
