# Phase 1: Unit Tests - Development Environment Plan

## 概要
実機ドローンなし、Raspberry Piではない開発環境内で実施。
パブリックな関数ごとの引数戻り値アサーション、エラー発生時の挙動、引数の境界値超前後と中央値の挙動が想定内かどうか。

## 環境設定
- 実行環境: Windows/Mac/Linux 開発環境
- Python: 3.11+
- ドローン: TelloStub (モック)
- ネットワーク: ローカル環境のみ

## テスト対象関数レベル分析

### 1. **core function単体テスト - services/drone_service.py**

#### 新規テストファイル: `test_drone_service_units.py`

```python
"""
DroneServiceクラスの全パブリック関数単体テスト
引数の境界値、戻り値、エラーハンドリングを徹底検証
"""

class TestDroneServiceUnits:
    
    # 接続系関数
    def test_connect_function_boundary_values(self):
        """connect()関数 - 境界値・戻り値テスト"""
        # 正常系: 初回接続
        # 異常系: 既接続状態での再接続
        # エラー系: 接続失敗時の例外処理
        # 戻り値検証: Dict[str, Any]形式
        
    def test_disconnect_function_boundary_values(self):
        """disconnect()関数 - 境界値・戻り値テスト"""
        # 正常系: 接続済み状態からの切断
        # 異常系: 未接続状態での切断試行
        # エラー系: 切断処理中の例外
        
    # 飛行制御系関数
    def test_takeoff_function_boundary_values(self):
        """takeoff()関数 - 境界値・戻り値テスト"""
        # 正常系: 接続済み・着陸状態からの離陸
        # 異常系: 未接続状態・既飛行状態での離陸
        # 境界値: バッテリー下限値での離陸
        
    def test_land_function_boundary_values(self):
        """land()関数 - 境界値・戻り値テスト"""
        # 正常系: 飛行状態からの着陸
        # 異常系: 未飛行状態・未接続状態での着陸
        
    def test_emergency_function_boundary_values(self):
        """emergency()関数 - 境界値・戻り値テスト"""
        # 正常系: 緊急停止実行
        # 全状態からの緊急停止対応確認
        
    # 移動制御系関数
    def test_move_function_boundary_values(self):
        """move()関数群 - 境界値・戻り値テスト"""
        # 各方向の移動距離境界値 (20-500cm)
        # 無効な移動距離での例外処理
        # 未飛行状態での移動試行
        # 戻り値の成功/失敗判定
        
    def test_rotate_function_boundary_values(self):
        """rotate()関数群 - 境界値・戻り値テスト"""
        # 回転角度境界値 (1-360度)
        # 無効角度での例外処理
        # 未飛行状態での回転試行
        
    # センサー系関数
    def test_get_battery_function_boundary_values(self):
        """get_battery()関数 - 境界値・戻り値テスト"""
        # 正常系: バッテリー残量取得 (0-100%)
        # 異常系: 未接続状態での取得試行
        # 戻り値型検証: int
        
    def test_get_sensors_function_boundary_values(self):
        """各種センサー取得関数 - 境界値・戻り値テスト"""
        # get_height(), get_speed(), get_position()等
        # センサー値の型・範囲検証
        # 未接続時のエラーハンドリング
        
    # カメラ系関数
    def test_camera_functions_boundary_values(self):
        """カメラ関連関数 - 境界値・戻り値テスト"""
        # start_camera_stream(), stop_camera_stream()
        # get_camera_frame(), capture_photo()
        # ストリーミング状態管理
        # 画像データの型・形式検証
```

### 2. **アプリケーション層単体テスト**

#### 新規テストファイル: `test_main_units.py`

```python
"""
main.pyアプリケーション初期化・設定の単体テスト
"""

class TestMainApplicationUnits:
    
    def test_fastapi_app_creation_boundary_values(self):
        """FastAPIアプリ作成 - 設定値境界テスト"""
        # title, description, version設定検証
        # openapi_url, docs_url, redoc_url設定検証
        
    def test_cors_middleware_configuration_boundary_values(self):
        """CORSミドルウェア設定 - 境界値テスト"""
        # allow_origins設定検証
        # allow_methods, allow_headers設定検証
        # credentials設定検証
        
    def test_router_inclusion_boundary_values(self):
        """Router登録 - 境界値テスト"""
        # 全10個のRouter登録検証
        # Router重複登録時の挙動
        # 無効Router追加時のエラー処理
        
    def test_root_health_endpoints_boundary_values(self):
        """ルート・ヘルスエンドポイント - 戻り値テスト"""
        # /エンドポイント戻り値検証
        # /healthエンドポイント戻り値検証
        # レスポンス形式・型検証
```

#### 新規テストファイル: `test_dependencies_units.py`

```python
"""
dependencies.py依存性注入の単体テスト
"""

class TestDependenciesUnits:
    
    def test_get_drone_service_boundary_values(self):
        """get_drone_service()関数 - 境界値・戻り値テスト"""
        # シングルトン動作検証
        # 複数回呼び出し時の同一インスタンス確認
        # 戻り値型検証: DroneService
        
    def test_lru_cache_behavior_boundary_values(self):
        """@lru_cache()動作 - 境界値テスト"""
        # キャッシュ機能有効性確認
        # メモリ使用量検証
        # キャッシュクリア動作確認
        
    def test_dependency_annotation_boundary_values(self):
        """DroneServiceDep型注釈 - 戻り値テスト"""
        # Annotated型の正常動作確認
        # FastAPI Depends()統合確認
```

### 3. **モデル層単体テスト**

#### 新規テストファイル: `test_models_units.py`

```python
"""
models/requests.py, models/responses.pyのデータモデル単体テスト
"""

class TestRequestModelsUnits:
    
    def test_request_model_validation_boundary_values(self):
        """リクエストモデル - 境界値・バリデーションテスト"""
        # 移動距離: 20-500cm境界値
        # 回転角度: 1-360度境界値
        # 速度設定: 10-100cm/s境界値
        # 無効値でのValidationError発生確認
        
class TestResponseModelsUnits:
    
    def test_response_model_serialization_boundary_values(self):
        """レスポンスモデル - 境界値・シリアライゼーションテスト"""
        # StatusResponse, ErrorResponse形式検証
        # センサーデータ型・範囲検証
        # JSON変換正常性確認
```

## テスト実行戦略

### 境界値テスト戦略
```python
# 例: 移動距離境界値テスト
def test_move_distance_boundaries():
    """移動距離境界値テスト"""
    # 下限値直前 (19cm) - エラー期待
    # 下限値 (20cm) - 成功期待
    # 中央値 (260cm) - 成功期待
    # 上限値 (500cm) - 成功期待  
    # 上限値直後 (501cm) - エラー期待
```

### エラーハンドリングテスト戦略
```python
# 例: 例外処理テスト
def test_function_error_handling():
    """関数エラーハンドリングテスト"""
    # 予期される例外の適切なキャッチ
    # エラーメッセージの内容・形式検証
    # エラー時の状態復旧確認
```

### 戻り値アサーション戦略
```python
# 例: 戻り値検証テスト
def test_function_return_values():
    """関数戻り値検証テスト"""
    # 戻り値の型検証 (Dict, bool, int, etc.)
    # 戻り値の構造検証 (key存在確認)
    # 戻り値の内容検証 (値の妥当性)
```

## 必要な新規テストファイル一覧

1. `test_drone_service_units.py` - DroneService関数単体テスト
2. `test_main_units.py` - main.pyアプリケーション単体テスト
3. `test_dependencies_units.py` - dependencies.py単体テスト
4. `test_models_units.py` - モデル層単体テスト
5. `test_router_units.py` - 各Router関数単体テスト (補完)

## 実行コマンド

```bash
# Phase 1 単体テスト実行
python -m pytest backend/tests/test_*_units.py -v

# カバレッジ付き実行
python -m pytest backend/tests/test_*_units.py --cov=backend --cov-report=html

# 境界値テストのみ実行
python -m pytest backend/tests/test_*_units.py -k "boundary_values" -v
```

## 成功基準

- 全パブリック関数の境界値テスト: 100%カバレッジ
- エラーハンドリングテスト: 全例外パターンカバー
- 戻り値アサーション: 全戻り値型・内容検証
- テスト実行時間: < 30秒
- テスト成功率: 100%