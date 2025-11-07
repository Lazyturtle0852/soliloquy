import json

# ファイルパスを指定
file_path = "/Users/ryoma/Desktop/soliloqui/twitter-2025-11-02-f23c655845f747d5f2dbc0216a4996c72b5d948a9af8bdb87dd2b39f9ae3edb1/data/tweets.js"
output_file_path = "/Users/ryoma/Desktop/soliloqui/tweet_texts.txt"


# ファイルを読み込む
def extract_full_texts(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        # JavaScriptのJSON形式をPythonで扱えるように整形
        content = file.read().replace("window.YTD.tweets.part0 = ", "")
        tweets_data = json.loads(content)

    # ツイートのテキストを抽出
    full_texts = []
    for tweet in tweets_data:
        if "tweet" in tweet and "full_text" in tweet["tweet"]:
            full_texts.append(tweet["tweet"]["full_text"])

    return full_texts


# 抽出したテキストをファイルに保存
def save_full_texts_to_file(full_texts, output_file_path):
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(", ".join(full_texts))


# メイン処理
if __name__ == "__main__":
    full_texts = extract_full_texts(file_path)
    save_full_texts_to_file(full_texts, output_file_path)
    print(f"ツイートのテキストを {output_file_path} に保存しました。")
