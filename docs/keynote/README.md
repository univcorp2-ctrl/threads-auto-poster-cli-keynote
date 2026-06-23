# Keynote Deck

生成物はリポジトリにはコミットせず、CI artifactまたはローカル `dist/keynote/` に作ります。

```bash
python scripts/build_keynote_deck.py --output dist/keynote/threads-auto-poster-keynote.pptx
```

内容:

1. Cover
2. Architecture
3. Posting process
4. Program map
5. Safety model
6. GitHub Actions
7. Secrets setup
8. Operations checklist

Apple Keynoteで `.pptx` を開き、必要に応じて `.key` として保存してください。
