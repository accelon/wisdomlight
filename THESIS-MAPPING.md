# 論文 → 資料模型對照

> 對象：李慧萍《意義的生成初探—以江味農《金剛經講義》為例》，2016 年定稿（五章＋八附錄）。
> 依據：`論文第1-5章(李慧萍0915).docx`（2016-09-15）與 `論文附錄(李慧萍0824版).docx`（2016-08-24）。
> 目的：把論文的知識結構逐項對到本專案的 **anchor／span／claim／edge／compilation**，
> 標出「接得住」與「要新增」的地方。
> 論文全文與附錄不在本 repo；本文只引用結構與少量範例。入庫前須先確認授權（見 §7）。

---

## 0. 一頁摘要

- 論文是**一個文本、一位注家、一位分析者**的完整知識工程：
  331 字經文、27,902 字注釋、233 個節點、151 題問答。
- 本專案的格式可以承接大部分：科判→`anchor`、字碼→`span`、名相→`claim`、
  情境／互文→`edge`、集注→`compilation`。
- 需要新增的主要有五樣：**注釋樹的 anchor 命名空間、跨版本 `span_map`、
  `question/answer` 型別、label 的 vocabulary 欄、名相 `term` registry**。
- 不要把 S／E 字碼當永久 ID：它們綁 2011 版；跨版要另建對照。
- 已全部匯入 [`samples/jingang-2016/`](samples/jingang-2016/README.md)（238 anchors、151 題、278 答案）；
  仍建議先核「1 證信序」（23 節點、12 題）。

## 1. 論文提供的資料

| 項目 | 數量／範圍 | 出處 |
|---|---|---|
| 經文 S | 331 字（含標點 412）；S1–S412 | 表 3-4、附錄三 |
| 注釋 E | 27,902 字；E1–E27902 | 表 3-4、附錄五 |
| 昭明科判 | 3 個節點 | 表 3-3 |
| 江味農科判 | 11 個節點 | 表 3-4 |
| 李慧萍科判 | 193 個意義單位（29 個二層、164 個三層） | 表 3-5、附錄五 |
| 上層結構節點 | 29 個第二層＋11 個江味農＝40 個 | 附錄五 |
| 段落分析 | 205 段 | 附錄四 |
| 名相 | 3 類（金剛經／佛教文化歷史／一般佛學） | 表 3-6、附錄六 |
| 名相多義 | 8 型（同詞異義、引證、譯者、歷史故事、跡和本、通途和正指、本義和引申義、性和相） | 第三章第二節 |
| 情境指涉 | 8 種文句關係＋意義單位間的關連 | 表 3-9 |
| 互文 | 5 類（原本對譯本、譯本對譯本、版本比對、引證文獻、內容參照） | 表 3-9 |
| 文義思考 | 151 題、278 個答案列 | 附錄七 |
| 系統雛型 | 3 個（CDP 2.0、線上詞語對映、Accelon16） | 第四章 |

節點總數：**11（江味農）＋ 29（第二層結構）＋ 193（意義單位）＝ 233 個**。
E 範圍 1–27902 連續無缺口；S 範圍 1–412 連續無缺口（本次已驗）。

論文所稱「193 個科判節點」是最末端的**意義單位**；上層另有 29 個結構節點與
11 個江味農節點，所以整棵樹是 233 個節點。兩者不矛盾，但引用時要說清楚。

## 2. 對照總表

| 論文概念 | 本專案元件 | 狀態 |
|---|---|---|
| 科判節點（昭明／江味農／李慧萍） | `anchor` ＋ `label`（多套 vocabulary） | 已建 `labels.tsv` |
| 經文 S1–S412 | `span`（edition=JJN.2011, space=char） | 可承接 |
| 注釋 E1–E27902 | `span`（同上） | 可承接 |
| 江味農節點 → S／E | `anchor_map` ＋ `annotates` | 已建（207 spans、11 edges） |
| 193 個意義單位 | 注釋 `anchor`（`jjn/…`） | 已建（`samples/jingang-2016/`） |
| 名相 3 類 | `term` ＋ `lexical claim` | 需加 `terms.tsv` |
| 名相多義 8 型 | `claim.sense_type` | 需加欄位 |
| 情境 8 關係 | `edge.kind` | 需加枚舉 |
| 互文 5 類 | `edge`（`parallel_of`／`variant_of`／`quotes`／`refers_to`） | 需加 `parallel_of`／`variant_of`／`refers_to` |
| 151 題問答 | `question` ＋ `answered_by` | 已建（`question/0.1`） |
| 表 3-9 超聯繫 | `registry` | 可承接 |
| 三個雛型 | 介面需求 | 不在資料模型內 |

### 與現有 sample 的差距

| 現有 `samples/jingang` | 論文 | 差距 |
|---|---|---|
| 3 個經文 anchor（`vcpp/1`–`3`） | 233 個節點 | 需擴樹 |
| 13 條 claim | 193 個意義單位＋151 題 | 需分批匯入 |
| 9 條 edge（3 種 kind） | 8＋5 種關係 | 需補 registry |
| 2 條 compilation | 無（論文不是集注） | 不變 |

現有 sample 仍然有效，這份對照是**加法**，不是重寫。

## 3. 逐項說明

### 3.1 科判：anchor 與多套 vocabulary

三套科判同時存在，但分屬兩棵樹：昭明掛在經文 anchor，江味農與李慧萍掛在注釋 anchor（`jjn/`）。
這是「同一閱讀位置、多套名稱」的測試：

| vocabulary | 標了哪些節點 | 例（同一段經文） |
|---|---|---|
| 昭明太子 | 3 個經文段 | 法會因由分第一 |
| 江味農 | 11 個注釋大單元 | （丙）初，證信序 |
| 李慧萍 | 233 個節點（11 上層＋29 結構＋193 單位） | 1 證信序 |

所以嚴格說：`jjn/1` 同時有江味農與李慧萍兩個 label（同一 anchor、兩套 vocabulary）；
昭明的「法會因由分第一」在 `vcpp/1`，透過 `jjn/1 annotates vcpp/1` 與它們相連。
不是三個 label 擠在同一個 anchor 上，而是兩棵樹、三個名稱指向同一個閱讀位置。

目前 `anchors.tsv` 是「一個 anchor 一個 label」。要改成：

- `anchors.tsv` 只存身分與 parent；
- 新增 `labels.tsv`：`anchor, vocabulary, label, order, said_by, license`。

理由：label 不是中性資料。昭明、江味農、李慧萍各是作者，各有授權；
把三個名稱壓成一個欄位，等於把作者身分吃掉。

**注釋樹的兩種放法**

- **A. 掛在經文 anchor 下**（`vcpp/1/1-3`）：一棵樹，查「這段經文的所有注釋」最快；
  但同一子樹混了經文 span 與注釋 span，provenance 較亂。
- **B. 另立 `jjn/` 命名空間**，用 `annotates` 連到 `vcpp/1`：兩棵樹，一棵經文、一棵注釋；
  可換版本、可再接第二部注疏。

建議 **B**。理由：193 個節點切的是「江味農的注釋」，不是經文；而且現有 sample 的吉藏節錄
已經用 `work:T/1699 annotates anchor:vcpp/1`，同一個模式。

樹的樣子：

```
jjn/1            （江味農節點；E1-2684；S1-33）
├─ jjn/1-1       （李慧萍；E1-119）
├─ jjn/1-2       （李慧萍；E120-286）
├─ …
├─ jjn/1-6       （結構節點；無自己的 span）
│  ├─ jjn/1-6-1  （E722-1070）
│  └─ …
└─ jjn/1-9       （結構節點）
   └─ jjn/1-9-1  （E2235-2244）
```

注意：29 個第二層**結構**節點與 29 個第二層**意義單位**是兩批不同的節點
（前者有子節點，後者是葉節點）；不要合併。

### 3.2 字碼：span 與 edition

S／E 是 2011 版（頁 11–13、128–194）的**字元序號，包含標點**。
它們不是永久 ID，因為：

- 換版本（B23 數位版）標點就不同。例：2011 版「諸經通有故；亦名經後序」，
  B23 版「諸經通有故。亦名經後序」；
- 校勘夾註（如「校也，舊版無。據原稿補。」）算不算字數，會改變 offset；
- 2011 版的校勘記本身是編校者的工作，不是江味農原文。

做法：

- `span` 一律帶 `edition`；2011 版用 `JJN.2011`，B23 用 `JJN.B23`。
- 以 2011 版為論文的座標系；另建 `span_map`（S：2011 char ↔ T8.235／YLZ；
  E：2011 char ↔ B23 char），用句對齊＋人工核，不要把 offset 直接套過去。
- 字碼規則固定：Unicode code point、含標點、不含換行；校勘夾註算入 span 文字。
- `hash` 對 span 內文字計算；正規化只用於比對，不改 offset。

### 3.3 注釋樹：233 個節點

- 11 個江味農節點：有 E span（表 3-4）與 S span。
- 29 個第二層結構節點：只有 label，沒有自己的 span。
- 193 個意義單位：有 E span（附錄五），是檢索與問答的粒度。
- 內部節點不存 span；要查範圍時由子節點取 min/max。
- 只在 11 個江味農節點建 `annotates`（例：`jjn/1 annotates vcpp/1`）；
  查詢時由子節點上溯到江味農節點，不要重複 193 條。

查詢示例：

> 打開 `jjn/1`（江味農的證信序），問「這一支分成幾個意義單位？」
> → `jjn/1` → `part_of*` → 23 個葉節點。

（同一段經文可能有好幾個江味農節點：`vcpp/1` 就同時被 `jjn/1` 與 `jjn/2` 注釋。）

### 3.4 名相：term 與 lexical claim

- 3 類：金剛經名相、佛教文化歷史名相、一般佛學名相。
- 8 型多義：同詞異義、引證、譯者、歷史故事、跡和本、通途和正指、本義和引申義、性和相。
- 現在 sample 有 lexical claim，但沒有 term registry；要加 `terms.tsv`：

```
term_id	headword	category	aliases	note
t-0001	如是	金剛經	—	多義：信成就／如如不動／指下文…
t-0002	證信序	一般佛學	通序,經後序,遺教序	四名同指
```

- `claim` 加 `term_id`、`sense_type`（8 型之一）。
- 作者要分開：江味農的釋義是 `said_by: person:jiang-weinong, stance: source`；
  李慧萍的分類與命名則是另一條 claim（`said_by: person:lee-huiping`），
  型別可先用 `structural` 或 `analysis`。不要把兩者混成同一條 claim。

例：「如是」在 E287–436 是「信成就」；在 E1815–1892 是「如如不動」；
在 E2419–2684 又指「上句善護念、善付囑」。三條都掛 `t-0001`，各帶 `sense_type`。

### 3.5 情境指涉：8 種 edge

| 論文關係 | `edge.kind` | 例 |
|---|---|---|
| 整體部分 | `part_of` | 證信序整段 → 四個分句（通序／經後序／遺教序／證信序） |
| 總相別相 | `generic_specific` | 眾生 → 卵生、胎生、濕生、化生 |
| 能指所指 | `signifier_signified` | 「正明之文」→ 正明段 |
| 因果 | `causes` | 諸經通有 → 名為通序 |
| 引證說明 | `quotes` | 江味農引《大智度論》 |
| 同義名相 | `synonym_of` | 證信序＝通序＝經後序＝遺教序 |
| 名相釋義 | `defines` | 如是 → 信成就 |
| 名相說明 | `explains` | 四相 → 我相、人相、眾生相、壽者相 |

- 意義單位間的關連（18／3 個相關單位）用 `related_to` ＋ `note`（關鍵字與情境說明），
  不另立型別；關鍵字放 `evidence`。
- 每條 edge 都要有 `said_by`：文本是江味農的，關連判斷是李慧萍的。

### 3.6 互文：5 種 edge

| 論文類型 | `edge.kind` | 例 |
|---|---|---|
| 原本對譯本 | `parallel_of` ＋ `anchor_map` | 梵本 vs 六漢譯 |
| 譯本對譯本 | `parallel_of` | 羅什 vs 玄奘 |
| 版本甲對版本乙 | `variant_of` | 江味農版 vs CBETA 2011 版 |
| 引證文獻 | `quotes` | 《大般涅槃經》《大智度論》 |
| 內容參照 | `refers_to`（新） | 江味農「如是」vs 宗密《纂要》 |

- 現有 sample 的 edge 只用 `quotes`／`derives_from`／`annotates`；
  `parallel_of`／`variant_of`／`refers_to` 要新增。
- 兩端都要有 span；相似度放 `note`，不要當成事實。

### 3.7 文義思考：question／answer（新型別）

- 151 題、278 個答案列（平均 1.84 個答案）。
- 問題不是 claim：它是一個有作者、有範圍的**提示**；答案是經文或注釋的連結。
- 建議新 schema：

```json
{
  "schema": "question/0.1",
  "id": "q-jjn-0006",
  "text": "如是我聞的意義為何？",
  "asked_by": "person:lee-huiping",
  "scope_anchor": "jjn/1",
  "order": 6,
  "status": "draft",
  "license": "CC-BY-SA-4.0"
}
```

答案用 edge（`answers.tsv` 或 `edges.tsv` 的 `answered_by`）：

```
id	from	kind	to	said_by	recorded_by	status	evidence	note
e-q-0006-1	q-jjn-0006	answered_by	jjn/1-3	person:lee-huiping	actor:me	draft	附錄七 #6	信成就
e-q-0006-2	q-jjn-0006	answered_by	jjn/1-4	person:lee-huiping	actor:me	draft	附錄七 #6	聞成就
e-q-0006-3	q-jjn-0006	answered_by	jjn/1-8-1	person:lee-huiping	actor:me	draft	附錄七 #6	如是
e-q-0006-4	q-jjn-0006	answered_by	jjn/1-8-2	person:lee-huiping	actor:me	draft	附錄七 #6	我聞
```

- 多答案保留她的順序，加 `order_source: thesis`。
- 問題是她的人類著作；未來機器生成的問題只能 `draft`，不得發布。

### 3.8 表 3-9：type registry

表 3-9 已經把超聯繫整理成四層：

```
科判（結構樹）
名相釋義（類別：3 類；多義：8 型）
情境指涉（意義單位間；文句間：8 關係）
聯想（互文：5 類；文義思考問答）
```

把它變成 `registry.tsv`：

```
id	family	kind	label	description	status
R-01	structure	part_of	整體部分	…	active
R-02	structure	generic_specific	總相別相	…	active
…
R-21	intertext	refers_to	內容參照	…	proposed
```

所有 edge 的 `kind` 都要對到 registry；不要讓自由字串散在各檔。

### 3.9 三個雛型：介面需求

雛型不在資料模型內，但它們是驗收條件：

| 工具 | 對應查詢 | 雛型 |
|---|---|---|
| 內容架構 | anchor tree ＋ labels | CDP 2.0 可；Accelon16 開發中 |
| 字詞釋義 | term ＋ lexical claim | CDP 2.0、Accelon16 |
| 互為文本 | edge ＋ anchor_map | CDP 2.0、線上詞語對映、Accelon16 |
| 情境指涉 | edge（8 關係） | CDP 2.0 可；Accelon16 開發中 |
| 文義思考 | question／answer | CDP 2.0、Accelon16 |

- CDP 2.0 的「檢索夾」可列出某段文字作過的所有標誌與關連（**局部反查**）；
  Accelon16 可從注釋點回經文。
- 本專案要補的是**跨庫、可署名、可引用的永久逆鏈**，不是重做局部反查。
- Accelon16 的「經文與標記分離、標記可重疊」正是本專案 span／claim 分離的資料層等價物。

## 4. 資料形狀範例

### 4.1 anchors.tsv 與 labels.tsv

```
# anchors.tsv（label 移出，保留相容的空欄）
jjn		work	-	0	江味農《金剛般若波羅蜜經講義》
jjn/1	jjn	section	-	1	（丙）初，證信序；E1-2684
jjn/1-3	jjn/1	unit	-	3	1-3 如是與信成就；E287-436
```

```
# labels.tsv（新增）
anchor	vocabulary	label	order	said_by	license
jjn/1	jiang-weinong	（丙）初，證信序	1	person:jiang-weinong	PD
jjn/1	lee-huiping	1 證信序	1	person:lee-huiping	CC-BY-SA-4.0
jjn/1-3	lee-huiping	1-3 如是與信成就	3	person:lee-huiping	CC-BY-SA-4.0
```

### 4.2 anchor_map.tsv

```
anchor	edition	space	start	end	chars	text
vcpp/1	JJN.2011	char	1	33	33	如是我聞：一時……
jjn/1	JJN.2011	char	1	2684	2684	此證信序，又名通序……
jjn/1-3	JJN.2011	char	287	436	150	初曰如是者，不異為如……
vcpp/1	YLZ.235	line	2	13	86	如是我聞：一時，佛在舍衛國……
```

同一 anchor 可以有多個 edition 的 span；這正是「版本比對」的資料基礎。

### 4.3 claim（JSON）

```json
{
  "schema": "claim/0.1",
  "id": "c-jjn-0001",
  "version": 1,
  "domain": "jingang",
  "subject_anchor": "jjn/1-3",
  "type": "lexical",
  "term_id": "t-0001",
  "sense_type": "同詞異義",
  "proposition": "「如是」在此是信成就：不異為如，無非曰是。",
  "stance": "source",
  "said_by": "person:jiang-weinong",
  "recorded_by": "actor:me",
  "vouched_by": null,
  "origin": "source",
  "evidence": [
    {
      "kind": "text",
      "edition": "JJN.2011",
      "space": "char",
      "start": 287,
      "end": 436,
      "quote": "初曰如是者……故曰信成就也。"
    }
  ],
  "relations": [],
  "status": "draft",
  "license": "TBD",
  "date": "2026-10-21"
}
```

`term_id`、`sense_type` 是本次要新增的欄位（可空，舊資料不受影響）。

### 4.4 edge（TSV）

```
id	from	kind	to	said_by	recorded_by	status	evidence	note
e-jjn-0001	jjn/1	annotates	vcpp/1	actor:me	actor:me	reviewed	JJN.2011 1-33	江味農節點對應經文
e-jjn-0002	jjn/1-3	part_of	jjn/1	actor:me	actor:me	reviewed	—	李慧萍節點細分
e-jjn-0003	jjn/1-3	defines	t-0001	actor:me	actor:me	draft	E287-436	如是＝信成就
```

### 4.5 question（JSON）＋ answer edge

見 §3.7。答案 edge 可放 `edges.tsv`，也可另立 `answers.tsv`；建議另立，
因為 `answered_by` 的語意與一般 `edge` 不同（問題→答案，不是文本→文本）。

## 5. 入庫步驟與驗收

> 2026-10-21 現況：已建 `samples/jingang-2016/`（238 anchors、207 spans、151 題、278 答案）。
> 下列步驟保留作為驗收清單；已完成者標「已建」，其餘仍待。

1. **授權**：論文、江味農文本、2011 版編校、CBETA／DILA，逐一確認（§7）。
2. **建 2011 witness**：用附錄五的 E 全文＋表 3-4 的 S 全文重建，逐字核對紙本
   （頁 11–13、128–194）。這是唯一能讓 S／E 字碼有意義的版本。
   附錄五 193 列的 E 文字，去空白後實測 27,904 字，與 27,902 差 2 字；
   其中 10 個節點的段落邊界與 E 範圍不一致（見 `checks.tsv`），先逐列核對，再定 offsets。
3. **建 238 個 anchor（已建）**：11 江味農＋29 結構＋193 意義單位，
   另加 3 個經文段與 2 個 root；三套 label 進 `labels.tsv`。
4. **建 span＋span_map（部分）**：JJN.2011 的 S／E span 已建；S 端對 T8.235／YLZ、
   E 端對 B23 的 `span_map` 仍待。
5. **名相**：`terms.tsv`＋lexical claims（3 類、8 型）。
6. **edge**：8 種文句關係＋5 類互文，全部對 registry。
7. **question／answer（已建）**：151 題＋278 個答案列。`status` 仍為 `draft`，待逐題核。
8. **驗收**：
   - 193 個葉節點的 E 範圍連續覆蓋 1–27902（已驗無缺口）；
   - 11 個江味農節點覆蓋 S1–412；
   - 151 題每題至少 1 個答案，共 278 列；
   - 「如是我聞」的八人反查仍在；
   - 每條 claim 都有 `said_by／recorded_by／vouched_by／status／license`。
9. **不要做**：
   - 不要把 S／E 字碼當永久 ID；
   - 不要把 label 當無主資料；
   - 不要把 question 併進 claim；
   - 全量已匯入，但仍應先核「1 證信序」的 23 節點、12 題，再核其餘。

## 6. 要新增的 schema 元素

| 元素 | 現況 | 最小改動 |
|---|---|---|
| `labels.tsv` | 已建（247 列） | 保留；`anchors.label` 仍可相容 |
| `anchor.kind` | 已用 `workgroup`／`sutra`／`section`／`structure`／`unit` | 可再加 `commentary` |
| `span_map` | 無 | 新檔：`edition_a, start_a, end_a, edition_b, start_b, end_b, method, status` |
| `terms.tsv` | 無 | 新檔：`term_id, headword, category, aliases, note` |
| `claim.term_id`／`sense_type` | 無 | 加可空欄位 |
| `question/0.1`＋`answered_by` | 已建（151 題、278 答案） | 保留 |
| `edge` 8＋5 種 | 3 種（`annotates`／`derives_from`／`quotes`） | 加 registry 枚舉 |
| `registry.tsv` | 無 | 新檔 |
| `JJN.2011` edition | `samples/jingang-2016/works.tsv` 已有 | 補頁碼 11–13／128–194 |

## 7. 授權與邊界

- **論文**：© 李慧萍。233 個節點名稱、151 題問題是她的著作，不是中性資料。
  她是 [github.com/accelon/wisdomlight](https://github.com/accelon/wisdomlight) 的管理員之一，
  已同意把節點、問答放進本 repo；依 repo 預設以 **CC BY-SA 4.0** 釋出。
- **江味農文本**：作者 1940 年卒；正文在我國著作權法下可能已屆保護期，
  但 2011 版的編校、校勘記、排版可能另有權利，須個案確認。
- **CBETA B23**：限非商業使用；**DILA**：CC BY-NC-SA 4.0。
- 論文 docx 未放入本 repo；[`samples/jingang-2016/`](samples/jingang-2016/README.md)
  已放入節點、問答與 E 段文字（27,904 字），經李慧萍同意。
- 機器生成的白話、摘要、候選問答：一律 `draft`，不得發布。

## 8. 未決問題

1. **注釋樹放法**：A（掛在經文下）或 B（`jjn/` 另立）？已採 B，見 `samples/jingang-2016/`。
2. **233 個節點（jjn 樹）**：內部節點要不要都建 anchor？已建（無 span），
   另加 3 個經文段與 2 個 root，共 238。
3. **question 型別**：新 schema 或 claim subtype？已採 `question/0.1`。
4. **座標系**：2011 版或 B23？目前以 2011 為論文座標，B23 為第二見證，不設 canonical。
5. **對齊方法**：句對齊或字對齊？先句對齊，再人工核字碼。
6. **多答案順序**：保留她的順序，加 `order_source: thesis`。
7. **29 個結構節點的 label**：算結構 metadata 或 claim？已用 label＋`said_by`，不升成 claim。
8. **匯入範圍**：先 pilot「1 證信序」（23 節點、12 題），還是全量？已全量匯入；
   仍應先核 pilot。
9. **校勘夾註**：算 span 文字或另立 note？建議算文字，另在 `note` 說明。
10. **E 全文**：已入庫（27,904 字）；10 個邊界差異待核（`checks.tsv`）。

## 9. 變更記錄

- 2026-10-21：建立。對照 2016 年定稿（五章＋八附錄）；數字以附錄五、七實測為準。
- 2026-10-21：依本文建 `samples/jingang-2016/`（238 anchors、207 spans、151 題、278 答案）；
  李慧萍同意以 CC BY-SA 4.0 釋出節點與問答。
