# SVG Renderer

InkscapeのSVGファイルから特定のレイヤーを抽出し、PNG画像またはSVGファイルとして出力するPythonツールです。

## 機能

- **レイヤー抽出**: Inkscape SVGファイルから名前またはIDでレイヤーを抽出
- **PNG出力**: 指定したレイヤーをCairoを使って高品質なPNG画像にレンダリング
- **DPI指定**: 96dpi（画面表示用）から300dpi（印刷用）まで任意のDPIでレンダリング可能
- **SVG出力**: レイヤーを新しいSVGファイルとして保存
- **複数レイヤー対応**: 複数のレイヤーを一度にレンダリング・出力可能
- **スタイル保持**: fill、stroke、stroke-width等のスタイル属性を正確に再現
- **単位対応**: mm、cm、in、pt等の単位を自動検出してDPI計算に反映

## インストール

### 依存関係

このプロジェクトには以下のライブラリが必要です：

- lxml: SVGのXML解析
- pycairo: 高品質な2Dグラフィックスレンダリング
- pytest: テスト実行

### セットアップ

```bash
# 仮想環境をアクティベート
source src/venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# または個別にインストール
pip install lxml pycairo pytest
```

## 使い方

### ライブラリとして使用

```python
from svg_renderer import SVGRenderer

# レンダラーを初期化
renderer = SVGRenderer('input.svg')

# レイヤーをリスト表示
layers = renderer.list_layers()
print(layers)

# レイヤーをPNGにレンダリング（viewBoxサイズそのまま）
renderer.render_layer_to_png('Layer 1', 'output.png')

# レイヤーをSVGとして抽出
renderer.export_layer_to_svg('Layer 1', 'output.svg')

# 複数レイヤーを結合
renderer.render_layers_to_png(['Layer 1', 'Layer 2'], 'combined.png')
```

### DPIを指定してレンダリング

```python
from svg_renderer import SVGRenderer

# 300dpi（印刷用）でレンダラーを初期化
renderer = SVGRenderer('input.svg', dpi=300)

# A4サイズ（210mm x 297mm）のSVGの場合、出力は 2480 x 3508 ピクセル
renderer.render_layer_to_png('Layer 1', 'output_300dpi.png')

# 96dpi（画面表示用）の場合
renderer_screen = SVGRenderer('input.svg', dpi=96)
renderer_screen.render_layer_to_png('Layer 1', 'output_96dpi.png')
```

### 実行例

```bash
# サンプルスクリプトの実行
cd src/examples

# 単一レイヤーをレンダリング
python render_layer.py

# レイヤーをSVGとして抽出
python export_layer.py

# 複数レイヤーを結合
python combine_layers.py
```

## サンプルプログラム（examples）

`src/examples/` ディレクトリには、SVGRendererライブラリの主要な機能を示す3つのサンプルプログラムが含まれています。

### render_layer.py - 単一レイヤーをPNGに出力

**機能**: InkscapeのSVGファイルから指定したレイヤーを抽出し、PNG画像として出力します。

- SVGファイル内の全レイヤー名を一覧表示
- 指定したレイヤー（"Layer 1"）をPNG形式でレンダリング
- Cairo描画エンジンを使用した高品質な出力

**使用例**:
```bash
cd src/examples
python render_layer.py
```

**出力**:
```
Available layers:
  1. Layer 1
  2. Layer 2

Successfully rendered to example_layer1.png
```

### export_layer.py - 単一レイヤーをSVGとして抽出

**機能**: InkscapeのSVGファイルから特定のレイヤーのみを抽出し、新しいSVGファイルとして保存します。

- 元のSVGから指定レイヤー（"Layer 1"）の要素のみを抽出
- 新しいSVGファイルとして保存（Inkscape等で再編集可能）
- スタイル属性を保持したまま抽出

**使用例**:
```bash
cd src/examples
python export_layer.py
```

**出力**:
```
Successfully exported to example_layer1.svg
```

### combine_layers.py - 複数レイヤーの結合

**機能**: 複数のレイヤーを組み合わせて、1つのPNGまたはSVGファイルとして出力します。

- SVGファイル内の全レイヤーを取得
- 全レイヤーを結合してPNG画像として出力
- 全レイヤーを結合してSVGファイルとして出力
- レイヤーの重ね順を維持

**使用例**:
```bash
cd src/examples
python combine_layers.py
```

**出力**:
```
Combining 2 layers: Layer 1, Layer 2
Rendered combined PNG to example_combined.png
Exported combined SVG to example_combined.svg
```

### サンプルで使用される主要API

各サンプルでは以下のSVGRenderer APIを使用しています：

| メソッド | 説明 |
|----------|------|
| `SVGRenderer(svg_file, dpi=None)` | SVGファイルを読み込んでレンダラーを初期化（dpiで解像度指定） |
| `list_layers()` | 利用可能なレイヤー名のリストを取得 |
| `render_layer_to_png(layer, output)` | 単一レイヤーをPNGに出力 |
| `export_layer_to_svg(layer, output)` | 単一レイヤーをSVGとして抽出 |
| `render_layers_to_png(layers, output)` | 複数レイヤーを結合してPNGに出力 |
| `export_layers_to_svg(layers, output)` | 複数レイヤーを結合してSVGに出力 |

## コマンドラインインターフェース

### 基本的な使い方

```bash
# レイヤーの一覧を表示
PYTHONPATH=src python -m svg_renderer input.svg --list-layers

# レイヤーをPNGにレンダリング（viewBoxサイズそのまま）
PYTHONPATH=src python -m svg_renderer input.svg --layer "Layer 1" -o output.png

# 300dpiでレンダリング（印刷用）
PYTHONPATH=src python -m svg_renderer input.svg --layer "Layer 1" --dpi 300 -o output.png

# SVG形式で出力
PYTHONPATH=src python -m svg_renderer input.svg --layer "Layer 1" -f svg -o output.svg
```

### オプション一覧

| オプション | 説明 |
|-----------|------|
| `input` | 入力SVGファイルのパス（必須） |
| `--list-layers` | SVGファイル内のレイヤーをリスト表示 |
| `--layer`, `-l` | 処理するレイヤーの名前またはID（複数指定可能） |
| `--output`, `-o` | 出力ファイルのパス |
| `--format`, `-f` | 出力形式（`png`または`svg`、デフォルト: `png`） |
| `--dpi` | PNGレンダリングのDPI（例: 96=画面用, 300=印刷用） |

### DPIについて

DPIを指定しない場合、viewBoxの値がそのままピクセル数として使用されます。

DPIを指定すると、SVGのドキュメント単位（mm、cm、in等）に基づいてピクセルサイズが計算されます：

| ドキュメントサイズ | DPI | 出力ピクセルサイズ |
|------------------|-----|------------------|
| A4 (210mm x 297mm) | 96 | 794 x 1123 |
| A4 (210mm x 297mm) | 300 | 2480 x 3508 |
| Letter (8.5in x 11in) | 300 | 2550 x 3300 |

## アーキテクチャ

プロジェクトはSOLID原則に基づいたモジュール構造になっています：

### パッケージ構造

```
src/
├── svg_renderer/              # メインパッケージ
│   ├── __init__.py           # パッケージAPI公開
│   ├── __main__.py           # CLI実行エントリーポイント
│   ├── api.py                # SVGRenderer統合クラス
│   ├── cli.py                # CLI実装
│   ├── parser.py             # SVG解析（旧 svg_parser.py）
│   ├── style.py              # スタイル解析（旧 style_parser.py）
│   ├── layer.py              # レイヤー抽出（旧 layer_extractor.py）
│   ├── renderer.py           # Cairoレンダリング
│   └── writer.py             # SVG出力（旧 svg_writer.py）
└── examples/                  # 使用例
    ├── render_layer.py       # レイヤーをPNGにレンダリング
    ├── export_layer.py       # レイヤーをSVGに抽出
    └── combine_layers.py     # 複数レイヤーの結合
```

### 主要クラス

- **SVGRenderer** (api.py): 高レベル統合API
- **SVGParser** (parser.py): SVGファイルの読み込み、viewBox解析
- **LayerExtractor** (layer.py): Inkscapeレイヤーの識別と抽出
- **StyleParser** (style.py): スタイル属性の解析とカラー変換
- **Renderer** (renderer.py): Cairoベースのレンダリングエンジン
- **SVGWriter** (writer.py): SVGファイルの生成と出力

### データフロー

#### PNG出力
```
SVGファイル読み込み
  ↓
viewBox解析
  ↓
レイヤー抽出
  ↓
要素収集（path, rect）
  ↓
スタイル解析
  ↓
Cairoレンダリング
  ↓
PNG保存
```

#### SVG出力
```
SVGファイル読み込み
  ↓
viewBox解析
  ↓
レイヤー抽出
  ↓
新規SVGドキュメント作成
  ↓
要素とスタイルをコピー
  ↓
SVG保存
```

## テスト

```bash
# 仮想環境をアクティベート
source src/venv/bin/activate

# すべてのテストを実行
python -m pytest tests/ -v

# 特定のテストファイルを実行
python -m pytest tests/test_svg_parser.py -v

# レンダリングテストのみ実行
python -m pytest tests/test_renderer.py -v

# 画像比較の閾値を変更して実行
python -m pytest tests/ --image-threshold=0.01
```

### テストカテゴリ

| テストクラス | 説明 |
|-------------|------|
| `TestCairoRectRendering` | rect要素のCairoレンダリング検証 |
| `TestCairoPathRendering` | path要素のCairoレンダリング検証 |
| `TestImageDimensions` | 出力画像サイズの検証 |
| `TestInkscapeCompatibility` | Inkscape出力との互換性（viewBoxサイズ） |
| `TestInkscapeCompatibilityDPI` | Inkscape出力との互換性（DPI指定、300dpi） |

### テストケースの追加方法

DPI対応のInkscape互換性テストを追加するには：

1. `tests/fixtures/` にSVGファイルとInkscapeでエクスポートしたPNGを配置
2. `tests/test_renderer.py` の `DPI_TEST_CASES` リストにエントリを追加

```python
DPI_TEST_CASES = [
    # (SVGファイル名, PNG名, レイヤー名, DPI, 期待サイズ, 説明)
    ('new-test.svg', 'new-test.png', 'Layer 1', 300, (2480, 3508), 'New test case'),
]
```

## 実装状況

### フェーズ1: MVP（完了✓）

- [x] SVGファイルの読み込みとviewBox解析
- [x] レイヤーの抽出（名前またはIDで指定）
- [x] rect要素の基本レンダリング
- [x] path要素のレンダリング（M, L, C, Zコマンド対応）
- [x] PNG出力
- [x] SVG出力の基本実装
- [x] 基本的なスタイル属性のサポート
- [x] 単体テスト
- [x] DPI指定によるレンダリング（96dpi〜300dpi）
- [x] ドキュメント単位（mm, cm, in等）の自動検出

### フェーズ2: 機能拡張（今後）

- [ ] path要素の追加コマンド（Q, S, T, H, V, A）
- [ ] スタイル属性の完全サポート（dasharray等）
- [ ] transform属性の基本サポート（translate, rotate）
- [ ] SVG出力時の完全な名前空間保持

### フェーズ3: 高度な機能（将来）

- [ ] circle, ellipse要素のサポート
- [ ] 複雑なtransformの完全サポート
- [ ] 形状生成機能（ShapeGenerator）
- [ ] グラデーション、パターンのサポート

## サポートされている要素とスタイル

### 要素タイプ
- `<path>`: M, L, C, Zコマンド（相対座標含む）
- `<rect>`: 基本的な矩形

### スタイル属性
- `fill`: 塗りつぶし色（hex、named colors）
- `fill-opacity`: 塗りつぶし不透明度
- `stroke`: 線の色
- `stroke-width`: 線の太さ
- `stroke-opacity`: 線の不透明度
- `stroke-linejoin`: 線の結合スタイル
- `stroke-miterlimit`: マイター制限

## トラブルシューティング

### レイヤーが見つからない
```bash
# レイヤー名を確認
python src/main.py <SVGファイル> --list-layers
```

### レンダリング結果がおかしい
- サポートされていないpath コマンドが含まれている可能性があります
- 現在サポートしているのは M, L, C, Z コマンドです

## ライセンス

MIT
