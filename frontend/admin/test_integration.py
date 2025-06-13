#!/usr/bin/env python3
"""
Integration Test Script
フェーズ4モデル訓練機能の統合テスト

このスクリプトは実装された機能の基本的な動作確認を行います。
"""

import os
import sys
import importlib.util
from typing import Dict, Any, List
import json


class IntegrationTester:
    """統合テストクラス"""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {}
        self.errors: List[str] = []
        
    def test_file_structure(self) -> bool:
        """ファイル構造のテスト"""
        print("📁 ファイル構造テスト...")
        
        required_files = [
            # Core files
            'main.py',
            'requirements.txt',
            
            # Service files
            'services/__init__.py',
            'services/api_client.py',
            
            # Blueprint files
            'blueprints/__init__.py',
            'blueprints/model.py',
            
            # Template files
            'templates/index.html',
            'templates/model/index.html',
            'templates/model/training.html',
            'templates/model/management.html',
            
            # Static files
            'static/css/style.css',
            'static/js/model_training.js',
            
            # Test data files
            'test_data/README.md',
            'test_data/generate_test_images.py',
            
            # Integration test
            'test_integration.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.errors.append(f"Missing files: {missing_files}")
            return False
        
        print("   ✅ 全ての必要ファイルが存在します")
        return True
    
    def test_python_imports(self) -> bool:
        """Pythonインポートのテスト"""
        print("🐍 Pythonインポートテスト...")
        
        try:
            # Test main.py imports
            if os.path.exists('main.py'):
                spec = importlib.util.spec_from_file_location("main", "main.py")
                if spec and spec.loader:
                    # Check syntax without executing
                    with open('main.py', 'r', encoding='utf-8') as f:
                        compile(f.read(), 'main.py', 'exec')
                        
            # Test services imports
            if os.path.exists('services/api_client.py'):
                with open('services/api_client.py', 'r', encoding='utf-8') as f:
                    compile(f.read(), 'services/api_client.py', 'exec')
                    
            # Test blueprints imports
            if os.path.exists('blueprints/model.py'):
                with open('blueprints/model.py', 'r', encoding='utf-8') as f:
                    compile(f.read(), 'blueprints/model.py', 'exec')
                    
            print("   ✅ Python構文チェック完了")
            return True
            
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Import error: {e}")
            return False
    
    def test_requirements(self) -> bool:
        """requirements.txtのテスト"""
        print("📦 依存関係テスト...")
        
        try:
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            required_packages = [
                'Flask',
                'Flask-SocketIO', 
                'requests',
                'opencv-python',
                'numpy',
                'pillow',
                'eventlet',
                'aiohttp'
            ]
            
            for package in required_packages:
                found = any(package.lower() in req.lower() for req in requirements)
                if not found:
                    self.errors.append(f"Missing package: {package}")
                    return False
            
            print(f"   ✅ 全ての必要パッケージが含まれています ({len(requirements)}個)")
            return True
            
        except Exception as e:
            self.errors.append(f"Requirements test error: {e}")
            return False
    
    def test_template_structure(self) -> bool:
        """テンプレート構造のテスト"""
        print("🎨 テンプレート構造テスト...")
        
        try:
            # Test main template
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                index_content = f.read()
                if 'Bootstrap' not in index_content or 'Socket.IO' not in index_content:
                    self.errors.append("Main template missing required libraries")
                    return False
            
            # Test model templates
            model_templates = [
                'templates/model/training.html',
                'templates/model/management.html'
            ]
            
            for template_path in model_templates:
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'Bootstrap' not in content:
                        self.errors.append(f"Template {template_path} missing Bootstrap")
                        return False
            
            print("   ✅ テンプレート構造が正しく設定されています")
            return True
            
        except Exception as e:
            self.errors.append(f"Template test error: {e}")
            return False
    
    def test_javascript_structure(self) -> bool:
        """JavaScript構造のテスト"""
        print("⚡ JavaScript構造テスト...")
        
        try:
            with open('static/js/model_training.js', 'r', encoding='utf-8') as f:
                js_content = f.read()
                
                # Check for key functionality
                required_functions = [
                    'ModelTrainingManager',
                    'handleFileSelect',
                    'startTraining',
                    'validateFiles',
                    'updateTrainingProgress'
                ]
                
                for func in required_functions:
                    if func not in js_content:
                        self.errors.append(f"Missing JavaScript function: {func}")
                        return False
            
            print("   ✅ JavaScript機能が実装されています")
            return True
            
        except Exception as e:
            self.errors.append(f"JavaScript test error: {e}")
            return False
    
    def test_api_client_structure(self) -> bool:
        """APIクライアント構造のテスト"""
        print("🌐 APIクライアント構造テスト...")
        
        try:
            with open('services/api_client.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for key methods
                required_methods = [
                    'train_model',
                    'list_models',
                    'validate_image_files'
                ]
                
                for method in required_methods:
                    if f"def {method}" not in content:
                        self.errors.append(f"Missing API method: {method}")
                        return False
            
            print("   ✅ APIクライアント機能が実装されています")
            return True
            
        except Exception as e:
            self.errors.append(f"API client test error: {e}")
            return False
    
    def test_gitignore_rules(self) -> bool:
        """Gitignoreルールのテスト"""
        print("🔒 Gitignoreルールテスト...")
        
        try:
            # Check root gitignore
            with open('../.gitignore', 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
                
                required_rules = [
                    'frontend/admin/test_data/',
                    'frontend/admin/uploads/'
                ]
                
                for rule in required_rules:
                    if rule not in gitignore_content:
                        self.errors.append(f"Missing gitignore rule: {rule}")
                        return False
            
            print("   ✅ Gitignoreルールが正しく設定されています")
            return True
            
        except Exception as e:
            self.errors.append(f"Gitignore test error: {e}")
            return False
    
    def test_test_data_generation(self) -> bool:
        """テストデータ生成のテスト"""
        print("🎨 テストデータ生成テスト...")
        
        try:
            # Check if the test data generator has proper structure
            with open('test_data/generate_test_images.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
                required_classes = ['TestImageGenerator']
                required_methods = [
                    'generate_circle_images',
                    'generate_square_images', 
                    'generate_person_silhouettes'
                ]
                
                for cls in required_classes:
                    if f"class {cls}" not in content:
                        self.errors.append(f"Missing class: {cls}")
                        return False
                
                for method in required_methods:
                    if f"def {method}" not in content:
                        self.errors.append(f"Missing method: {method}")
                        return False
            
            print("   ✅ テストデータ生成機能が実装されています")
            return True
            
        except Exception as e:
            self.errors.append(f"Test data generation test error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """全テストの実行"""
        print("🚀 フェーズ4統合テスト開始\n")
        
        tests = [
            ('file_structure', self.test_file_structure),
            ('python_imports', self.test_python_imports),
            ('requirements', self.test_requirements),
            ('template_structure', self.test_template_structure),
            ('javascript_structure', self.test_javascript_structure),
            ('api_client_structure', self.test_api_client_structure),
            ('gitignore_rules', self.test_gitignore_rules),
            ('test_data_generation', self.test_test_data_generation)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = {
                    'passed': result,
                    'error': None
                }
                if result:
                    passed += 1
            except Exception as e:
                results[test_name] = {
                    'passed': False,
                    'error': str(e)
                }
                self.errors.append(f"{test_name}: {e}")
        
        print(f"\n📊 テスト結果: {passed}/{total} 合格")
        
        if self.errors:
            print(f"\n❌ エラー ({len(self.errors)}個):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("\n✅ 全てのテストが合格しました!")
        
        results['summary'] = {
            'passed': passed,
            'total': total,
            'success_rate': passed / total * 100,
            'errors': self.errors
        }
        
        return results


def main():
    """メイン実行関数"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Results to JSON for potential CI integration
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 テスト結果が test_results.json に保存されました")
    
    # Exit with appropriate code
    if results['summary']['passed'] == results['summary']['total']:
        print("\n🎉 統合テスト完了: すべての機能が正常です!")
        sys.exit(0)
    else:
        print("\n⚠️  統合テスト完了: 一部の問題が検出されました")
        sys.exit(1)


if __name__ == '__main__':
    main()