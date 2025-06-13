# テストデータ管理ガイド

## 概要

このディレクトリは、MFG Drone 管理者フロントエンドのモデル訓練機能をテストするためのテストデータ生成・管理システムです。

## 📁 ディレクトリ構造

```
test_data/
├── README.md                    # このファイル
├── generate_test_images.py      # 画像生成スクリプト
├── sample_objects/              # 生成された画像（gitignore対象）
│   ├── README.md               # 生成データの詳細
│   ├── circle/                 # 円形オブジェクト
│   ├── square/                 # 四角形オブジェクト
│   ├── triangle/               # 三角形オブジェクト
│   ├── person/                 # 人物シルエット
│   ├── vehicle/                # 車両形状
│   └── ball/                   # ボール形状
└── test_scenarios.py           # テストシナリオ（実装予定）
```

## 🎯 目的

1. **開発効率化**: 実際の画像データなしでモデル訓練機能のテストが可能
2. **CI/CD対応**: 自動テストでの画像データ依存を解決
3. **デモ・プレゼンテーション**: システムの動作デモに使用
4. **リポジトリサイズ管理**: .gitignoreによりリポジトリに含めない

## 🚀 使用方法

### 1. テスト画像の生成

```bash
# 基本的な生成（各カテゴリ10枚）
cd frontend/admin/test_data
python generate_test_images.py

# 大量生成（各カテゴリ20枚）
python generate_test_images.py --count 20

# カスタム出力ディレクトリ
python generate_test_images.py --output my_test_images
```

### 2. 生成される画像カテゴリ

| カテゴリ | 説明 | 特徴 |
|---------|------|------|
| **circle** | 円形オブジェクト | 様々なサイズ・色・ノイズ |
| **square** | 四角形オブジェクト | 回転・変形・色バリエーション |
| **triangle** | 三角形オブジェクト | 基本的な幾何学形状 |
| **person** | 人物シルエット | 簡略化された人型 |
| **vehicle** | 車両形状 | 車体・窓・車輪を含む基本形状 |
| **ball** | ボール形状 | ハイライト・パターン付き |

### 3. モデル訓練でのテスト手順

1. **画像生成**
   ```bash
   python generate_test_images.py --count 8
   ```

2. **管理者フロントエンドにアクセス**
   - URL: `http://localhost:5001/model/training`

3. **訓練実行**
   - オブジェクト名: `test_circle` など
   - 画像選択: `sample_objects/circle/` から5枚以上
   - 訓練開始ボタンをクリック

4. **結果確認**
   - 訓練進行状況の表示確認
   - WebSocket通信の動作確認
   - エラーハンドリングの確認

## 🔧 高度な使用方法

### カスタム画像生成

`generate_test_images.py` を編集してカスタム画像を生成:

```python
# 新しいカテゴリの追加例
def generate_custom_objects(self, count: int = 10):
    # カスタム画像生成ロジック
    pass
```

### バリデーションテスト

各種エラーケースのテスト:

```bash
# 大きすぎるファイル（10MB超）のテスト
# 4枚以下のファイルのテスト  
# 非画像ファイルのテスト
```

## 📊 生成画像の仕様

- **解像度**: 224x224ピクセル
- **フォーマット**: PNG
- **ファイルサイズ**: 約10-50KB
- **色深度**: RGB 24bit
- **背景**: ランダムなグレー系背景

## 🛡️ セキュリティとプライバシー

- ✅ **自動生成データのみ**: 実際の人物や車両画像は含まない
- ✅ **リポジトリ除外**: .gitignoreで自動除外
- ✅ **一時的な使用**: 開発・テスト目的のみ
- ✅ **削除可能**: いつでも安全に削除可能

## 🔍 トラブルシューティング

### 生成エラーが発生する場合

```bash
# 依存関係の確認
pip install pillow opencv-python numpy

# Python環境の確認
python --version  # Python 3.7以上

# 権限の確認
ls -la test_data/
```

### ディスク容量不足の場合

```bash
# 古いテストデータの削除
rm -rf sample_objects/
python generate_test_images.py --count 5
```

### 生成画像が表示されない場合

- ブラウザのキャッシュクリア
- フロントエンドの再起動
- ファイルパスの確認

## 📈 パフォーマンス

| 生成数 | 実行時間（目安） | ディスク使用量 |
|--------|------------------|----------------|
| 5枚/カテゴリ | ~5秒 | ~1MB |
| 10枚/カテゴリ | ~10秒 | ~2MB |
| 20枚/カテゴリ | ~20秒 | ~4MB |

## 🔄 更新とメンテナンス

### 定期的な再生成

```bash
# 週次での再生成（推奨）
cd frontend/admin/test_data
rm -rf sample_objects/
python generate_test_images.py --count 10
```

### 新しいカテゴリの追加

1. `generate_test_images.py`の`generate_all_categories`に追加
2. 対応する生成関数を実装
3. テスト実行

## 📞 サポート

問題や質問がある場合:

1. **GitHub Issues**: プロジェクトのIssueトラッカーに報告
2. **コードレビュー**: 生成スクリプトの改善提案
3. **ドキュメント**: この README の改善提案

---

**注意**: このテストデータシステムは開発・テスト専用です。本番環境では実際の高品質な画像データを使用してください。