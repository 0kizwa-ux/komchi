# Rakuten ROOM Draft Assistant


# 最初にダブルクリックするファイル

変化が分かりやすいように、先頭に `00_` が付いた起動ファイルを追加しています。

一番簡単にするため、短い名前の起動ファイルを追加しました。

迷ったら、まず **`START.bat`** をダブルクリックしてください。Komchi Creator App が起動し、ブラウザから主要機能を選べます。

デスクトップにアイコンを作りたい場合だけ、**`ICONS.bat`** をダブルクリックしてください。

日本語名のファイルが見える環境では、**`ここをダブルクリック_最初に起動.bat`** と **`デスクトップにアイコンを作成.bat`** も同じ用途で使えます。

| やりたいこと | ダブルクリックするファイル |
|---|---|
| まずアプリを開きたい | `START.bat` |
| デスクトップにアイコンを作りたい | `ICONS.bat` |
| 00名でアプリを開きたい | `00_START_HERE.bat` |
| 00名でアイコンを作りたい | `00_CREATE_DESKTOP_ICONS.bat` |
| 日本語名でアプリを開きたい | `ここをダブルクリック_最初に起動.bat` |
| 日本語名でアイコンを作りたい | `デスクトップにアイコンを作成.bat` |
| 統合アプリを直接開きたい | `start_komchi_app.bat` |
| 写真1枚ダンスだけ作りたい | `start_photo_dance_creator.bat` |
| ショート動画ストックだけ作りたい | `start_short_stock_creator.bat` |
| ROOM下書きだけ開きたい | `start_room_draft_assistant.bat` |

もしファイルが見えない場合は、古いフォルダを開いている可能性があります。最新版を取得・展開してから確認してください。


## START.batを押しても変化がない場合

`START_DEBUG.bat` をダブルクリックしてください。現在のフォルダ、`komchi_app.py` の有無、Pythonの有無、Pythonバージョンを表示してから起動します。黒い画面に出たエラーをコピーして送ってください。


## 黒い画面も出ない場合

`START_NO_BLACK_SCREEN.vbs` をダブルクリックしてください。黒い画面を出さずに起動を試し、`START_LOG.txt` をメモ帳で開きます。そこに出た内容を送ってください。

それでも何も起きない場合は、`START_LOG_ONLY.bat` を右クリックして「開く」を選んでください。ログだけを作ってメモ帳で開きます。

楽天市場の商品情報を取得し、楽天ROOMへ手動投稿するための「投稿候補」を作る半自動化ツールです。

このツールは楽天ROOMへのログイン、ブラウザ操作、自動投稿、いいね・フォロー等の自動操作を行いません。投稿前に人間が内容を確認して、楽天ROOM上で手動投稿してください。

## できること

- 楽天市場の商品検索APIから商品候補を取得
- ROOM向け紹介文の下書きを生成
- 薬機法・景表法・誇大表現に寄りやすいNG表現を簡易チェック
- Markdown / CSV で投稿候補リストを書き出し
- APIキーなしで動作確認できるモック出力
- ブラウザでボタンを押すだけの簡単UI

## 必要なもの

### APIキーなし・ボタンUIだけで使う場合

- ブラウザ
- Python 3.10+（`start_room_draft_assistant.py` で起動する場合）

### 楽天商品検索APIで実商品データを取得する場合

- Python 3.10+
- 楽天ウェブサービスのアプリID
  - 環境変数 `RAKUTEN_APP_ID` に設定してください。

楽天商品検索APIは、公式ドキュメント上で `applicationId` を必須パラメータとして受け取り、キーワード・ジャンルID・商品コード・ショップコード等のいずれかを検索条件にできます。2026年5月時点では `https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401` が現行エンドポイントです。

## 使い方

### 0. APIキーなし・ボタンだけで使う

APIキーがない場合は、次のどちらかでボタンUIを開いてください。

#### いちばん簡単な起動方法

- Windows: `start_room_draft_assistant.bat` をダブルクリック
- macOS: `start_room_draft_assistant.command` をダブルクリック
- 共通: ターミナルで `python3 start_room_draft_assistant.py` を実行

起動するとブラウザで `room_draft_button.html` が開きます。

#### 直接開く方法

`room_draft_button.html` をダブルクリックしてブラウザで開くこともできます。コピー機能が動かないブラウザでは、上の起動方法を使ってください。

#### ボタンUIでの操作

1. 商品ジャンルを入力する
2. 「投稿候補を作成」ボタンを押す
3. 表示された「楽天市場で確認」リンクから実商品を確認する
4. コメント案を確認・修正して、楽天ROOMへ手動投稿する
5. 必要なら「コメント案をコピー」または「CSVをダウンロード」を押す

このHTML版は楽天APIを呼び出さないため、実在の商品データではなく投稿文のたたき台を作る用途です。実際に投稿する前に、楽天市場の商品ページで価格・在庫・配送条件を必ず確認してください。

### 1. モックデータで動作確認

```bash
python3 scripts/room_draft_assistant.py --mock --keyword "コーヒー" --limit 3 --output drafts.md --csv drafts.csv
```

### 2. 楽天商品検索APIで候補を作成

```bash
export RAKUTEN_APP_ID="あなたのアプリID"
python3 scripts/room_draft_assistant.py --keyword "母の日 ギフト" --limit 10 --output drafts.md --csv drafts.csv
```

### 3. 楽天アフィリエイトIDを付ける場合

```bash
export RAKUTEN_APP_ID="あなたのアプリID"
export RAKUTEN_AFFILIATE_ID="あなたのアフィリエイトID"
python3 scripts/room_draft_assistant.py --keyword "収納ボックス" --limit 10 --output drafts.md
```

## 出力の見方

Markdownには以下が含まれます。

- 商品名
- 価格
- レビュー平均・レビュー件数
- 商品URL
- ROOM投稿用コメント案
- リスク表現の簡易チェック結果
- 手動確認チェックリスト

CSVはスプレッドシートに取り込み、投稿候補管理に使えます。

## 安全運用ルール

1. 投稿は必ず人間が最終確認して手動で行う。
2. 商品説明やレビューを確認し、実際の内容と違う紹介文にしない。
3. 医薬品・化粧品・健康食品などは効果効能を断定しない。
4. 外部リンクや無許可画像を投稿しない。
5. 同一文面の大量投稿や機械的な連投を避ける。

## 開発者向け

テスト実行:

```bash
python3 -m unittest discover -s tests
```


# ショート動画ストック作成

楽天ROOMではなく、YouTubeショート用の動画ストックを作る場合は `shorts/create_stock_short.py` を使います。

## Windowsで指定フォルダにストックする

`start_short_stock_creator.bat` をダブルクリックすると、テーマ入力後に以下へ保存します。

```text
C:\Users\osk_k\Desktop\ユーチューブショート動画ストック
```

## コマンドで作成する

```bash
python3 shorts/create_stock_short.py --theme "朝の時短テク3選" --output-dir "C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
```


## ベイビーダンス動画テンプレートで作成する

TikTokなどで見かけるベイビーダンス系の構成を、オリジナル動画用の台本として作る場合は `--template baby_dance` を使います。既存動画の丸コピーではなく、赤ちゃんの表情・手足の動き・保存CTAを入れた量産用テンプレートです。

```bash
python3 shorts/create_stock_short.py --theme "ベイビーダンス" --template baby_dance --output-dir "C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
```

作成されるもの:

- `short_video.mp4`（ffmpegがある場合）
- `title.txt`
- `description.txt`
- `script.txt`
- `metadata.json`

ffmpegがない環境では、MP4は作らず、台本・タイトル・説明文・メタデータだけ保存します。投稿はYouTube Studioで手動、または別途公式API/OAuth連携で行ってください。


# 写真1枚からダンス風ショートを作る

肖像画像1枚を使って、上下バウンス・ズーム・左右スウェイで「簡単に踊っているように見える」ショート動画ストックを作る場合は `shorts/create_photo_dance.py` を使います。

## Windowsで作る

`start_photo_dance_creator.bat` をダブルクリックし、画像パスとテーマを入力してください。保存先は以下です。

```text
C:\Users\osk_k\Desktop\ユーチューブショート動画ストック
```

## コマンドで作成する

```bash
python3 shorts/create_photo_dance.py --image "portrait.jpg" --theme "ベイビーダンス" --output-dir "C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
```

作成されるもの:

- `photo_dance.mp4`（ffmpegがある場合）
- `title.txt`
- `description.txt`
- `storyboard.txt`
- `metadata.json`



## 好きなBGMを指定する

写真1枚ダンス風ショートでは、`--bgm` で好きな音楽ファイルを指定できます。`--bgm-volume` で音量も調整できます。

```bash
python3 shorts/create_photo_dance.py --image "portrait.jpg" --theme "ベイビーダンス" --bgm "music.mp3" --bgm-volume 0.7 --output-dir "C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
```

BGMを指定しない場合は、従来どおり簡易ビート音を使います。BGMに合わせて上下バウンス・ズーム・左右スウェイを付けますが、現時点ではBPM自動解析ではなく周期的な同期風モーションです。

注意: これは写真1枚に動きを付ける簡易アニメーションです。手足や表情を本当に別ポーズへ変化させるAI生成動画ではありません。実在人物・子どもの肖像を使う場合は、本人または保護者の許可を得てください。


# デスクトップアプリ化・アイコン作成

Windowsで使いやすくするため、ローカルブラウザで開く統合アプリ `komchi_app.py` と、デスクトップショートカット作成スクリプトを用意しています。

## 統合アプリを起動する

```bash
python3 komchi_app.py
```

または Windows で `start_komchi_app.bat` をダブルクリックしてください。ブラウザで Komchi Creator App が開き、以下をまとめて操作できます。

- ROOM下書きUIを開く
- ショート動画ストックを作る
- 写真1枚ダンス風ショートを作る

## デスクトップにアイコンを作る

Windowsで `install_desktop_shortcuts.bat` をダブルクリックすると、デスクトップに以下のショートカットを作成します。

- Komchi Creator App
- Komchi ROOM Draft
- Komchi Photo Dance
- Komchi Short Stock

ショートカットはこのフォルダ内の `.bat` 起動ファイルを指します。フォルダを移動した場合は、もう一度 `install_desktop_shortcuts.bat` を実行してください。


# 参考動画から編集プロジェクトを作る

参考動画リンクを貼り付けて、同じ雰囲気・構成のオリジナル動画を作るための編集プロジェクトを作成できます。著作権や肖像権の問題を避けるため、参考動画そのものをコピー・転載するのではなく、人物・背景・BGM・テロップを自分の素材へ差し替える前提です。

```bash
python3 shorts/create_reference_project.py --reference-url "https://www.tiktok.com/@bkkth/video/7622581244072561936" --theme "ベイビーダンス参考" --notes "ベイビーダンス、明るいBGM、短い白字幕" --replace "人物A=C:\Users\osk_k\Desktop\portrait.jpg" --output-dir "C:\Users\osk_k\Desktop\ユーチューブショート動画ストック"
```

作成されるもの:

- `reference_url.txt`
- `storyboard_template.txt`
- `asset_replacements.csv`
- `rights_checklist.txt`
- `metadata.json`

`asset_replacements.csv` に、人物同士の入れ替え、BGM差し替え、背景差し替え、テロップ差し替えなどを記録できます。
