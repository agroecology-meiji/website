# Agroecology Lab website

明治大学農学部 アグロエコロジー研究室の GitHub Pages サイトです。既存の HTML/CSS を保ち、更新頻度の高いニュース・業績・ギャラリーを JSON から生成します。

## 日常の更新

1. `data/news.json`、`data/publications.json`、`data/gallery.json` のいずれかを編集します。
2. VS Code で「ターミナル」→「タスクの実行」→「サイト生成」を実行します。
3. 「プレビュー」を実行し、表示された `http://localhost:8000/website/` を確認します。終了は `Ctrl+C` です。
4. 「公開前チェック」を実行します。
5. 内容を確認後、Git のコミットと GitHub への送信を手動で行います。

「サイト生成」は日英のニュース一覧、トップページ最新3件、業績、ギャラリーを生成します。同時にギャラリー画像を最大1600px・JPEG品質82へ縮小し、EXIF、GPS、XMP、ICC、IPTC、コメント等の付加メタデータを除去します。画像処理は macOS 標準機能だけを使うため、追加パッケージは不要です。

## JSON の編集

- ニュース: `data/news.json` の `items` 先頭に追加します。日付は `YYYY-MM-DD`、項目は新しい順です。
- 業績: `data/publications.json` の該当 `section` に追加します。各区分の小見出しは `kicker`、大見出しは `title` で指定します。`html` では `<i>` と HTTPS の `<a>` だけ使用できます。`"locales": ["ja"]` または `["en"]` で表示言語を限定できます。
- ギャラリー: 元画像を `assets/img/` に置き、`data/gallery.json` の `items` 先頭に追加します。`source` は元画像、`output` は公開用JPEGのファイル名です。`slideshow_count` で先頭から何件をスライドに載せるか指定します。 1件に複数画像を載せる場合は、2枚目以降を `additional_images` に指定します。

元画像は保持され、公開用画像が `assets/img/gallery/` に生成されます。

## 自動生成部分とチェック

HTML の `<!-- AUTO:...:START -->` と `<!-- AUTO:...:END -->` の間は生成時に上書きされるため、直接編集せず JSON を変更してください。範囲外のHTMLと既存CSSは変更されません。

「公開前チェック」はファイルを変更せず、JSONの形式・日付順・重複キー、生成HTMLとの一致、画像サイズとメタデータ除去、ローカルリンク切れ、画像の代替テキストを確認します。

生成・プレビュー・チェックは Git のコミットや `push` を一切実行しません。
