# sources／原始文本

此目錄放**取回來的一手文本**（L0 素材），不是編輯產物。每個檔案的來源、版本與授權寫在檔頭。

## 目前

| 檔案 | 內容 | 來源 |
|---|---|---|
| `jiang-weinong-jingang-jiangyi.md` | 江味農《金剛般若波羅蜜經講義》，全 5 卷＋校勘記＋跋；36.5 萬字、364 節、501 頁碼 | [DILA 江味農居士著作全集數位典藏](https://ryosan.dila.edu.tw/jwn/reader.html?doc=JWN-B-B0023)（底本：CBETA 大藏經補編 No. 23） |

## 怎麼取回來的（可重跑）

reader 是 SPA，內容不是 API，而是**單一 HTML 檔**：

```
https://ryosan.dila.edu.tw/jwn/html/<doc>.html
```

`<doc>` 取自 `search.php?vol_dump=yes` 的 `G_VOLS`。目前全集有 13 部：

- `JWN-B-1` 圓覺經講義附親聞記、`JWN-B-2` 大乘止觀述記、`JWN-B-B0023` 金剛經講義
- `JWN-J-1`–`JWN-J-10` 民國期刊文獻輯錄

## 檔案結構與轉換規則

原始 HTML 的標記（以 class 區分）與 Markdown 的對應：

| 原 HTML | Markdown | 說明 |
|---|---|---|
| `p.text_paragraph.h1` | `# …` | 書名 |
| `p.text_paragraph.juan` | `## …` | 卷（卷一…卷五終） |
| `div.kepan-head[level=1..3]` | `###`–`#####` | 江味農科判；同時構成目錄 |
| `p.text_paragraph.orig` | `> …` | 《金剛經》經文 |
| `p.text_paragraph` | 段落 | 講義正文 |
| `p.text_paragraph.kp` | 段落 | 科判夾行 |
| `span.inline_small_note` | `〔…〕` | 原書夾註（含校勘記） |
| `a.pb[data-page]` | `<!-- p.0239a -->` | 原書頁碼（CBETA B23 頁＋欄）；放在行內或段間 |
| `a.lb`（8024 個） | 略 | 原書行錨點；需要逐行引用時再取回 |

段落內的硬換行已接回（中文不加空格）；`lg`／`lg_l`（偈頌）保留換行。

## 授權

- 網站內容：CC BY-NC-SA 4.0（法鼓文理學院），限非商業使用。
- 底本 CBETA 大藏經補編 No. 23：`Available for non-commercial use when distributed with this header intact.`
- 因此本目錄的檔案**不進公開發布包**；若要用於營利或再散布，須先取得授權並保留表頭。
