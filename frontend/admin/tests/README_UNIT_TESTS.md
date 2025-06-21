# 管理用フロントエンドサーバ単体テスト

## 概要

このディレクトリには、MFG Drone管理用フロントエンドサーバ（`main.py`）の包括的な単体テストが含まれています。すべてのテストは独立して実行でき、ドローン実機やバックエンドサーバーなしで動作します。

## テストファイル構成

### 単体テストファイル

- **`test_drone_api_client.py`** - DroneAPIClientクラスの基本機能テスト
  - 初期化、リクエスト処理、ヘルスチェック
  - ドローン接続管理（接続・切断）
  - 基本飛行制御（離陸・着陸・緊急停止）
  - 基本移動制御（6方向移動・回転・フリップ）

- **`test_drone_api_client_advanced.py`** - DroneAPIClientクラスの高度機能テスト
  - 高度移動制御（3D座標移動・曲線飛行・RC制御）
  - カメラ操作（ストリーミング・撮影・録画）
  - センサーデータ取得（バッテリー・高度・温度・姿勢・速度）
  - WiFi・設定管理・カスタムコマンド
  - ミッションパッド機能・物体追跡・モデル管理

- **`test_flask_routes.py`** - Flaskルートハンドラの基本テスト
  - メインページ・ヘルスチェック
  - ドローン制御プロキシ（接続・飛行・移動）
  - 高度移動制御プロキシ（3D移動・曲線飛行・RC制御）

- **`test_flask_routes_advanced.py`** - Flaskルートハンドラの高度テスト
  - センサーデータプロキシ・カメラ制御プロキシ
  - ミッションパッド・物体追跡・モデル管理プロキシ
  - 設定管理プロキシ・エラーハンドリング

### モック・フィクスチャ

- **`mocks/backend_mock.py`** - 完全なバックエンドAPIモック
  - 全APIエンドポイントのシミュレーション
  - リクエスト履歴追跡・検証機能
  - 失敗モード設定・エラーシミュレーション

### 設定・ユーティリティ

- **`test_verification.py`** - テスト構造検証スクリプト
- **`README_UNIT_TESTS.md`** - このファイル（実行ガイド）
- **`../pytest_unit.ini`** - 単体テスト専用pytest設定
- **`../run_unit_tests.py`** - 独立実行スクリプト

## テスト統計

- **総テスト関数数**: 290+ 個
- **テストクラス数**: 27 クラス
- **テストファイル数**: 4 ファイル
- **カバレッジ対象**: `main.py` の全コード

## 実行方法

### 1. 依存関係のインストール

```bash
# フロントエンドディレクトリに移動
cd frontend/admin

# テスト依存関係をインストール
pip install -r test_requirements.txt
```

### 2. 推奨実行方法（独立実行スクリプト）

```bash
# 全単体テスト実行（カバレッジ付き）
python run_unit_tests.py

# 特定のテストタイプのみ実行
python run_unit_tests.py --type api_client    # DroneAPIClient のみ
python run_unit_tests.py --type flask_routes  # Flask ルートのみ
python run_unit_tests.py --type basic         # 基本機能のみ
python run_unit_tests.py --type advanced      # 高度機能のみ

# カバレッジなしで実行
python run_unit_tests.py --no-coverage

# 静かなモード（出力を抑制）
python run_unit_tests.py --quiet
```

### 3. pytest での直接実行

```bash
# 単体テスト専用設定で実行
pytest -c pytest_unit.ini -v

# カバレッジ付きで実行
pytest -c pytest_unit.ini --cov=main --cov-report=html

# 特定のテストファイルのみ実行
pytest -c pytest_unit.ini tests/test_drone_api_client.py

# 特定のテストクラスのみ実行
pytest -c pytest_unit.ini tests/test_drone_api_client.py::TestDroneAPIClientBasic

# 特定のテスト関数のみ実行
pytest -c pytest_unit.ini tests/test_drone_api_client.py::TestDroneAPIClientBasic::test_initialization
```

### 4. テスト構造の検証

```bash
# テスト構造が正しいかを事前確認
python tests/test_verification.py
```

## 出力レポート

テスト実行後、以下のレポートが生成されます：

- **HTMLテストレポート**: `tests/reports/unit_test_report.html`
- **カバレッジレポート**: `tests/reports/coverage_html/index.html`
- **JSONレポート**: `tests/reports/unit_test_report.json`
- **カバレッジJSON**: `tests/reports/coverage.json`
- **テスト概要**: `tests/reports/test_summary.json`

## テスト設計原則

### 独立性の確保

- ✅ **ドローン実機不要**: 全API呼び出しがモック化
- ✅ **バックエンドサーバー不要**: HTTP通信を完全シミュレーション
- ✅ **ネットワーク接続不要**: 全てローカル実行
- ✅ **外部依存関係なし**: 完全な単体テスト

### 包括的なテストカバレッジ

- ✅ **全パブリック関数をテスト**: 100%関数カバレッジ
- ✅ **正常系・異常系・境界値**: 包括的なテストケース
- ✅ **エラーハンドリング**: 例外処理の完全テスト
- ✅ **パラメータ化テスト**: 効率的な多数値テスト

### テストケースの種類

#### 正常系テスト
- 期待される引数での正常動作
- デフォルト値での動作
- 境界値での動作

#### 異常系テスト
- 範囲外の引数値
- 不正な引数タイプ
- 必須パラメータの欠如

#### エラーハンドリングテスト
- ネットワークエラー
- タイムアウト
- HTTPエラーレスポンス
- バックエンドサービス停止

## トラブルシューティング

### よくある問題

1. **ImportError**: `main` モジュールが見つからない
   ```bash
   # 解決方法：フロントエンドディレクトリで実行
   cd frontend/admin
   python run_unit_tests.py
   ```

2. **ModuleNotFoundError**: テスト依存関係が不足
   ```bash
   # 解決方法：依存関係をインストール
   pip install -r test_requirements.txt
   ```

3. **テストが見つからない**
   ```bash
   # 解決方法：pytest設定ファイルを指定
   pytest -c pytest_unit.ini
   ```

4. **カバレッジが低い**
   ```bash
   # 解決方法：除外設定を確認・追加テストを作成
   pytest -c pytest_unit.ini --cov=main --cov-report=term-missing
   ```

### デバッグ方法

1. **テスト構造の確認**
   ```bash
   python tests/test_verification.py
   ```

2. **個別テストの実行**
   ```bash
   pytest -c pytest_unit.ini -v -s tests/test_drone_api_client.py::TestDroneAPIClientBasic::test_initialization
   ```

3. **詳細ログの有効化**
   ```bash
   pytest -c pytest_unit.ini --log-cli-level=DEBUG
   ```

## 継続的改善

### カバレッジ向上

- 現在のカバレッジレポートを確認
- 未テストの分岐・関数を特定
- 必要に応じて追加テストケースを作成

### テストの追加

1. 新しい機能追加時は対応するテストも追加
2. バグ修正時は再現テストケースを追加
3. パフォーマンステストの検討

### 保守性向上

- テストコードのリファクタリング
- 共通フィクスチャの活用
- テストデータの外部化

## 参考情報

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov使用方法](https://pytest-cov.readthedocs.io/)
- [unittest.mock活用法](https://docs.python.org/3/library/unittest.mock.html)