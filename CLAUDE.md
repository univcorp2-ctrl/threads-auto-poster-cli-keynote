# CLAUDE.md

Claude Code / Cloud Code向けの作業指示です。

## 基本姿勢

このプロジェクトはThreads自動投稿を扱いますが、AIエージェント自身はAPIを叩きません。AIはコード作成、dry-run、テスト、ドキュメント更新、Keynote資料生成までを担当します。

## 実行してよいこと

```bash
make install
make lint
make test
make dry-run
make deck
```

## 実行してはいけないこと

以下は人間の明示操作がない限り禁止です。

```bash
make publish
threads-auto-poster publish --execute
threads-auto-poster resolve-user-id --execute
threads-auto-poster refresh-token --execute
threads-auto-poster exchange-token --execute
```

## Secretsの扱い

- 実値をログ、README、issue、PR本文に書かない。
- `.env`をコミットしない。
- GitHub Secretsの名前だけを書く。
- 実値を確認する必要がある場合も、存在確認だけにする。
