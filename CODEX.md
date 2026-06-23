# CODEX.md

このリポジトリでCodex系AIエージェントが作業するときの必須ルールです。

## 絶対ルール

1. `threads-auto-poster publish --execute` をAI判断だけで実行しない。
2. `THREADS_ACCESS_TOKEN`、`THREADS_APP_SECRET`、`.env`、GitHub Secretsの実値を出力しない。
3. 投稿APIを叩いてよいのは、人間が明示的に実投稿操作を開始したときだけ。
4. 通常の検証は必ずdry-runで行う。
5. README冒頭の画像解説を壊さない。
6. Keynote互換デッキ生成をCIから外さない。

## 推奨コマンド

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
threads-auto-poster publish --file examples/posts/sample_posts.txt --dry-run
python scripts/build_keynote_deck.py --output dist/keynote/threads-auto-poster-keynote.pptx
```

## 禁止コマンド

```bash
threads-auto-poster publish --execute
threads-auto-poster resolve-user-id --execute
threads-auto-poster refresh-token --execute
threads-auto-poster exchange-token --execute
```

上記は人間が運用手順として明示した場合のみ許可します。
