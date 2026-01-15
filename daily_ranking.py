import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import os

def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"
    # GitHubのSettings > Secretsに保存した値を使います
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    
    if not token or not user_id:
        print("LINE設定が足りません")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, headers=headers, json=data)
    print(res.status_code, res.text)

# 設定
url = "https://www.clubdam.com/ranking/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 実行時の日付を取得（ファイル名に使用：例 20260115_dam_ranking.csv）
today_str = datetime.now().strftime("%Y%m%d")

# 'data' というフォルダに保存する場合（あらかじめリポジトリにフォルダを作っておく）
os.makedirs("data", exist_ok=True)
filename = f"data/{today_str}_dam_ranking.csv"

try:
    #print(f"アクセス中: {url}")
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")

    # 1. ランキングの親要素を取得
    ranking_container = soup.find(id="daily-ranking")

    if ranking_container:
        # 2. 各行（li要素）を取得
        items = ranking_container.select("li.p-ranking-list__item")

        # CSVファイルを作成して書き込む
        with open(filename, "w", newline="", encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            # ヘッダー（項目名）を書き込む
            writer.writerow(["順位", "曲名", "アーティスト"])

            for item in items[:100]:
                rank = item.select_one(".p-ranking__num").get_text(strip=True) if item.select_one(".p-ranking__num") else "-"
                title = item.select_one(".p-song__title").get_text(strip=True) if item.select_one(".p-song__title") else "不明"
                artist = item.select_one(".p-song__artist").get_text(strip=True) if item.select_one(".p-song__artist") else "不明"
                
                # 1行ずつCSVに書き出し
                writer.writerow([rank, title, artist])
        
        print(f"CSVファイル『{filename}』に100位まで保存しました。")

        # --- LINE通知の作成 ---
        if items:
            # 配列の最初(0番目)が1位のデータ
            top_title = items[0].select_one(".p-song__title").get_text(strip=True)
            top_artist = items[0].select_one(".p-song__artist").get_text(strip=True)
            
            # メッセージを組み立てる（\n は改行です）
            msg = f"\n【DAMデイリーランキング】\n本日の第1位は…\n\n『{top_title}』\n（{top_artist}）\n\nです！"
            send_line_message(msg)

    else:
        print("指定されたID（daily-ranking）が見つかりませんでした。")

    # サーバー保護のための待機
    time.sleep(3)

except Exception as e:

    print(f"エラーが発生しました: {e}")
