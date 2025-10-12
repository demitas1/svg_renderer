# 実装計画と進捗状況

## プロジェクト概要

InkscapeのSVGファイルから特定のレイヤーを抽出し、PNG画像またはSVGファイルとして出力するPythonツール。

**現在のステータス**: フェーズ1（MVP）完了 ✅

## 実装フェーズ

### フェーズ1: MVP（最小限の機能実装）

**目標**: 基本的なSVG読み込み、レイヤー抽出、シンプルなレンダリング、PNG/SVG出力

#### 1.1 基盤モジュールの実装

**`src/svg_parser.py`**
- SVGファイルの読み込み（lxml使用）
- viewBox属性の解析（x, y, width, height）
- XML名前空間の取得と管理
- SVGルート要素へのアクセス

**`src/style_parser.py`**
- style属性文字列の辞書への変換
- 個別SVG属性の取得（fill, stroke, stroke-width等）
- カラーコードのRGB値への変換（hex, named colors）
- 数値+単位の解析（stroke-width等）

**`src/layer_extractor.py`**
- Inkscapeレイヤーの識別（`inkscape:groupmode="layer"`）
- レイヤー名による検索（`inkscape:label`）
- レイヤーIDによる検索（`id`属性）
- レイヤー内のpath/rect要素の抽出

#### 1.2 レンダリングモジュール

**`src/renderer.py`**
- Cairoサーフェスの初期化（viewBoxサイズ）
- rect要素のレンダリング
  - x, y, width, height属性の取得
  - 塗りつぶし（fill）の適用
  - ストローク（stroke, stroke-width）の適用
- path要素の基本レンダリング（M, L, Zコマンドのみ）
  - パスコマンドのパース
  - Cairo Contextへの変換（move_to, line_to, close_path）
  - スタイルの適用
- PNG形式での保存

#### 1.3 SVG出力モジュール

**`src/svg_writer.py`**
- 新しいSVGドキュメントの作成（svgwrite使用）
- 元SVGからviewBoxの継承
- Inkscape名前空間の保持
- レイヤー（g要素）の作成と属性設定
- path要素の追加（d属性とstyle）
- rect要素の追加（x, y, width, height, style）
- SVGファイルとして保存

#### 1.4 統合とテスト

**`src/main.py`**
- コマンドライン引数の処理
- モジュールの統合
- 基本的な使用例の実装

**`tests/`**
- `test_svg_parser.py`: viewBox解析のテスト
- `test_style_parser.py`: スタイル解析のテスト
- `test_layer_extractor.py`: レイヤー抽出のテスト
- `test_renderer.py`: レンダリング結果の検証
- `test_svg_writer.py`: SVG出力の検証
- `test_integration.py`: エンドツーエンドテスト

**必要な依存関係**
```bash
# venv環境で実行
source venv/bin/activate
pip install lxml pycairo svgwrite pytest
```

### フェーズ2: 機能拡張

**目標**: パスの曲線サポート、スタイルの完全対応、transform属性の基本サポート

#### 2.1 パスレンダリングの拡張

- 3次ベジェ曲線（C, cコマンド）のサポート
- 2次ベジェ曲線（Q, qコマンド）のサポート
- 相対座標コマンド（小文字コマンド）の完全サポート
- S, T（滑らかな曲線）コマンドのサポート
- H, V（水平・垂直線）コマンドのサポート

#### 2.2 スタイル処理の完全実装

- fill-opacity, stroke-opacityのサポート
- stroke-linejoin（miter, round, bevel）
- stroke-linecap（butt, round, square）
- stroke-miterlimitの適用
- stroke-dasharrayのサポート
- rgb(), rgba()カラーフォーマットのサポート

#### 2.3 Transform属性の基本サポート

- transform属性のパース
- translate(tx, ty)変換
- rotate(angle [cx cy])変換
- Cairo変換行列への適用
- SVG出力時のtransform属性保持

#### 2.4 エラーハンドリングの強化

- 詳細なエラーメッセージ
- 利用可能なレイヤー名のリスト表示
- サポートされていないコマンドの警告
- 部分的なレンダリング継続

### フェーズ3: 高度な機能

**目標**: より複雑な形状とtransform、形状生成機能

#### 3.1 追加の図形要素

- 楕円弧（A, aコマンド）のサポート
- circle要素のレンダリング
- ellipse要素のレンダリング
- polygon/polyline要素のサポート

#### 3.2 複雑なTransform

- scale(sx [sy])変換
- skewX(angle), skewY(angle)変換
- 複数transformの組み合わせ
- 変換行列（matrix）のサポート

#### 3.3 形状生成機能（ShapeGenerator）

**`src/shape_generator.py`**
- パスのオフセット（内側・外側への拡大縮小）
- 回転パターン生成（放射状配置）
- 境界ボックスの計算
- 重心の計算
- パスの結合・分割

#### 3.4 追加機能

- グラデーションのサポート
- パターンのサポート
- クリッピングパスのサポート
- マスクのサポート
- テキスト要素の基本サポート

## 実装の進め方

### ステップ1: 環境準備 ✅ 完了
1. ✅ 仮想環境の作成（`src/venv/`）
2. ✅ 依存関係のインストール（lxml, pycairo, pytest）
3. ✅ プロジェクト構造の作成

### ステップ2: フェーズ1の実装 ✅ 完了
1. ✅ 基盤モジュール（Parser系）の実装
2. ✅ レンダリングモジュールの実装
3. ✅ SVG出力モジュールの実装
4. ✅ 各モジュールごとにテストを作成（19テスト）
5. ✅ 統合テスト
6. ✅ パッケージ化とリファクタリング

### ステップ3: フェーズ2への移行
1. パスコマンドの拡張
2. スタイル属性の拡張
3. Transform属性のサポート
4. テストの追加

### ステップ4: フェーズ3（将来）
1. 追加図形要素のサポート
2. 形状生成機能の実装
3. 高度な機能の追加

## 技術的な設計原則

### SOLID原則の適用

1. **Single Responsibility Principle（単一責任の原則）**
   - SVGParser: SVG読み込みと解析のみ
   - LayerExtractor: レイヤー抽出のみ
   - Renderer: レンダリングのみ
   - StyleParser: スタイル解析のみ

2. **Open/Closed Principle（開放閉鎖の原則）**
   - 新しいパスコマンドや図形要素を追加しやすい設計
   - 拡張ポイントの明確化

3. **Liskov Substitution Principle（リスコフの置換原則）**
   - 基底クラス/インターフェースの適切な設計

4. **Interface Segregation Principle（インターフェース分離の原則）**
   - 小さく特化したインターフェース
   - 不要な依存関係を持たない

5. **Dependency Inversion Principle（依存性逆転の原則）**
   - 具象クラスではなく抽象に依存
   - 依存性注入の活用

### コード品質

- 型ヒントの使用（Python 3.9+）
- Docstringによる詳細なドキュメント
- PEP 8準拠
- ユニットテストのカバレッジ80%以上
- 適切なエラーハンドリング
- ログ出力による動作の可視化

### パフォーマンス考慮

- 大きなviewBoxでのメモリ使用量管理
- 複雑なpathの効率的な処理
- 必要に応じたキャッシング
- プログレスバー表示（大規模ファイル用）

## 成果物

### フェーズ1完了時 ✅
- ✅ 動作する基本的なSVGレンダラー
- ✅ 単純な形状（rect、曲線を含むpath）のPNG出力
- ✅ レイヤー抽出機能
- ✅ SVG出力機能
- ✅ 基本的なテストスイート（19テスト、全合格）
- ✅ CLIインターフェース
- ✅ パッケージ化された構造
- ✅ 使用例（examples/）
- ✅ 完全なドキュメント

### フェーズ2完了時
- 曲線を含む複雑なpathのサポート
- 完全なスタイル属性のサポート
- 基本的なtransformのサポート
- 包括的なテストスイート

### フェーズ3完了時
- すべての基本的なSVG図形のサポート
- 完全なtransformのサポート
- 形状生成機能
- 実用的なアプリケーション

## 完了した実装

### プロジェクト構造
```
src/
├── svg_renderer/              # メインパッケージ
│   ├── __init__.py           # パッケージAPI公開
│   ├── __main__.py           # CLIエントリーポイント
│   ├── api.py                # SVGRenderer統合クラス
│   ├── cli.py                # CLI実装
│   ├── parser.py             # SVG解析
│   ├── style.py              # スタイル解析
│   ├── layer.py              # レイヤー抽出
│   ├── renderer.py           # Cairoレンダリング
│   └── writer.py             # SVG出力
└── examples/                  # 使用例
    ├── render_layer.py
    ├── export_layer.py
    └── combine_layers.py
```

### 使用方法

**CLIとして:**
```bash
PYTHONPATH=src python -m svg_renderer input.svg --list-layers
PYTHONPATH=src python -m svg_renderer input.svg --layer "Layer 1" -o output.png
```

**ライブラリとして:**
```python
from svg_renderer import SVGRenderer

renderer = SVGRenderer('input.svg')
renderer.render_layer_to_png('Layer 1', 'output.png')
```

## 次のアクション（フェーズ2以降）

1. path要素の追加コマンドサポート（Q, S, T, H, V, A）
2. transform属性の実装
3. より多くのスタイル属性のサポート
4. パフォーマンス最適化
5. エラーハンドリングの強化
6. 形状生成機能（ShapeGenerator）の設計と実装
