#!/usr/bin/env python3
"""
MCP ドキュメント検証スクリプト
=====================================

このスクリプトは、MCPドローン制御システムのドキュメントを検証し、
リンクの有効性や統計情報の正確性をチェックします。

使用方法:
    python validate_docs.py
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DocumentValidator:
    """ドキュメント検証クラス"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """全ての検証を実行"""
        print("🔍 MCPドキュメント検証を開始します...")
        
        # 1. ファイル存在チェック
        self._validate_file_existence()
        
        # 2. リンク検証
        self._validate_links()
        
        # 3. 統計情報検証
        self._validate_statistics()
        
        # 4. 結果表示
        self._display_results()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_file_existence(self):
        """ドキュメントファイルの存在確認"""
        print("📁 ファイル存在チェック...")
        
        required_files = [
            "docs/README.md",
            "docs/MCP_PROTOCOL.md",
            "docs/setup.md",
            "docs/command_reference.md",
            "docs/FAQ.md",
            "docs/error_reference.md",
            "docs/SECURITY_SETUP.md",
            "MCP_SETUP.md",
        ]
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                self.errors.append(f"❌ 必須ファイルが見つかりません: {file_path}")
            else:
                print(f"✅ {file_path}")
    
    def _validate_links(self):
        """ドキュメント内のリンク検証"""
        print("🔗 リンク検証...")
        
        # README.mdのリンクチェック
        readme_path = self.base_path / "docs" / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Markdownリンクを抽出
            links = re.findall(r'\[.*?\]\((.*?)\)', content)
            
            for link in links:
                if link.startswith('#'):
                    # アンカーリンクはスキップ
                    continue
                elif link.startswith('http'):
                    # 外部リンクはスキップ
                    continue
                else:
                    # 相対パスリンクをチェック
                    if link.startswith('./'):
                        link_path = self.base_path / "docs" / link[2:]
                    elif link.startswith('../'):
                        link_path = self.base_path / link[3:]
                    else:
                        link_path = self.base_path / "docs" / link
                    
                    if not link_path.exists():
                        self.errors.append(f"❌ リンク先が見つかりません: {link}")
                    else:
                        print(f"✅ リンク確認: {link}")
    
    def _validate_statistics(self):
        """統計情報の検証"""
        print("📊 統計情報検証...")
        
        # ドキュメントファイルの行数カウント
        total_lines = 0
        file_count = 0
        
        doc_files = [
            "docs/README.md",
            "docs/MCP_PROTOCOL.md",
            "docs/setup.md",
            "docs/command_reference.md",
            "docs/FAQ.md",
            "docs/error_reference.md",
            "docs/SECURITY_SETUP.md",
            "MCP_SETUP.md",
        ]
        
        for file_path in doc_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    file_count += 1
                    print(f"📄 {file_path}: {lines}行")
        
        print(f"📊 総計: {file_count}ファイル, {total_lines}行")
        
        # README.mdの統計情報をチェック
        readme_path = self.base_path / "docs" / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 文書数チェック
            doc_count_match = re.search(r'総文書数.*?(\d+)文書', content)
            if doc_count_match:
                stated_count = int(doc_count_match.group(1))
                if stated_count != file_count:
                    self.errors.append(f"❌ 文書数が一致しません: 記載={stated_count}, 実際={file_count}")
                else:
                    print(f"✅ 文書数確認: {file_count}文書")
            
            # 行数チェック
            line_count_match = re.search(r'総行数.*?(\d+(?:,\d+)*)行', content)
            if line_count_match:
                stated_lines = int(line_count_match.group(1).replace(',', ''))
                if stated_lines != total_lines:
                    self.errors.append(f"❌ 行数が一致しません: 記載={stated_lines}, 実際={total_lines}")
                else:
                    print(f"✅ 行数確認: {total_lines}行")
    
    def _display_results(self):
        """検証結果の表示"""
        print("\n" + "="*50)
        print("🎯 検証結果")
        print("="*50)
        
        if self.errors:
            print(f"❌ エラー: {len(self.errors)}件")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"⚠️ 警告: {len(self.warnings)}件")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ 全ての検証が成功しました！")
        elif not self.errors:
            print("✅ 検証完了（警告あり）")
        else:
            print("❌ 検証失敗")

def main():
    """メイン実行関数"""
    validator = DocumentValidator()
    success, errors, warnings = validator.validate_all()
    
    if success:
        print("\n🎉 ドキュメント検証が完了しました！")
        exit(0)
    else:
        print("\n💥 ドキュメント検証でエラーが発生しました。")
        exit(1)

if __name__ == "__main__":
    main()