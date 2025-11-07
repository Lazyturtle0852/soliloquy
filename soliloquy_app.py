import requests
from datetime import datetime
import os
from bs4 import BeautifulSoup
import random
import time

# --- LLM API Configuration ---
API_URL = "http://127.0.0.1:1234/v1/chat/completions"

MODEL_ID = "openai/gpt-oss-20b"
MAX_TOKENS = 3000
TEMPERATURE = 0.8

HTML_FILE = "index.html"
MAX_ENTRIES = 50  # ページに表示する独り言の最大数
TWEET_TEXTS_FILE = "tweet_texts.txt"


def get_random_tweets(file_path: str, count: int = 3) -> list:
    """Get a specified number of random tweets from the file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tweets = f.read().split(", ")
        return random.sample(tweets, min(count, len(tweets)))
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりません。")
        return []


def get_thought(tweets: list) -> str:
    three_tweets = chr(10).join(f"- {tweet}" for tweet in tweets)

    """Generates a new thought based on random tweets."""
    prompt = f"""
    あなたは、とある人間の、オンライン上の分身です。
    あなたは、最近以下のようなことを思っています。
    ---
    {three_tweets}
    ---
    これらをフュージョンして、思考を生成してください。
    口調やスタイルもできるだけ似せてください。
    必ず日本語で応答してください。
    なお、アカウント名などは含めないでください。
    """
    print(prompt)
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=360)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        return f"ツイート生成中にエラーが発生しました: {e}"


def create_initial_html():
    """Creates the initial HTML file if it doesn't exist."""
    content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>たーとるの分身</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #f9f9f9; }
        h1 { font-size: 2em; color: #111; }
        .container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .monologue { border-bottom: 1px solid #eee; padding: 15px 0; }
        .monologue:first-of-type { padding-top: 0; }
        .monologue:last-of-type { border-bottom: none; }
        .timestamp { font-weight: bold; color: #555; font-size: 0.9em; }
        .thought { margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>たーとるの分身</h1>
        <p>ローカルAIが、過去のたーとるのツイートに基づき生成した思考の記録が、ここに自動で追加されていきます。
ツイートを3つランダムに選び、それらを元に新しい思考を生成してます。
並行世界とも言えるのかもね。</p>
        <div id="monologue-list">
            <!-- Thoughts will be injected here -->
        </div>
    </div>
</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main function to generate a thought and update the HTML file."""
    # index.htmlがなければ作成
    if not os.path.exists(HTML_FILE):
        create_initial_html()

    # ランダムなツイートを取得
    random_tweets = get_random_tweets(TWEET_TEXTS_FILE)
    if not random_tweets:
        print("ツイートが取得できませんでした。")
        return

    # 新しいツイートを生成
    new_tweet = get_thought(random_tweets)
    print(f"生成されたツイート: {new_tweet}")

    # 既存の独り言を読み込んで履歴を作成
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    except FileNotFoundError:
        create_initial_html()
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

    monologue_list_div = soup.find(id="monologue-list")
    if not monologue_list_div:
        print(f"エラー: {HTML_FILE}内に#monologue-listが見つかりません。")
        # ファイルが壊れている可能性があるので、再作成を試みる
        create_initial_html()
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        monologue_list_div = soup.find(id="monologue-list")

    # 新しい思考を取得
    new_thought_text = new_tweet  # 1回目の生成結果をそのまま使用
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 新しい思考のためのHTML要素を作成
    new_monologue_div = soup.new_tag("div", **{"class": "monologue"})
    ts_p = soup.new_tag("p", **{"class": "timestamp"})
    ts_p.string = timestamp
    thought_p = soup.new_tag("p", **{"class": "thought"})
    thought_p.string = new_thought_text
    new_monologue_div.append(ts_p)
    new_monologue_div.append(thought_p)

    # 新しい思考をリストの先頭に追加
    monologue_list_div.insert(0, new_monologue_div)

    # 古いエントリーを削除
    all_monologues = monologue_list_div.find_all("div", class_="monologue")
    if len(all_monologues) > MAX_ENTRIES:
        for i in range(MAX_ENTRIES, len(all_monologues)):
            all_monologues[i].decompose()

    # 更新されたHTMLをファイルに書き戻す
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    print(f"新しい思考を {HTML_FILE} に書き出しました。")


if __name__ == "__main__":
    main()
