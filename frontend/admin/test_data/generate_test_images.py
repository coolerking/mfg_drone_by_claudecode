#!/usr/bin/env python3
"""
Test Image Generation Script
テスト用画像データの自動生成スクリプト

このスクリプトは、モデル訓練テスト用の合成画像を生成します。
リポジトリにはコミットされません（.gitignoreで除外）。
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import argparse
from datetime import datetime
from typing import List, Tuple, Dict


class TestImageGenerator:
    """テスト画像生成器"""
    
    def __init__(self, output_dir: str = "sample_objects"):
        self.output_dir = output_dir
        self.image_size = (224, 224)  # 標準的な画像サイズ
        self.colors = [
            (255, 0, 0),    # 赤
            (0, 255, 0),    # 緑
            (0, 0, 255),    # 青
            (255, 255, 0),  # 黄
            (255, 0, 255),  # マゼンタ
            (0, 255, 255),  # シアン
            (128, 128, 128), # グレー
            (255, 165, 0),  # オレンジ
            (128, 0, 128),  # 紫
            (255, 192, 203) # ピンク
        ]
        
        # 背景色のバリエーション
        self.backgrounds = [
            (240, 240, 240), # ライトグレー
            (255, 255, 255), # 白
            (200, 200, 200), # グレー
            (220, 220, 220), # ライトグレー2
            (180, 180, 180), # ダークグレー
        ]
        
        self.setup_output_directory()

    def setup_output_directory(self):
        """出力ディレクトリのセットアップ"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # オブジェクトカテゴリごとのディレクトリ作成
        categories = ['circle', 'square', 'triangle', 'person', 'vehicle', 'ball']
        for category in categories:
            category_dir = os.path.join(self.output_dir, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir)

    def generate_circle_images(self, count: int = 10) -> List[str]:
        """円形オブジェクトの画像生成"""
        generated_files = []
        
        for i in range(count):
            # キャンバス作成
            img = Image.new('RGB', self.image_size, random.choice(self.backgrounds))
            draw = ImageDraw.Draw(img)
            
            # ランダムな円を描画
            center_x = random.randint(50, self.image_size[0] - 50)
            center_y = random.randint(50, self.image_size[1] - 50)
            radius = random.randint(20, 60)
            
            # 円の描画
            color = random.choice(self.colors)
            draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], fill=color, outline=(0, 0, 0), width=2)
            
            # ノイズ追加
            img_array = np.array(img)
            noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
            img_array = np.clip(img_array + noise, 0, 255)
            img = Image.fromarray(img_array)
            
            # 保存
            filename = f"circle_{i+1:03d}.png"
            filepath = os.path.join(self.output_dir, 'circle', filename)
            img.save(filepath)
            generated_files.append(filepath)
            
        return generated_files

    def generate_square_images(self, count: int = 10) -> List[str]:
        """四角形オブジェクトの画像生成"""
        generated_files = []
        
        for i in range(count):
            # キャンバス作成
            img = Image.new('RGB', self.image_size, random.choice(self.backgrounds))
            draw = ImageDraw.Draw(img)
            
            # ランダムな四角形を描画
            size = random.randint(40, 100)
            x1 = random.randint(20, self.image_size[0] - size - 20)
            y1 = random.randint(20, self.image_size[1] - size - 20)
            x2 = x1 + size
            y2 = y1 + size
            
            # 四角形の描画
            color = random.choice(self.colors)
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=(0, 0, 0), width=2)
            
            # 回転を追加
            angle = random.randint(-30, 30)
            img = img.rotate(angle, expand=False, fillcolor=random.choice(self.backgrounds))
            
            # 保存
            filename = f"square_{i+1:03d}.png"
            filepath = os.path.join(self.output_dir, 'square', filename)
            img.save(filepath)
            generated_files.append(filepath)
            
        return generated_files

    def generate_triangle_images(self, count: int = 10) -> List[str]:
        """三角形オブジェクトの画像生成"""
        generated_files = []
        
        for i in range(count):
            # キャンバス作成
            img = Image.new('RGB', self.image_size, random.choice(self.backgrounds))
            draw = ImageDraw.Draw(img)
            
            # ランダムな三角形を描画
            center_x = random.randint(60, self.image_size[0] - 60)
            center_y = random.randint(60, self.image_size[1] - 60)
            size = random.randint(30, 70)
            
            # 三角形の頂点計算
            points = [
                (center_x, center_y - size),  # 上
                (center_x - size, center_y + size),  # 左下
                (center_x + size, center_y + size)   # 右下
            ]
            
            # 三角形の描画
            color = random.choice(self.colors)
            draw.polygon(points, fill=color, outline=(0, 0, 0))
            
            # 保存
            filename = f"triangle_{i+1:03d}.png"
            filepath = os.path.join(self.output_dir, 'triangle', filename)
            img.save(filepath)
            generated_files.append(filepath)
            
        return generated_files

    def generate_person_silhouettes(self, count: int = 10) -> List[str]:
        """人物シルエット画像の生成"""
        generated_files = []
        
        for i in range(count):
            # キャンバス作成
            img = Image.new('RGB', self.image_size, random.choice(self.backgrounds))
            draw = ImageDraw.Draw(img)
            
            # 簡単な人物シルエット描画
            color = random.choice(self.colors)
            center_x = self.image_size[0] // 2
            base_y = self.image_size[1] - 20
            
            # 頭
            head_radius = random.randint(15, 25)
            head_y = base_y - random.randint(120, 150)
            draw.ellipse([
                center_x - head_radius, head_y - head_radius,
                center_x + head_radius, head_y + head_radius
            ], fill=color)
            
            # 体
            body_width = random.randint(20, 35)
            body_height = random.randint(60, 80)
            draw.rectangle([
                center_x - body_width // 2, head_y + head_radius,
                center_x + body_width // 2, head_y + head_radius + body_height
            ], fill=color)
            
            # 腕（簡略化）
            arm_length = random.randint(30, 50)
            arm_y = head_y + head_radius + 20
            draw.line([
                center_x - body_width // 2, arm_y,
                center_x - body_width // 2 - arm_length, arm_y + 20
            ], fill=color, width=8)
            draw.line([
                center_x + body_width // 2, arm_y,
                center_x + body_width // 2 + arm_length, arm_y + 20
            ], fill=color, width=8)
            
            # 脚
            leg_length = random.randint(40, 60)
            leg_y = head_y + head_radius + body_height
            draw.line([
                center_x - 10, leg_y,
                center_x - 15, base_y
            ], fill=color, width=10)
            draw.line([
                center_x + 10, leg_y,
                center_x + 15, base_y
            ], fill=color, width=10)
            
            # ランダムな回転
            angle = random.randint(-15, 15)
            img = img.rotate(angle, expand=False, fillcolor=random.choice(self.backgrounds))
            
            # 保存
            filename = f"person_{i+1:03d}.png"
            filepath = os.path.join(self.output_dir, 'person', filename)
            img.save(filepath)
            generated_files.append(filepath)
            
        return generated_files

    def generate_vehicle_images(self, count: int = 10) -> List[str]:
        """車両画像の生成"""
        generated_files = []
        
        for i in range(count):
            # キャンバス作成
            img = Image.new('RGB', self.image_size, random.choice(self.backgrounds))
            draw = ImageDraw.Draw(img)
            
            # 簡単な車両形状描画
            color = random.choice(self.colors)
            center_x = self.image_size[0] // 2
            center_y = self.image_size[1] // 2
            
            # 車体
            car_width = random.randint(80, 120)
            car_height = random.randint(30, 50)
            draw.rectangle([
                center_x - car_width // 2, center_y - car_height // 2,
                center_x + car_width // 2, center_y + car_height // 2
            ], fill=color, outline=(0, 0, 0), width=2)
            
            # 窓
            window_color = (100, 100, 255)
            window_width = car_width - 20
            window_height = car_height - 20
            draw.rectangle([
                center_x - window_width // 2, center_y - window_height // 2,
                center_x + window_width // 2, center_y + window_height // 2
            ], fill=window_color)
            
            # 車輪
            wheel_radius = random.randint(8, 15)
            wheel_color = (50, 50, 50)
            # 左の車輪
            draw.ellipse([
                center_x - car_width // 2 + 10 - wheel_radius,
                center_y + car_height // 2 - wheel_radius,
                center_x - car_width // 2 + 10 + wheel_radius,
                center_y + car_height // 2 + wheel_radius
            ], fill=wheel_color)
            # 右の車輪
            draw.ellipse([
                center_x + car_width // 2 - 10 - wheel_radius,
                center_y + car_height // 2 - wheel_radius,
                center_x + car_width // 2 - 10 + wheel_radius,
                center_y + car_height // 2 + wheel_radius
            ], fill=wheel_color)
            
            # 保存
            filename = f"vehicle_{i+1:03d}.png"
            filepath = os.path.join(self.output_dir, 'vehicle', filename)
            img.save(filepath)
            generated_files.append(filepath)
            
        return generated_files

    def generate_ball_images(self, count: int = 10) -> List[str]:
        """ボール画像の生成"""
        generated_files = []
        
        for i in range(count):
            # キャンバス作成
            img = Image.new('RGB', self.image_size, random.choice(self.backgrounds))
            draw = ImageDraw.Draw(img)
            
            # ランダムなボールを描画
            center_x = random.randint(50, self.image_size[0] - 50)
            center_y = random.randint(50, self.image_size[1] - 50)
            radius = random.randint(25, 70)
            
            # ボールの基本色
            color = random.choice(self.colors)
            draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], fill=color, outline=(0, 0, 0), width=2)
            
            # ハイライト効果
            highlight_radius = radius // 3
            highlight_x = center_x - radius // 3
            highlight_y = center_y - radius // 3
            highlight_color = tuple(min(255, c + 80) for c in color)
            draw.ellipse([
                highlight_x - highlight_radius // 2,
                highlight_y - highlight_radius // 2,
                highlight_x + highlight_radius // 2,
                highlight_y + highlight_radius // 2
            ], fill=highlight_color)
            
            # パターン追加（一部のボールに）
            if random.random() > 0.5:
                pattern_color = tuple(max(0, c - 50) for c in color)
                # ストライプパターン
                for j in range(3):
                    stripe_y = center_y - radius + (radius * 2 * j // 3)
                    draw.line([
                        center_x - radius, stripe_y,
                        center_x + radius, stripe_y
                    ], fill=pattern_color, width=3)
            
            # 保存
            filename = f"ball_{i+1:03d}.png"
            filepath = os.path.join(self.output_dir, 'ball', filename)
            img.save(filepath)
            generated_files.append(filepath)
            
        return generated_files

    def generate_all_categories(self, count_per_category: int = 10) -> Dict[str, List[str]]:
        """全カテゴリの画像を生成"""
        results = {}
        
        print(f"🎨 テスト画像生成開始 (各カテゴリ {count_per_category}枚)")
        
        # 各カテゴリの生成
        categories = [
            ('circle', self.generate_circle_images),
            ('square', self.generate_square_images),
            ('triangle', self.generate_triangle_images),
            ('person', self.generate_person_silhouettes),
            ('vehicle', self.generate_vehicle_images),
            ('ball', self.generate_ball_images)
        ]
        
        for category_name, generator_func in categories:
            print(f"  📁 {category_name} 画像生成中...")
            files = generator_func(count_per_category)
            results[category_name] = files
            print(f"     ✅ {len(files)}枚生成完了")
        
        return results

    def create_readme(self, results: Dict[str, List[str]]):
        """README文書の作成"""
        readme_path = os.path.join(self.output_dir, "README.md")
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# テスト画像データセット\n\n")
            f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("このディレクトリには、MFG Drone システムのモデル訓練テスト用の合成画像が含まれています。\n\n")
            f.write("## 重要な注意\n\n")
            f.write("- これらのファイルは自動生成されたテストデータです\n")
            f.write("- `.gitignore`でリポジトリから除外されています\n")
            f.write("- 本番環境では実際の画像データを使用してください\n\n")
            f.write("## 生成された画像カテゴリ\n\n")
            
            total_files = 0
            for category, files in results.items():
                f.write(f"### {category}\n")
                f.write(f"- ファイル数: {len(files)}枚\n")
                f.write(f"- ディレクトリ: `{category}/`\n")
                f.write(f"- 説明: {self._get_category_description(category)}\n\n")
                total_files += len(files)
            
            f.write(f"**総ファイル数: {total_files}枚**\n\n")
            f.write("## 使用方法\n\n")
            f.write("1. 管理者フロントエンドの「モデル訓練」ページにアクセス\n")
            f.write("2. 訓練したいオブジェクト名を入力\n")
            f.write("3. 対応するカテゴリから画像を選択してアップロード\n")
            f.write("4. 訓練を開始\n\n")
            f.write("## 再生成\n\n")
            f.write("```bash\n")
            f.write("cd frontend/admin/test_data\n")
            f.write("python generate_test_images.py --count 10\n")
            f.write("```\n")

    def _get_category_description(self, category: str) -> str:
        """カテゴリの説明を取得"""
        descriptions = {
            'circle': '様々なサイズと色の円形オブジェクト',
            'square': '回転や変形を含む四角形オブジェクト', 
            'triangle': '基本的な三角形形状',
            'person': '簡略化された人物シルエット',
            'vehicle': '基本的な車両形状（車体、窓、車輪含む）',
            'ball': 'ハイライトやパターンを含むボール形状'
        }
        return descriptions.get(category, '未定義のカテゴリ')


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='テスト画像生成スクリプト')
    parser.add_argument('--count', type=int, default=10,
                      help='各カテゴリで生成する画像数 (デフォルト: 10)')
    parser.add_argument('--output', type=str, default='sample_objects',
                      help='出力ディレクトリ (デフォルト: sample_objects)')
    
    args = parser.parse_args()
    
    # 生成器の初期化
    generator = TestImageGenerator(args.output)
    
    # 画像生成実行
    results = generator.generate_all_categories(args.count)
    
    # README作成
    generator.create_readme(results)
    
    # 結果表示
    total_files = sum(len(files) for files in results.values())
    print(f"\n🎉 テスト画像生成完了!")
    print(f"   📊 総ファイル数: {total_files}枚")
    print(f"   📁 出力ディレクトリ: {args.output}/")
    print(f"   📄 詳細: {args.output}/README.md")
    print(f"\n🔒 これらのファイルは .gitignore により自動的に除外されます")


if __name__ == '__main__':
    main()