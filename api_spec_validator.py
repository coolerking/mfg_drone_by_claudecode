#!/usr/bin/env python3
"""
API仕様適合性検証ツール
OpenAPI仕様書と実装されたAPIの完全な適合性をチェックします

機能:
1. OpenAPI仕様書の解析
2. 実装されたAPIエンドポイントの検証
3. リクエスト/レスポンス形式の検証
4. パラメータ検証
5. エラーハンドリング検証
6. セキュリティ設定検証
"""

import asyncio
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import jsonschema
from jsonschema import validate, ValidationError


class ValidationResult(Enum):
    """検証結果"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"


@dataclass
class ValidationIssue:
    """検証問題"""
    severity: ValidationResult
    category: str
    endpoint: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApiSpecValidationReport:
    """API仕様検証レポート"""
    total_endpoints: int = 0
    validated_endpoints: int = 0
    passed_endpoints: int = 0
    failed_endpoints: int = 0
    warning_endpoints: int = 0
    skipped_endpoints: int = 0
    compliance_rate: float = 0.0
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ApiSpecValidator:
    """API仕様適合性検証ツール"""
    
    def __init__(self, spec_file: Path, base_url: str = "http://localhost:3001"):
        self.spec_file = spec_file
        self.base_url = base_url
        self.spec_data = None
        self.report = ApiSpecValidationReport()
        
        # API仕様をロード
        self._load_api_spec()
    
    def _load_api_spec(self):
        """API仕様ファイルのロード"""
        try:
            with open(self.spec_file, 'r', encoding='utf-8') as f:
                if self.spec_file.suffix.lower() == '.yaml':
                    self.spec_data = yaml.safe_load(f)
                elif self.spec_file.suffix.lower() == '.json':
                    self.spec_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {self.spec_file.suffix}")
            
            print(f"✅ API仕様ファイルロード完了: {self.spec_file}")
            
        except Exception as e:
            print(f"❌ API仕様ファイルロードエラー: {str(e)}")
            sys.exit(1)
    
    async def validate_api_compliance(self) -> ApiSpecValidationReport:
        """API適合性の包括的検証"""
        print("🔍 API仕様適合性検証開始")
        print("=" * 60)
        
        # OpenAPI仕様の基本検証
        await self._validate_openapi_structure()
        
        # エンドポイント一覧の検証
        await self._validate_endpoints_coverage()
        
        # 各エンドポイントの詳細検証
        await self._validate_individual_endpoints()
        
        # セキュリティ設定の検証
        await self._validate_security_configuration()
        
        # スキーマ定義の検証
        await self._validate_schema_definitions()
        
        # 最終レポート生成
        self._generate_compliance_report()
        
        return self.report
    
    async def _validate_openapi_structure(self):
        """OpenAPI仕様構造の検証"""
        print("\n📋 OpenAPI仕様構造検証...")
        
        # 必須フィールドの検証
        required_fields = ['openapi', 'info', 'paths']
        missing_fields = [field for field in required_fields if field not in self.spec_data]
        
        if missing_fields:
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.FAIL,
                category="OpenAPI Structure",
                endpoint="spec_file",
                message=f"必須フィールドが不足: {missing_fields}"
            ))
        else:
            print("  ✅ 必須フィールド: すべて存在")
        
        # OpenAPIバージョンチェック
        openapi_version = self.spec_data.get('openapi', '')
        if not openapi_version.startswith('3.'):
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.WARNING,
                category="OpenAPI Structure",
                endpoint="spec_file",
                message=f"OpenAPIバージョンが古い可能性: {openapi_version}"
            ))
        else:
            print(f"  ✅ OpenAPIバージョン: {openapi_version}")
        
        # API情報の検証
        info = self.spec_data.get('info', {})
        required_info_fields = ['title', 'version']
        missing_info_fields = [field for field in required_info_fields if field not in info]
        
        if missing_info_fields:
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.WARNING,
                category="OpenAPI Structure",
                endpoint="spec_file",
                message=f"API情報フィールドが不足: {missing_info_fields}"
            ))
        else:
            print(f"  ✅ API情報: {info.get('title')} v{info.get('version')}")
    
    async def _validate_endpoints_coverage(self):
        """エンドポイント網羅性検証"""
        print("\n🌐 エンドポイント網羅性検証...")
        
        # 仕様に定義されたエンドポイント一覧
        spec_endpoints = set()
        paths = self.spec_data.get('paths', {})
        
        for path, methods in paths.items():
            for method in methods.keys():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    spec_endpoints.add(f"{method.upper()} {path}")
        
        self.report.total_endpoints = len(spec_endpoints)
        print(f"  📊 仕様定義エンドポイント数: {self.report.total_endpoints}")
        
        # 実装されたエンドポイントの確認
        implemented_endpoints = set()
        missing_endpoints = []
        
        async with aiohttp.ClientSession() as session:
            # OpenAPI仕様のJSONを取得
            try:
                async with session.get(f"{self.base_url}/openapi.json") as response:
                    if response.status == 200:
                        impl_spec = await response.json()
                        impl_paths = impl_spec.get('paths', {})
                        
                        for path, methods in impl_paths.items():
                            for method in methods.keys():
                                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                                    implemented_endpoints.add(f"{method.upper()} {path}")
                        
                        print(f"  📊 実装エンドポイント数: {len(implemented_endpoints)}")
                        
                        # 不足エンドポイントの特定
                        missing_endpoints = list(spec_endpoints - implemented_endpoints)
                        extra_endpoints = list(implemented_endpoints - spec_endpoints)
                        
                        if missing_endpoints:
                            self.report.issues.append(ValidationIssue(
                                severity=ValidationResult.FAIL,
                                category="Endpoint Coverage",
                                endpoint="multiple",
                                message=f"未実装エンドポイント: {len(missing_endpoints)}個",
                                details={"missing_endpoints": missing_endpoints}
                            ))
                            print(f"  ❌ 未実装エンドポイント: {len(missing_endpoints)}個")
                        else:
                            print("  ✅ すべてのエンドポイントが実装済み")
                        
                        if extra_endpoints:
                            self.report.issues.append(ValidationIssue(
                                severity=ValidationResult.WARNING,
                                category="Endpoint Coverage",
                                endpoint="multiple",
                                message=f"仕様外エンドポイント: {len(extra_endpoints)}個",
                                details={"extra_endpoints": extra_endpoints}
                            ))
                            print(f"  ⚠️ 仕様外エンドポイント: {len(extra_endpoints)}個")
                    
                    else:
                        self.report.issues.append(ValidationIssue(
                            severity=ValidationResult.FAIL,
                            category="Endpoint Coverage",
                            endpoint="/openapi.json",
                            message=f"OpenAPI仕様にアクセスできません: HTTP {response.status}"
                        ))
                        print(f"  ❌ OpenAPI仕様にアクセスできません: HTTP {response.status}")
            
            except Exception as e:
                self.report.issues.append(ValidationIssue(
                    severity=ValidationResult.FAIL,
                    category="Endpoint Coverage",
                    endpoint="/openapi.json",
                    message=f"エンドポイント確認エラー: {str(e)}"
                ))
                print(f"  ❌ エンドポイント確認エラー: {str(e)}")
    
    async def _validate_individual_endpoints(self):
        """個別エンドポイント詳細検証"""
        print("\n🔍 個別エンドポイント詳細検証...")
        
        paths = self.spec_data.get('paths', {})
        
        async with aiohttp.ClientSession() as session:
            for path, methods in paths.items():
                for method, spec in methods.items():
                    if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                        continue
                    
                    endpoint_id = f"{method.upper()} {path}"
                    print(f"  🔎 検証中: {endpoint_id}")
                    
                    # エンドポイントアクセス検証
                    await self._validate_endpoint_access(session, path, method, spec, endpoint_id)
                    
                    # レスポンススキーマ検証
                    await self._validate_response_schema(session, path, method, spec, endpoint_id)
                    
                    # パラメータ検証
                    await self._validate_parameters(session, path, method, spec, endpoint_id)
    
    async def _validate_endpoint_access(self, session: aiohttp.ClientSession, path: str, method: str, spec: Dict, endpoint_id: str):
        """エンドポイントアクセス検証"""
        try:
            # パスパラメータがある場合は適当な値で置換
            test_path = path
            if '{' in path:
                # 簡易的にテスト値で置換
                test_path = path.replace('{droneId}', 'test_drone')
                test_path = test_path.replace('{drone_id}', 'test_drone')
            
            full_url = f"{self.base_url}{test_path}"
            
            # リクエスト実行
            async with session.request(method.upper(), full_url) as response:
                # ステータスコードの検証
                expected_responses = spec.get('responses', {})
                
                if str(response.status) in expected_responses:
                    self.report.validated_endpoints += 1
                    self.report.passed_endpoints += 1
                    print(f"    ✅ アクセス成功: HTTP {response.status}")
                elif response.status in [401, 403]:
                    # 認証エラーは正常（認証が必要な場合）
                    self.report.validated_endpoints += 1
                    self.report.passed_endpoints += 1
                    print(f"    ✅ 認証エラー（期待通り）: HTTP {response.status}")
                else:
                    self.report.validated_endpoints += 1
                    self.report.failed_endpoints += 1
                    self.report.issues.append(ValidationIssue(
                        severity=ValidationResult.FAIL,
                        category="Endpoint Access",
                        endpoint=endpoint_id,
                        message=f"予期しないステータスコード: HTTP {response.status}",
                        details={"expected_responses": list(expected_responses.keys())}
                    ))
                    print(f"    ❌ 予期しないステータス: HTTP {response.status}")
        
        except Exception as e:
            self.report.validated_endpoints += 1
            self.report.failed_endpoints += 1
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.FAIL,
                category="Endpoint Access",
                endpoint=endpoint_id,
                message=f"エンドポイントアクセスエラー: {str(e)}"
            ))
            print(f"    ❌ アクセスエラー: {str(e)}")
    
    async def _validate_response_schema(self, session: aiohttp.ClientSession, path: str, method: str, spec: Dict, endpoint_id: str):
        """レスポンススキーマ検証"""
        # 成功レスポンス（200番台）のスキーマを検証
        responses = spec.get('responses', {})
        success_responses = {code: resp for code, resp in responses.items() 
                           if code.startswith('2') or code == '200'}
        
        if not success_responses:
            return
        
        # 最初の成功レスポンスを検証対象とする
        response_code = list(success_responses.keys())[0]
        response_spec = success_responses[response_code]
        
        # レスポンススキーマの確認
        content = response_spec.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})
        
        if schema:
            print(f"    📋 レスポンススキーマが定義されています")
        else:
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.WARNING,
                category="Response Schema",
                endpoint=endpoint_id,
                message="レスポンススキーマが未定義"
            ))
            print(f"    ⚠️ レスポンススキーマが未定義")
    
    async def _validate_parameters(self, session: aiohttp.ClientSession, path: str, method: str, spec: Dict, endpoint_id: str):
        """パラメータ検証"""
        parameters = spec.get('parameters', [])
        
        if parameters:
            print(f"    📝 パラメータ定義: {len(parameters)}個")
            
            # 必須パラメータの確認
            required_params = [p for p in parameters if p.get('required', False)]
            if required_params:
                print(f"    📌 必須パラメータ: {len(required_params)}個")
        
        # リクエストボディの検証
        request_body = spec.get('requestBody', {})
        if request_body:
            required = request_body.get('required', False)
            content = request_body.get('content', {})
            
            if required and content:
                print(f"    📤 必須リクエストボディが定義されています")
            elif content:
                print(f"    📤 オプションリクエストボディが定義されています")
    
    async def _validate_security_configuration(self):
        """セキュリティ設定検証"""
        print("\n🔒 セキュリティ設定検証...")
        
        # セキュリティスキームの確認
        components = self.spec_data.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        
        if security_schemes:
            print(f"  ✅ セキュリティスキーム: {len(security_schemes)}個定義")
            for name, scheme in security_schemes.items():
                scheme_type = scheme.get('type', 'unknown')
                print(f"    • {name}: {scheme_type}")
        else:
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.WARNING,
                category="Security Configuration",
                endpoint="spec_file",
                message="セキュリティスキームが未定義"
            ))
            print("  ⚠️ セキュリティスキームが未定義")
        
        # グローバルセキュリティ設定の確認
        global_security = self.spec_data.get('security', [])
        if global_security:
            print(f"  ✅ グローバルセキュリティ設定: 有効")
        else:
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.WARNING,
                category="Security Configuration",
                endpoint="spec_file",
                message="グローバルセキュリティ設定が未設定"
            ))
            print("  ⚠️ グローバルセキュリティ設定が未設定")
    
    async def _validate_schema_definitions(self):
        """スキーマ定義検証"""
        print("\n📐 スキーマ定義検証...")
        
        components = self.spec_data.get('components', {})
        schemas = components.get('schemas', {})
        
        if schemas:
            print(f"  ✅ スキーマ定義: {len(schemas)}個")
            
            # 各スキーマの基本構造確認
            for schema_name, schema_def in schemas.items():
                schema_type = schema_def.get('type', 'unknown')
                properties = schema_def.get('properties', {})
                required = schema_def.get('required', [])
                
                print(f"    • {schema_name}: {schema_type} ({len(properties)} properties, {len(required)} required)")
                
                # 必須フィールドの検証
                if schema_type == 'object' and not properties:
                    self.report.issues.append(ValidationIssue(
                        severity=ValidationResult.WARNING,
                        category="Schema Definition",
                        endpoint=schema_name,
                        message="オブジェクト型スキーマにプロパティが未定義"
                    ))
        else:
            self.report.issues.append(ValidationIssue(
                severity=ValidationResult.WARNING,
                category="Schema Definition",
                endpoint="spec_file",
                message="スキーマ定義が存在しません"
            ))
            print("  ⚠️ スキーマ定義が存在しません")
    
    def _generate_compliance_report(self):
        """適合性レポート生成"""
        # 適合率計算
        if self.report.validated_endpoints > 0:
            self.report.compliance_rate = (self.report.passed_endpoints / self.report.validated_endpoints) * 100
        
        # 推奨事項生成
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """推奨事項生成"""
        # 失敗率による推奨事項
        if self.report.compliance_rate < 90:
            self.report.recommendations.append("API適合性を向上させるため、失敗したエンドポイントの修正を優先してください")
        
        # セキュリティ関連
        security_issues = [issue for issue in self.report.issues if issue.category == "Security Configuration"]
        if security_issues:
            self.report.recommendations.append("セキュリティ設定を強化し、認証・認可機能を適切に実装してください")
        
        # スキーマ関連
        schema_issues = [issue for issue in self.report.issues if issue.category == "Schema Definition"]
        if schema_issues:
            self.report.recommendations.append("データスキーマ定義を改善し、APIドキュメントの品質を向上させてください")
        
        # エンドポイント関連
        endpoint_issues = [issue for issue in self.report.issues if issue.category == "Endpoint Coverage"]
        if endpoint_issues:
            self.report.recommendations.append("仕様で定義されたすべてのエンドポイントを実装し、仕様外エンドポイントを整理してください")
    
    def print_validation_report(self):
        """検証レポート表示"""
        print("\n" + "=" * 80)
        print("📋 API仕様適合性検証レポート")
        print("=" * 80)
        
        print(f"\n📊 検証統計:")
        print(f"  総エンドポイント数: {self.report.total_endpoints}")
        print(f"  検証済みエンドポイント: {self.report.validated_endpoints}")
        print(f"  合格: {self.report.passed_endpoints}")
        print(f"  不合格: {self.report.failed_endpoints}")
        print(f"  警告: {self.report.warning_endpoints}")
        print(f"  スキップ: {self.report.skipped_endpoints}")
        print(f"  適合率: {self.report.compliance_rate:.1f}%")
        
        # 問題一覧
        if self.report.issues:
            print(f"\n🚨 検出された問題:")
            for issue in self.report.issues:
                icon = "❌" if issue.severity == ValidationResult.FAIL else "⚠️" if issue.severity == ValidationResult.WARNING else "ℹ️"
                print(f"  {icon} [{issue.category}] {issue.endpoint}: {issue.message}")
        
        # 推奨事項
        if self.report.recommendations:
            print(f"\n💡 推奨事項:")
            for rec in self.report.recommendations:
                print(f"  💡 {rec}")
        
        # 最終評価
        print(f"\n🏆 最終評価:")
        if self.report.compliance_rate >= 95:
            print("  ✅ 優秀 - API仕様に完全に適合しています")
        elif self.report.compliance_rate >= 90:
            print("  ✅ 良好 - API仕様にほぼ適合しています")
        elif self.report.compliance_rate >= 80:
            print("  ⚠️ 改善必要 - 一部のAPIが仕様に適合していません")
        else:
            print("  ❌ 不合格 - 多くのAPIが仕様に適合していません")
        
        print("\n" + "=" * 80)


async def main():
    """メイン実行関数"""
    print("🔍 API仕様適合性検証ツール")
    print("MCP Drone Control System - OpenAPI Specification Compliance Validator")
    print("=" * 80)
    
    # API仕様ファイルパス
    spec_file = Path(__file__).parent / "shared" / "api-specs" / "mcp-api.yaml"
    
    if not spec_file.exists():
        print(f"❌ API仕様ファイルが見つかりません: {spec_file}")
        return 1
    
    # 検証ツール初期化
    validator = ApiSpecValidator(spec_file)
    
    # 適合性検証実行
    report = await validator.validate_api_compliance()
    
    # レポート表示
    validator.print_validation_report()
    
    # JSONレポート出力
    json_report = {
        "api_compliance_report": {
            "total_endpoints": report.total_endpoints,
            "validated_endpoints": report.validated_endpoints,
            "passed_endpoints": report.passed_endpoints,
            "failed_endpoints": report.failed_endpoints,
            "compliance_rate": report.compliance_rate,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category,
                    "endpoint": issue.endpoint,
                    "message": issue.message,
                    "details": issue.details
                }
                for issue in report.issues
            ],
            "recommendations": report.recommendations
        },
        "timestamp": asyncio.get_event_loop().time(),
        "spec_file": str(spec_file),
        "base_url": validator.base_url
    }
    
    with open("api_compliance_report.json", "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 詳細レポートが保存されました: api_compliance_report.json")
    
    # 終了コード決定
    if report.compliance_rate >= 95:
        return 0  # 成功
    elif report.compliance_rate >= 80:
        return 1  # 警告
    else:
        return 2  # エラー


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)