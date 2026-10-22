from datetime import datetime
import hashlib
import os
import requests

# 1. 配置你要监控的目标网页 URL
TARGET_URL = "https://github.com/Alvin9999-newpac/fanqiang/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
# 2. 保存网页内容的本地快照文件名
SNAPSHOT_FILE = "snapshot.txt"


def fetch_web_content():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    response = requests.get(TARGET_URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text
  except Exception as e:
    print(f"抓取网页失败: {e}")
    return None


def main():
  current_content = fetch_web_content()
  if not current_content:
    return

  # 计算当前网页内容的哈希值
  current_hash = hashlib.sha256(current_content.encode("utf-8")).hexdigest()

  # 读取历史快照
  old_hash = ""
  if os.path.exists(SNAPSHOT_FILE):
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
      old_hash = f.read().strip()

  # 对比内容是否有变化
  if current_hash != old_hash:
    print("检测到网页内容发生变化！正在触发 n8n Webhook...")

    # 从环境变量获取  Webhook 地址
    url = os.environ.get("WEBHOOK_URL")
    if url:
      payload = {
          "event": "web_page_changed",
          "url": TARGET_URL,
          "timestamp": datetime.utcnow().isoformat(),
          "old_hash": old_hash,
          "new_hash": current_hash,
      }
      headers = {
          "Content-Type": "application/json",
          "User-Agent": "GitHub-Actions-Monitor/1.0",
      }
      try:
        res = requests.post(url, json=payload, timeout=15)
        print(f" Webhook 触发成功，状态码: {res.status_code}")
      except Exception as e:
        print(f"触发  Webhook 失败: {e}")
    else:
      print("警告: 未检测到 WEBHOOK_URL 环境变量。")

    # 更新本地快照文件
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
      f.write(current_hash)
  else:
    print("网页内容无变化。")


if __name__ == "__main__":
  main()
