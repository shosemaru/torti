# Torti — 公開サイト

App Store 提出に必要な **プライバシーポリシー / 利用規約 / サポート** の公開ページ。
GitHub Pages で配信する。

| ページ | 用途 |
|---|---|
| `/` | ランディング |
| `/privacy/` | App Store Connect の Privacy Policy URL |
| `/support/` | App Store Connect の Support URL |
| `/terms/` | ペイウォールの Terms of Use リンク（ガイドライン 3.1.2 の必須要素） |

## 更新のしかた

HTML を直接編集しない。`build.py` が生成する。

```bash
python3 site/build.py     # app_glp1/ から実行する
```

**プライバシーポリシーの原本は `../store/metadata/privacy-policy-en-US.md`**。
原本を2つ持つと必ずズレるので、ポリシーの文言はそちらを直してから再生成する。
利用規約・サポート・ランディングの文面は `build.py` 内にある。

生成後は commit して push すれば、GitHub Pages が数十秒で反映する。

## 注意

- リンクはすべて相対パス。リポジトリ名を変えても壊れない。
- アプリ側の `AppConfig.swift` がこのサイトのURLを参照している。
  **URLを変えたらアプリ側も直すこと**（ペイウォールのリンク切れは 3.1.2 でリジェクトされる）。
- 規約の文面は法律の専門家のレビューを受けていない出発点。
  US向けの健康隣接アプリなので、本格的に伸ばす前に一度見てもらうのが望ましい。
