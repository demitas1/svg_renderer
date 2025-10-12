# SVGレンダリングプログラム設計書

## 1. 概要
Inkscapeで作成したSVGファイルから、特定のレイヤーを指定してPNG画像にレンダリングするPythonプログラムを作成します。

## 2. 要件
- **入力**: SVGファイル（Inkscape形式）
- **出力**: PNG画像（viewBoxのサイズに基づく）、またはSVGファイル
- **対象要素**: path要素とrect要素
- **レイヤー指定**: レイヤー名またはレイヤーIDで指定可能
- **スタイル適用**: stroke、fill、stroke-widthなどのSVG属性を反映
- **SVG出力**: 生成した形状を新しいSVGファイルとして保存可能

## 3. 技術スタック

### 推奨ライブラリ
1. **xml.etree.ElementTree** または **lxml**: SVGのXML解析・生成
2. **cairo** (pycairo): 高品質な2Dグラフィックスレンダリング（PNG出力用）
3. **svgwrite**: SVGファイルの生成（SVG出力用）
4. **PIL/Pillow**: 画像の最終出力（オプション）

### 代替案
- **svgwrite + cairosvg**: SVG操作とレンダリング
- **matplotlib**: 簡易的なレンダリング（品質は劣る）

## 4. プログラム構造

### 4.1 モジュール構成
```
src/
├── svg_renderer/           # メインパッケージ
│   ├── __init__.py        # パッケージAPI公開
│   ├── __main__.py        # CLIエントリーポイント
│   ├── api.py             # 統合API（SVGRendererクラス）
│   ├── cli.py             # CLI実装
│   ├── parser.py          # SVG解析モジュール
│   ├── layer.py           # レイヤー抽出モジュール
│   ├── renderer.py        # レンダリングエンジン（PNG用）
│   ├── writer.py          # SVG出力モジュール
│   └── style.py           # スタイル解析モジュール
└── examples/              # 使用例
    ├── render_layer.py    # レイヤーをPNGにレンダリング
    ├── export_layer.py    # レイヤーをSVGに抽出
    └── combine_layers.py  # 複数レイヤーの結合
```

### 4.2 主要クラス

#### SVGParser
- **責務**: SVGファイルの読み込みとXML解析
- **メソッド**:
  - `load_svg(filepath)`: SVGファイルを読み込む
  - `get_viewbox()`: viewBox属性を取得・解析
  - `get_namespaces()`: XML名前空間を取得

#### LayerExtractor
- **責務**: 特定レイヤーの要素を抽出
- **メソッド**:
  - `get_layer_by_name(layer_name)`: レイヤー名で検索
  - `get_layer_by_id(layer_id)`: レイヤーIDで検索
  - `extract_elements(layer)`: レイヤー内のpath/rect要素を抽出

#### StyleParser
- **責務**: SVG要素のスタイル属性を解析
- **メソッド**:
  - `parse_style(element)`: style属性を辞書に変換
  - `get_color(color_str)`: カラーコードをRGB値に変換
  - `get_stroke_width(width_str)`: 線幅を数値に変換

#### Renderer
- **責務**: Cairoを使用した実際のレンダリング（PNG出力）
- **メソッド**:
  - `setup_surface(width, height)`: 描画サーフェスの初期化
  - `render_path(path_data, style)`: path要素の描画
  - `render_rect(x, y, width, height, style)`: rect要素の描画
  - `save_png(output_path)`: PNG形式で保存

#### SVGWriter
- **責務**: SVGファイルの生成と出力
- **メソッド**:
  - `create_svg(viewbox, width, height)`: 新しいSVGドキュメントを作成
  - `add_layer(layer_name)`: レイヤー（g要素）を追加
  - `add_path(path_data, style, layer)`: path要素を追加
  - `add_rect(x, y, width, height, style, layer)`: rect要素を追加
  - `save_svg(output_path)`: SVGファイルとして保存
  - `preserve_namespaces()`: Inkscape名前空間を保持

## 5. データフロー

### PNG出力フロー
```
1. SVGファイル読み込み
   ↓
2. viewBox解析（出力サイズ決定）
   ↓
3. 指定レイヤーの検索・抽出
   ↓
4. レイヤー内のpath/rect要素を収集
   ↓
5. 各要素のスタイル属性を解析
   ↓
6. Cairoサーフェスを初期化
   ↓
7. 要素ごとにレンダリング
   ↓
8. PNG出力
```

### SVG出力フロー
```
1. SVGファイル読み込み（元ファイル）
   ↓
2. viewBox解析
   ↓
3. 指定レイヤーの検索・抽出
   ↓
4. 新しいSVGドキュメントを作成
   ↓
5. 元のviewBox、名前空間を継承
   ↓
6. レイヤー（g要素）を作成
   ↓
7. path/rect要素をスタイル付きで追加
   ↓
8. SVGファイル出力
```

### 形状生成後のSVG出力フロー
```
1. 元SVGから形状を読み込み
   ↓
2. ShapeGeneratorで新しい形状を生成
   ↓
3. 生成した形状を内部データ構造に保存
   ↓
4. SVGWriterで新しいSVGドキュメント作成
   ↓
5. 生成形状をSVG要素として追加
   ↓
6. SVGファイル出力
```

## 6. 主要処理の詳細

### 6.1 viewBox解析
```python
# viewBox="0 0 4960.6002 7015.706" の解析
viewbox_str = svg_root.get('viewBox')
x, y, width, height = map(float, viewbox_str.split())
```

### 6.2 レイヤー識別
Inkscapeのレイヤーは以下の特徴を持つ：
- `<g>` 要素
- `inkscape:groupmode="layer"` 属性
- `inkscape:label` 属性（レイヤー名）
- `id` 属性（レイヤーID）

### 6.3 path要素の処理
- `d` 属性のパスデータをパース
- Cairo Contextで `move_to()`, `line_to()`, `curve_to()` などに変換
- サポートするコマンド: M, L, C, Q, A, Z など

### 6.4 rect要素の処理
- `x`, `y`, `width`, `height` 属性を取得
- `transform` 属性があれば適用（rotation等）

### 6.5 スタイル適用
処理する属性：
- `fill`: 塗りつぶし色
- `fill-opacity`: 塗りつぶし不透明度
- `stroke`: 線の色
- `stroke-width`: 線の太さ
- `stroke-linejoin`: 線の結合スタイル
- `stroke-miterlimit`: マイター制限

## 7. エラーハンドリング

- **ファイルが存在しない**: FileNotFoundError
- **不正なSVGフォーマット**: xml.etree.ElementTree.ParseError
- **レイヤーが見つからない**: ValueError（カスタムメッセージ）
- **viewBoxがない**: デフォルト値を使用またはエラー
- **サポートされていないpath構文**: 警告を出して可能な範囲で描画

## 8. 使用例

### 8.1 ライブラリとして使用
```python
from svg_renderer import SVGRenderer

# レンダラーの初期化
renderer = SVGRenderer('drawing-example.svg')

# レイヤー指定でレンダリング
renderer.render_layer_to_png('Layer 1', 'output.png')

# または複数レイヤー
renderer.render_layers_to_png(['Layer 1', 'Layer 2'], 'combined.png')
```

### 8.2 SVG出力
```python
from svg_renderer import SVGRenderer

# レンダラーの初期化
renderer = SVGRenderer('drawing-example.svg')

# レイヤーを抽出してSVGとして保存
renderer.export_layer_to_svg('Layer 1', 'layer1.svg')

# 複数レイヤーを結合してSVG出力
renderer.export_layers_to_svg(['Layer 1', 'Layer 2'], 'combined.svg')
```

### 8.3 CLIとして使用
```bash
# レイヤーのリスト表示
PYTHONPATH=src python -m svg_renderer drawing-example.svg --list-layers

# 単一レイヤーをPNGに出力
PYTHONPATH=src python -m svg_renderer drawing-example.svg \
  --layer "Layer 1" --output output.png

# 単一レイヤーをSVGに出力
PYTHONPATH=src python -m svg_renderer drawing-example.svg \
  --layer "Layer 1" --output output.svg --format svg

# 複数レイヤーを結合してPNG出力
PYTHONPATH=src python -m svg_renderer drawing-example.svg \
  --layer "Layer 1" --layer "Layer 2" --output combined.png
```

### 8.4 形状生成とSVG出力（将来の実装）
```python
from svg_renderer import SVGRenderer
from svg_renderer.shapes import ShapeGenerator  # 将来実装予定

# レンダラーとジェネレータの初期化
renderer = SVGRenderer('drawing-example.svg')
generator = ShapeGenerator(renderer)

# Layer 1からpath要素を取得
original_path = renderer.get_element_by_id('path1')

# オフセット形状を生成
offset_path = generator.offset_path(original_path, offset=10)

# 回転パターンを生成
pattern = generator.radial_pattern(
    original_path,
    count=12,
    angle=30,
    center=(2480, 3507)
)

# 生成した形状をSVGファイルとして出力
renderer.create_new_svg(
    layers={
        'Original': [original_path],
        'Offset': [offset_path],
        'Pattern': pattern
    },
    output='generated_shapes.svg'
)

# またはPNG出力も可能
renderer.render_generated_shapes(
    pattern,
    output='pattern.png'
)
```

## 9. 今後の拡張性

### 9.1 基本機能の拡張
- **transform属性の完全サポート**: translate, rotate, scale, skew
- **circle, ellipse要素のサポート**
- **グラデーション・パターンのサポート**
- **テキスト要素のサポート**
- **アンチエイリアシングのオプション**
- **背景色の指定**
- **出力サイズのカスタマイズ**（viewBoxと異なるサイズ）

### 9.2 特殊形状生成機能
読み込んだpath、rect要素を基準として、プログラマティックに新しい形状を生成する機能を追加します。

#### 9.2.1 形状の変形・変換
- **オフセット**: path/rectの輪郭を内側/外側に拡大・縮小
- **ブーリアン演算**: 複数の形状の和集合、差集合、積集合
- **モーフィング**: 2つの形状間の中間形状を生成
- **パスの単純化**: 頂点数を削減して軽量化

#### 9.2.2 パターン生成
- **配列複製**: 形状を格子状やパス沿いに複製
- **回転パターン**: 中心点を軸に形状を回転配置（万華鏡効果）
- **フラクタル生成**: 再帰的に形状を分割・変形

#### 9.2.3 形状解析に基づく生成
- **境界ボックス取得**: path/rectの外接矩形を計算
- **重心計算**: 形状の中心点を求める
- **面積計算**: ポリゴンの面積を算出
- **交点検出**: 複数の形状の交差部分を検出

#### 9.2.4 パス操作
- **パスの分割**: 長いパスを複数のセグメントに分割
- **パスの結合**: 複数のパスを1つに統合
- **パスの反転**: 描画方向を逆転
- **パスのスムージング**: ベジェ曲線で滑らかに

#### 9.2.5 実装例
```python
from svg_renderer import SVGRenderer, ShapeGenerator

renderer = SVGRenderer('drawing-example.svg')
generator = ShapeGenerator(renderer)

# Layer 1からpath要素を取得
original_path = renderer.get_element_by_id('path1')

# オフセット形状を生成（10ピクセル外側）
offset_path = generator.offset_path(original_path, offset=10)

# 回転パターンを生成（12個、30度ずつ）
pattern = generator.radial_pattern(
    original_path, 
    count=12, 
    angle=30,
    center=(2480, 3507)  # viewBoxの中心
)

# 新しいレイヤーとして追加
renderer.add_layer('Generated Shapes', pattern)
renderer.render_layer('Generated Shapes', output='generated.png')
```

#### 9.2.6 ユースケース
- **装飾デザイン**: 基本形状から複雑なパターンを自動生成
- **プロトタイピング**: デザインのバリエーション作成
- **データ可視化**: データに基づいて形状をパラメトリックに変更
- **アニメーション**: 形状の時系列変化をフレームごとに生成
- **レーザーカット/3Dプリント**: 製造用のパス調整（オフセット、結合など）

## 10. パフォーマンス考慮事項

- 大きなviewBoxの場合、メモリ使用量に注意
- path要素が複雑な場合、レンダリング時間が増加
- 必要に応じてプログレスバー表示

## 11. 実装の優先順位

### フェーズ1: 基本機能（MVP）✅ **完了**
1. ✅ SVGファイルの読み込みとviewBox解析
2. ✅ レイヤーの抽出（名前またはIDで指定）
3. ✅ rect要素の基本レンダリング（塗りつぶしと線）
4. ✅ path要素のレンダリング（M, L, C, Zコマンド）
5. ✅ PNG出力
6. ✅ SVG出力の基本実装
7. ✅ CLIインターフェース
8. ✅ パッケージ化とAPI整備
9. ✅ 単体テスト（19テスト）
10. ✅ 使用例（examples/）

**実装済みの構造:**
- `src/svg_renderer/`: メインパッケージ
- `src/examples/`: 使用例スクリプト
- `tests/`: 単体テスト
- `docs/`: ドキュメント

### フェーズ2: 機能拡張（今後）
1. path要素の追加コマンド（Q, S, T, H, V, Aコマンド）
2. スタイル属性の完全サポート（dasharray等）
3. transform属性の基本サポート（translate, rotate）
4. SVG出力時の名前空間とメタデータの完全保持
5. エラーハンドリングの強化

### フェーズ3: 高度な機能（将来）
1. 楕円弧（Aコマンド）のサポート
2. 複雑なtransformの完全サポート（scale, skew, matrix）
3. その他の図形要素のサポート（circle, ellipse, polygon）
4. **形状生成機能（ShapeGenerator）の実装**
5. グラデーション、パターンのサポート

## 12. テスト計画

### 単体テスト
- SVGParser: viewBox解析の正確性
- LayerExtractor: レイヤー検索の正確性
- StyleParser: 各種スタイル属性の解析

### 統合テスト
- サンプルSVGファイルでの完全なレンダリング
- 複数レイヤーの処理
- エッジケース（空のレイヤー、不正なデータなど）

### 視覚的テスト
- レンダリング結果とInkscapeでの表示の比較
- 各種スタイルの正確な再現

### SVG出力テスト
- 出力されたSVGファイルがInkscapeで正しく開けるか
- 元のSVGと出力SVGの視覚的な一致性
- 名前空間とメタデータの保持確認
- 生成された形状が正しくSVG要素として出力されているか
