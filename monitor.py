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
    # 返回网页的正文或文本内容（也可以根据需要缩小范围提取特定标签）
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
    print("检测到网页内容发生变化！")

    # TODO: 可以在这里添加发送通知的逻辑（例如调用 Server酱、Telegram Bot 或企业微信 Webhook）
    # webhook_url = os.environ.get("WEBHOOK_URL")
    # if webhook_url:
    #     requests.post(webhook_url, json={"text": f"网页 {TARGET_URL} 内容更新啦！"})

    # 更新本地快照文件
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
      f.write(current_hash)
  else:
    print("网页内容无变化。")


if __name__ == "__main__":
  main()
