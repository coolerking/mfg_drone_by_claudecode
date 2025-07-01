# Phase 3: カメラ画像テストフィクスチャ

このディレクトリには、Tello EDU ダミーシステムのテスト用画像ファイルが格納されています。

## ディレクトリ構造

```
camera_images/
├── README.md                    # このファイル
├── indoor/                      # 室内環境画像
│   ├── living_room_*.jpg        # リビングルーム
│   ├── office_*.jpg             # オフィス環境
│   └── warehouse_*.jpg          # 倉庫環境
├── outdoor/                     # 屋外環境画像
│   ├── park_*.jpg               # 公園環境
│   ├── parking_lot_*.jpg        # 駐車場
│   └── construction_*.jpg       # 建設現場
├── tracking_targets/            # 追跡対象画像
│   ├── person_*.jpg             # 人物追跡用
│   ├── vehicle_*.jpg            # 車両追跡用
│   └── objects_*.jpg            # その他オブジェクト
└── scenarios/                   # 特殊シナリオ画像
    ├── low_light_*.jpg          # 低照度環境
    ├── emergency_*.jpg          # 緊急事態
    └── weather_*.jpg            # 悪天候環境
```

## 画像生成について

これらの画像は以下の方法で生成されます：

### 1. Stability.ai API による自動生成（Phase 0）
- `scripts/setup_dummy_images.py` スクリプトを使用
- GitHub Actions ワークフローから実行可能
- 多様なドローン視点画像を自動生成

### 2. 手動での画像追加
- 必要に応じて手動で画像を追加可能
- JPEGフォーマット推奨（640x480ピクセル）
- ファイル名は用途がわかるように命名

## 使用方法

### VirtualCameraStream での利用
```python
from core.virtual_camera import VirtualCameraStream

# 静的画像モードでの使用
camera = VirtualCameraStream(640, 480, 30)
# この実装では動的生成がメインのため、
# 静的画像モードは将来の拡張機能として予約
```

### テストでの利用
```python
import os
import cv2

# テスト用画像の読み込み
fixtures_dir = "backend/tests/fixtures/camera_images"
indoor_images = os.listdir(os.path.join(fixtures_dir, "indoor"))

for image_file in indoor_images:
    image_path = os.path.join(fixtures_dir, "indoor", image_file)
    test_image = cv2.imread(image_path)
    # テスト処理...
```

## 画像要件

### 技術仕様
- **解像度**: 640x480ピクセル（推奨）
- **フォーマット**: JPEG（.jpg）
- **色空間**: RGB
- **ファイルサイズ**: 1MB以下推奨

### 内容要件
- **ドローン視点**: 高度1-5mからの俯瞰視点
- **追跡対象**: 明確に識別可能なオブジェクト
- **環境多様性**: 様々な照明・天候条件
- **現実性**: 実際のTello EDUで撮影可能な画像品質

## Phase 3統合

Phase 3の物理シミュレーションと組み合わせて使用する際：

1. **ドローンの高度に応じた画像選択**
   - 低高度（0.5-2m）: 詳細な追跡対象画像
   - 中高度（2-5m）: 一般的な環境画像
   - 高高度（5m以上）: 広域環境画像

2. **シミュレーション状況に応じた画像**
   - 通常飛行: indoor/outdoor画像
   - 追跡ミッション: tracking_targets画像
   - 緊急時: scenarios画像

3. **動的生成との連携**
   - 静的画像をベースレイヤーとして使用
   - その上に動的オブジェクトを合成

## 画像生成スクリプト実行方法

### GitHub Actions経由（推奨）
1. GitHub リポジトリの Actions タブを開く
2. "Setup Dummy Images" ワークフローを選択
3. "Run workflow" をクリックして実行

### ローカル実行
```bash
# 環境変数設定
export STABILITY_API_KEY=your_api_key_here

# スクリプト実行
cd backend
python ../scripts/setup_dummy_images.py

# 制限付き実行（テスト用）
python ../scripts/setup_dummy_images.py --limit 5 --dry-run
```

## トラブルシューティング

### よくある問題

1. **画像が生成されない**
   - `STABILITY_API_KEY` 環境変数が正しく設定されているか確認
   - GitHub Secrets の設定を確認

2. **画像品質が低い**
   - プロンプトの調整が必要
   - `scripts/setup_dummy_images.py` の設定を確認

3. **ディスク容量不足**
   - 古い画像ファイルを削除
   - 画像生成数を制限（--limit オプション使用）

### ログ確認
```bash
# デバッグモードで実行
python scripts/setup_dummy_images.py --log-level DEBUG
```

## 貢献方法

1. 新しい画像カテゴリが必要な場合は Issue を作成
2. プロンプトの改善提案は Pull Request で送信
3. 手動で高品質な画像を追加する場合は適切なディレクトリに配置

---

**注意**: このディレクトリの画像は開発・テスト目的のみに使用してください。商用利用前には適切なライセンス確認が必要です。