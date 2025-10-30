import os
import subprocess
import sys
from datetime import datetime
from git import Repo, GitCommandError

# --- Configuration ---
# このスクリプトがリポジトリのルートにあることを前提としています
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
GENERATOR_SCRIPT = "soliloquy_app.py"
TARGET_FILE = "index.html"
REMOTE_NAME = "origin"
# ご自身のデフォルトブランチ名に合わせて変更してください (例: "master")
BRANCH_NAME = "main"

def run_generator():
    """コンテンツ生成スクリプトを実行します。"""
    generator_path = os.path.join(REPO_PATH, GENERATOR_SCRIPT)
    print(f"実行中: {generator_path}")
    try:
        # このスクリプトを実行しているPythonインタプリタと同じものを利用します
        process = subprocess.run(
            [sys.executable, generator_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_PATH,
            encoding='utf-8'
        )
        print(process.stdout)
        if process.stderr:
            print("スクリプト実行時にエラーが出力されました:", file=sys.stderr)
            print(process.stderr, file=sys.stderr)
    except FileNotFoundError:
        print(f"エラー: {GENERATOR_SCRIPT} が見つかりません。", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"スクリプトの実行中にエラーが発生しました:", file=sys.stderr)
        print(e.stdout, file=sys.stdout)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

def main():
    """コンテンツを更新し、コミット、プッシュを実行します。"""
    # 1. コンテンツ生成スクリプトを実行
    run_generator()

    try:
        # 2. Gitリポジトリを初期化
        repo = Repo(REPO_PATH)

        # デフォルトブランチにいるか確認
        if repo.active_branch.name != BRANCH_NAME:
            print(f"警告: 現在のブランチは '{repo.active_branch.name}' です。'{BRANCH_NAME}' ブランチに切り替えてください。", file=sys.stderr)
            # ここで処理を中断したい場合は sys.exit(1) をコール
    
        # 3. 対象ファイルをステージング
        print(f"ステージング中: {TARGET_FILE}")
        repo.index.add([TARGET_FILE])

        # 4. コミットすべき変更があるか確認
        if not repo.index.diff("HEAD"):
             print("コミットする変更がありません。")
             return

        # 5. 変更をコミット
        commit_message = f"📝 AI Log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"コミット中: '{commit_message}'")
        repo.index.commit(commit_message)

        # 6. リモートにプッシュ
        print(f"プッシュ中: {REMOTE_NAME} / {repo.active_branch.name}")
        origin = repo.remote(name=REMOTE_NAME)
        origin.push()

        print("\n✅ 独り言の更新とプッシュが完了しました。")

    except GitCommandError as e:
        print(f"\n❌ Git操作中にエラーが発生しました: {e}", file=sys.stderr)
        print("リポジトリの設定、ネットワーク接続、認証情報が正しいか確認してください。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期せぬエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()