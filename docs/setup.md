# Setup Guide

## 0. 安全方針

AIエージェントがThreads APIを勝手に叩かないよう、初期状態ではすべてdry-runです。実投稿は、人間が明示的に `--execute` またはGitHub Actionsの実投稿確認を行ったときだけです。

## 1. Meta Developers側で必要なもの

1. Meta DevelopersでThreads API use caseを持つアプリを用意します。
2. 投稿に必要な権限を設定します。
   - `threads_basic`
   - `threads_content_publish`
3. 投稿対象アカウントでThreads User Access Tokenを取得します。
4. 可能ならThreads user idも控えます。わからない場合は、このCLIの `resolve-user-id --execute` で取得できます。

## 2. GitHub Secrets

GitHub repositoryの `Settings → Secrets and variables → Actions → New repository secret` に以下を入れます。

| Name | Value |
|---|---|
| `THREADS_ACCESS_TOKEN` | Threads User Access Token |
| `THREADS_USER_ID` | Threads user id。任意だが推奨 |
| `THREADS_APP_ID` | Threads app id |
| `THREADS_APP_SECRET` | Threads app secret |
| `THREADS_DRY_RUN` | 通常は `true` |

実値はREADME、issue、PR、ログに貼らないでください。

## 3. ローカル開発

```bash
python -m pip install -e ".[dev]"
cp .env.example .env
```

`.env` に実値を入れる場合も、`.env`は`.gitignore`されています。

動作確認:

```bash
threads-auto-poster validate-env
threads-auto-poster publish --file examples/posts/sample_posts.txt --dry-run
pytest
ruff check .
```

## 4. user idの取得

APIを叩く操作なので、AIエージェントには実行させないでください。人間が明示的に行います。

```bash
threads-auto-poster resolve-user-id --execute
```

## 5. 実投稿

ローカル実投稿:

```bash
threads-auto-poster publish --text "投稿本文" --execute
```

GitHub Actions実投稿は、`.github/workflows` 登録後に `Threads Publish` workflowから実行します。標準はdry-runです。

## 6. Keynote互換デッキ

```bash
python scripts/build_keynote_deck.py --output dist/keynote/threads-auto-poster-keynote.pptx
```

Apple KeynoteでこのPPTXを開けます。
