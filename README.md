# Generation Gap Atlas / 世代間格差アトラス

公開サイト: https://nobby11334.github.io/generationgapatlas/

日本の就職氷河期世代と前後の世代を、公開統計と政府資料に基づき比較・検証する独立したオープンデータプロジェクト。

## 現在の実装（初版）
- **概観**：2025年の就職氷河期中心層（1974〜1983年生まれ）の政府公表KPIを表示。
- **世代比較**：比較可能な一次統計が揃わない指標は未掲載と明示。
- **政策トラッカー**：2026〜2028年度の新支援プログラム、雇用、訓練、社会参加、高齢期支援、終了済み地域交付金を整理。
- **政策効果測定**：政策実施、アウトカムの観測値、因果効果の判定を分離。未測定は未判定として表示。
- **特別年金シミュレーター**：対象人数、月額、給付開始・終了年齢から単純な年間・累積支給額を試算。
- **資料・方法論**：出典・限界・データ取り扱いを説明。

## エビデンス
- [内閣官房：関係閣僚会議](https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/kankeikakuryokaigi/index.html)
- [2026年4月10日決定プログラム KPI 別表](https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/kankeikakuryokaigi/pdf/20260410_siryou4.pdf)
- [2026年10月27日 第8回全国プラットフォーム・進捗資料](https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/suishin_platform/dai8/gijishidai.html)
- [厚生労働省：中高年の活躍支援](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/jinzaikaihatsu/shushoku_hyogaki_shien.html)
- [内閣府：地域就職氷河期世代支援加速化交付金（終了）](https://www5.cao.go.jp/keizai1/c_hyogaki/c_hyogaki.html)
- [e-Stat](https://www.e-stat.go.jp/)

## KPIの定義
- 正規雇用労働者率 71.2%（2025年）：1974〜1983年生まれ、役員を除く雇用者に占める正規従業員の割合。
- 不本意非正規雇用労働者率 8.8%（2025年）：同出生層の非正規従業員のうち「正規の仕事がないから」を主な理由とした人の割合。**全人口に占める割合ではありません。**

## 推計と実測の区分
「2026年新支援プログラムの効果」は現時点で因果推定していません。KPIや採用件数の前後比較だけでは政策効果を証明できません。50歳からの特別給付は現行制度ではなく、利用者入力による政策シナリオです。財政試算は単純化されたグロス給付であり、人口動態、税・社会保険料、現在価値、既存制度との調整を含みません。

## 公開・更新
GitHub Actions (.github/workflows/deploy.yml) が main push 時にGitHub Pagesへデプロイします。**デプロイの自動化と統計データの自動取得は別**です。初版では一次資料を検証して手動反映しています。誤った自動更新を避けるため、公開データを無検証で転載する処理は設けていません。

## 今後の拡張
1. 労働力調査・賃金構造基本統計調査・全国家計構造調査から、世代別に比較可能な長期時系列を取り込む。
2. 公的な政策KPIの年度別結果、予算・決算、受益者数を構造化し、根拠URLと取得日を管理。
3. 政策介入前後の系列比較・対照群設定を行い、因果推定の成立要件を開示。
4. 年金・税・所得の生涯シミュレーターを拡張し、制度案ごとの受益分布と負担分布を示す。
5. 機械検証済みの公開データ更新ワークフローを追加。

政治的立場や特定世代の優劣を示すことを目的とせず、検証可能な事実と政策選択肢を提供します。

## 2026-11-12 データ拡充
| ファイル | 範囲 | 注意 |
|---|---|---|
| `data/kpis.json` | 2026年4月公表の政府KPI 29指標、基準値、目標値、定義 | 2026年10月27日フォローアップの改定値は未反映・照合作業が必要 |
| `data/wages.json` | 男性一般労働者の実質月例賃金・4出生年代×6年齢階級（欠損はnull） | 全世代の生涯所得の推計ではない |
| `data/employment-history.json` | 2019〜2024年の就職氷河期中心層の雇用状態5系列 | 役員増等を含むため、政策の純効果とは解釈しない |
| `data/funding.json` | 予算・交付決定など7件 | 内数、重複、補正／当初、支出済額を厳格に区分 |

出典：[政府KPI別表](https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/kankeikakuryokaigi/pdf/20260410_siryou4.pdf)、[2019〜2023年特別集計](https://www.mhlw.go.jp/jigyo_shiwake/dl/r06_jigyou04a_day1.pdf)、[2025年政府基本方針](https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/kankeikakuryokaigi/pdf/20250603_kettei.pdf)、[地域交付金・2026年3月交付決定](https://www.cao.go.jp/shushoku_hyogaki/suishin/pdf/kettei-r08.pdf)、[2026年政策別予算](https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/kankeikakuryokaigi/dai3/siryou1-2.pdf)。

### カバレッジの限界
「完全網羅」は現状達成していません。政府の全施策、全年度・全自治体の執行額、正規・非正規を含む全年代の賃金・資産系列、2026年10月の最新KPI結果については未完成です。公開データの無い項目は推測で埋めず、未収録・未公開・照合未了を区別する必要があります。特に予算額と支出額の合算は行っていません。
