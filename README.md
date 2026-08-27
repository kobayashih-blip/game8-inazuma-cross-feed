# Game8 イナイレクロス RSS

Game8の検索結果を15分ごとに確認し、最終更新日時順のRSSをGitHub Pagesで公開します。

公開フィードURL:

https://kobayashih-blip.github.io/game8-inazuma-cross-feed/feed.xml

## 初回設定

1. このフォルダ内の `generate_feed.py`、`.github`、`README.md` をリポジトリ直下へアップロードします。
2. リポジトリの **Settings → Pages** を開きます。
3. **Build and deployment → Source** を **GitHub Actions** に設定します。
4. **Actions** タブで `Update RSS feed` を開き、**Run workflow** を実行します。
5. 処理完了後、上記フィードURLを開いてXMLが表示されることを確認します。

Slackでは対象チャンネルに次を投稿します。

```
/feed subscribe https://kobayashih-blip.github.io/game8-inazuma-cross-feed/feed.xml
```
