# SVG Renderer

InkscapeのSVGファイルから特定のレイヤーを抽出し、PNG画像またはSVGファイルとして出力するPythonツールです。

## 機能

- **レイヤー抽出**: Inkscape SVGファイルから名前またはIDでレイヤーを抽出
- **PNG出力**: 指定したレイヤーをCairoを使って高品質なPNG画像にレンダリング
- **SVG出力**: レイヤーを新しいSVGファイルとして保存
- **複数レイヤー対応**: 複数のレイヤーを一度にレンダリング・出力可能
- **スタイル保持**: fill、stroke、stroke-width等のスタイル属性を正確に再現

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

### CLIとして使用

```bash
# レイヤーのリストを表示
PYTHONPATH=src python -m svg_renderer <SVGファイル> --list-layers

# 単一レイヤーをPNGに出力
PYTHONPATH=src python -m svg_renderer <SVGファイル> --layer "Layer 1" --output output.png

# 単一レイヤーをSVGに出力
PYTHONPATH=src python -m svg_renderer <SVGファイル> --layer "Layer 1" --output output.svg --format svg

# 複数レイヤーを組み合わせてPNGに出力
PYTHONPATH=src python -m svg_renderer <SVGファイル> --layer "Layer 1" --layer "Layer 2" --output combined.png
```

### ライブラリとして使用

```python
from svg_renderer import SVGRenderer

# レンダラーを初期化
renderer = SVGRenderer('input.svg')

# レイヤーをリスト表示
layers = renderer.list_layers()
print(layers)

# レイヤーをPNGにレンダリング
renderer.render_layer_to_png('Layer 1', 'output.png')

# レイヤーをSVGとして抽出
renderer.export_layer_to_svg('Layer 1', 'output.svg')

# 複数レイヤーを結合
renderer.render_layers_to_png(['Layer 1', 'Layer 2'], 'combined.png')
```

### 実行例（CLI）

```bash
# サンプルSVGのレイヤーを確認
PYTHONPATH=src python -m svg_renderer tests/fixtures/drawing-example.svg --list-layers

# Layer 1をPNGに出力
PYTHONPATH=src python -m svg_renderer tests/fixtures/drawing-example.svg \
  --layer "Layer 1" --output layer1.png

# Layer 1をSVGとして抽出
PYTHONPATH=src python -m svg_renderer tests/fixtures/drawing-example.svg \
  --layer "Layer 1" --output layer1.svg --format svg

# 両方のレイヤーを結合してPNG出力
PYTHONPATH=src python -m svg_renderer tests/fixtures/drawing-example.svg \
  --layer "Layer 1" --layer "Layer 2" --output both_layers.png
```

### 実行例（ライブラリ）

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

## コマンドラインオプション

- `input`: 入力SVGファイルのパス（必須）
- `--list-layers`: SVGファイル内のレイヤーをリスト表示
- `--layer`, `-l`: 処理するレイヤーの名前またはID（複数指定可能）
- `--output`, `-o`: 出力ファイルのパス
- `--format`, `-f`: 出力形式（`png`または`svg`、デフォルト: `png`）

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
