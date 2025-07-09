#!/usr/bin/env python3
"""
Phase 6-5: 完全検証実行スクリプト
MCP Drone Control System の全機能・品質・セキュリティを包括的に検証

このスクリプトは以下のテストツールを統合実行し、最終的な品質レポートを生成します:
1. 包括的テスト・検証スイート (test_phase6_5_comprehensive.py)
2. API仕様適合性検証 (api_spec_validator.py)
3. システム品質保証チェック (system_quality_checker.py)

最終的に、システムの本番環境展開準備状況を総合評価します。
"""

import asyncio
import json
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import importlib.util


@dataclass
class VerificationResult:
    """検証結果"""
    tool_name: str
    success: bool
    exit_code: int
    execution_time: float
    report_file: Optional[str] = None
    summary: Dict[str, Any] = None
    error_message: Optional[str] = None


@dataclass
class FinalAssessment:
    """最終評価"""
    overall_grade: str  # "A", "B", "C", "D", "F"
    overall_score: float  # 0-100
    production_ready: bool
    critical_issues: List[str]
    recommendations: List[str]
    verification_results: List[VerificationResult]
    total_execution_time: float


class Phase6CompleteVerificationRunner:
    """Phase 6-5 完全検証実行ツール"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.verification_results = []
        
        # 各検証ツールの情報
        self.verification_tools = [
            {
                "name": "包括的テスト・検証スイート",
                "script": "test_phase6_5_comprehensive.py",
                "description": "全システムコンポーネントの統合テスト・品質保証"
            },
            {
                "name": "API仕様適合性検証",
                "script": "api_spec_validator.py", 
                "description": "OpenAPI仕様との適合性検証"
            },
            {
                "name": "システム品質保証チェック",
                "script": "system_quality_checker.py",
                "description": "パフォーマンス・セキュリティ・可用性の品質評価"
            }
        ]
        
        # 本番展開基準
        self.production_criteria = {
            "min_test_success_rate": 95.0,
            "min_api_compliance_rate": 90.0,
            "min_quality_score": 80.0,
            "max_critical_issues": 0,
            "max_high_issues": 2
        }
    
    async def run_complete_verification(self) -> FinalAssessment:
        """完全検証の実行"""
        print("🚀 Phase 6-5: MCP Drone Control System 完全検証開始")
        print("=" * 90)
        print("本システムの本番環境展開準備状況を包括的に評価します")
        print("=" * 90)
        
        start_time = time.time()
        
        # システム前提条件チェック
        await self._check_prerequisites()
        
        # 各検証ツールの実行
        for tool_info in self.verification_tools:
            print(f"\n📊 {tool_info['name']} 実行中...")
            print(f"    {tool_info['description']}")
            print("-" * 70)
            
            result = await self._run_verification_tool(tool_info)
            self.verification_results.append(result)
            
            # 結果サマリー表示
            self._print_tool_result_summary(result)
        
        # 最終評価生成
        total_time = time.time() - start_time
        final_assessment = self._generate_final_assessment(total_time)
        
        # 最終レポート表示
        self._print_final_assessment(final_assessment)
        
        # 統合レポート出力
        await self._generate_integrated_report(final_assessment)
        
        return final_assessment
    
    async def _check_prerequisites(self):
        """前提条件チェック"""
        print("\n🔍 システム前提条件チェック...")
        
        # 必要なファイルの存在確認
        required_files = [
            "test_phase6_5_comprehensive.py",
            "api_spec_validator.py",
            "system_quality_checker.py",
            "shared/api-specs/mcp-api.yaml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ 必要なファイルが不足しています:")
            for file in missing_files:
                print(f"   • {file}")
            print("\n検証を中止します。")
            sys.exit(1)
        else:
            print("✅ 必要なファイル: すべて存在確認")
        
        # Python依存関係チェック
        required_packages = ["aiohttp", "pyyaml", "jsonschema", "psutil"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️ 不足パッケージ:")
            for package in missing_packages:
                print(f"   • {package}")
            print("   以下のコマンドでインストールしてください:")
            print(f"   pip install {' '.join(missing_packages)}")
        else:
            print("✅ Python依存関係: すべて満足")
        
        print("✅ 前提条件チェック完了")
    
    async def _run_verification_tool(self, tool_info: Dict[str, str]) -> VerificationResult:
        """個別検証ツールの実行"""
        start_time = time.time()
        script_path = self.project_root / tool_info["script"]
        
        try:
            # サブプロセスで検証ツールを実行
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            # 実行結果の解析
            success = process.returncode == 0
            
            # 出力の表示
            if stdout:
                print(stdout.decode('utf-8'))
            if stderr and not success:
                print("エラー出力:", stderr.decode('utf-8'))
            
            # レポートファイルの確認
            report_file = self._find_report_file(tool_info["script"])
            summary = await self._extract_summary(report_file) if report_file else None
            
            return VerificationResult(
                tool_name=tool_info["name"],
                success=success,
                exit_code=process.returncode,
                execution_time=execution_time,
                report_file=report_file,
                summary=summary,
                error_message=stderr.decode('utf-8') if stderr else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return VerificationResult(
                tool_name=tool_info["name"],
                success=False,
                exit_code=-1,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _find_report_file(self, script_name: str) -> Optional[str]:
        """レポートファイルの検索"""
        # スクリプト名に基づいてレポートファイル名を推測
        report_mappings = {
            "test_phase6_5_comprehensive.py": "phase6_5_test_report.json",
            "api_spec_validator.py": "api_compliance_report.json",
            "system_quality_checker.py": "system_quality_report.json"
        }
        
        report_file = report_mappings.get(script_name)
        if report_file and (self.project_root / report_file).exists():
            return report_file
        return None
    
    async def _extract_summary(self, report_file: str) -> Optional[Dict[str, Any]]:
        """レポートファイルからサマリー抽出"""
        try:
            with open(self.project_root / report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ファイルタイプに応じてサマリー抽出
            if "test_report" in data:
                return {
                    "type": "comprehensive_test",
                    "success_rate": data["test_report"]["success_rate"],
                    "total_tests": data["test_report"]["total_tests"],
                    "critical_issues": len(data["test_report"]["critical_issues"])
                }
            elif "api_compliance_report" in data:
                return {
                    "type": "api_compliance",
                    "compliance_rate": data["api_compliance_report"]["compliance_rate"],
                    "total_endpoints": data["api_compliance_report"]["total_endpoints"],
                    "issues": len(data["api_compliance_report"]["issues"])
                }
            elif "quality_report" in data:
                return {
                    "type": "quality_assessment",
                    "overall_score": data["quality_report"]["overall_score"],
                    "critical_issues": len([i for i in data["quality_report"]["issues"] if i["severity"] == "CRITICAL"])
                }
        except Exception as e:
            print(f"レポート解析エラー ({report_file}): {str(e)}")
        
        return None
    
    def _print_tool_result_summary(self, result: VerificationResult):
        """ツール実行結果サマリー表示"""
        status = "✅ 成功" if result.success else "❌ 失敗"
        print(f"\n📊 {result.tool_name} 実行結果:")
        print(f"   {status} (終了コード: {result.exit_code}, 実行時間: {result.execution_time:.2f}秒)")
        
        if result.summary:
            if result.summary["type"] == "comprehensive_test":
                print(f"   🎯 テスト成功率: {result.summary['success_rate']:.1f}%")
                print(f"   📊 総テスト数: {result.summary['total_tests']}")
                if result.summary['critical_issues'] > 0:
                    print(f"   🚨 重大問題: {result.summary['critical_issues']}件")
            elif result.summary["type"] == "api_compliance":
                print(f"   📋 API適合率: {result.summary['compliance_rate']:.1f}%")
                print(f"   🌐 総エンドポイント: {result.summary['total_endpoints']}")
                if result.summary['issues'] > 0:
                    print(f"   ⚠️ 適合性問題: {result.summary['issues']}件")
            elif result.summary["type"] == "quality_assessment":
                print(f"   🎯 品質スコア: {result.summary['overall_score']:.1f}/100")
                if result.summary['critical_issues'] > 0:
                    print(f"   🚨 重大品質問題: {result.summary['critical_issues']}件")
        
        if result.error_message and not result.success:
            print(f"   ❌ エラー: {result.error_message[:100]}...")
    
    def _generate_final_assessment(self, total_time: float) -> FinalAssessment:
        """最終評価生成"""
        # 各検証結果から数値を抽出
        test_success_rate = 0.0
        api_compliance_rate = 0.0
        quality_score = 0.0
        critical_issues = []
        recommendations = []
        
        for result in self.verification_results:
            if result.summary:
                if result.summary["type"] == "comprehensive_test":
                    test_success_rate = result.summary["success_rate"]
                    if result.summary["critical_issues"] > 0:
                        critical_issues.append(f"テストで{result.summary['critical_issues']}件の重大問題を検出")
                elif result.summary["type"] == "api_compliance":
                    api_compliance_rate = result.summary["compliance_rate"]
                    if result.summary["compliance_rate"] < 95:
                        critical_issues.append(f"API適合率が{result.summary['compliance_rate']:.1f}%で基準を下回る")
                elif result.summary["type"] == "quality_assessment":
                    quality_score = result.summary["overall_score"]
                    if result.summary["critical_issues"] > 0:
                        critical_issues.append(f"品質評価で{result.summary['critical_issues']}件の重大問題を検出")
        
        # 総合スコア計算
        weights = {
            "test_success": 0.4,
            "api_compliance": 0.3,
            "quality_score": 0.3
        }
        
        overall_score = (
            test_success_rate * weights["test_success"] +
            api_compliance_rate * weights["api_compliance"] +
            quality_score * weights["quality_score"]
        )
        
        # グレード決定
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        # 本番環境準備状況判定
        production_ready = (
            test_success_rate >= self.production_criteria["min_test_success_rate"] and
            api_compliance_rate >= self.production_criteria["min_api_compliance_rate"] and
            quality_score >= self.production_criteria["min_quality_score"] and
            len(critical_issues) <= self.production_criteria["max_critical_issues"]
        )
        
        # 推奨事項生成
        if not production_ready:
            recommendations.append("本番環境展開前に重大問題の解決が必要です")
        
        if test_success_rate < 95:
            recommendations.append("テスト成功率を95%以上に向上させることを推奨します")
        
        if api_compliance_rate < 95:
            recommendations.append("API仕様適合性を向上させることを推奨します")
        
        if quality_score < 85:
            recommendations.append("システム品質の全般的な改善を推奨します")
        
        if not critical_issues:
            recommendations.append("システムは高品質で本番環境に適しています")
        
        return FinalAssessment(
            overall_grade=grade,
            overall_score=overall_score,
            production_ready=production_ready,
            critical_issues=critical_issues,
            recommendations=recommendations,
            verification_results=self.verification_results,
            total_execution_time=total_time
        )
    
    def _print_final_assessment(self, assessment: FinalAssessment):
        """最終評価レポート表示"""
        print("\n" + "=" * 90)
        print("🏆 Phase 6-5: MCP Drone Control System 最終評価レポート")
        print("=" * 90)
        
        # 総合評価
        grade_colors = {
            "A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "⚫"
        }
        grade_icon = grade_colors.get(assessment.overall_grade, "⚪")
        
        print(f"\n📊 総合評価:")
        print(f"   {grade_icon} グレード: {assessment.overall_grade}")
        print(f"   📈 総合スコア: {assessment.overall_score:.1f}/100")
        print(f"   ⏱️ 総検証時間: {assessment.total_execution_time:.2f}秒")
        
        # 本番環境準備状況
        print(f"\n🚀 本番環境展開準備状況:")
        if assessment.production_ready:
            print("   ✅ 本番環境展開準備完了")
        else:
            print("   ❌ 本番環境展開準備未完了")
        
        # 検証結果サマリー
        print(f"\n📋 検証結果サマリー:")
        for result in assessment.verification_results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.tool_name}: {result.execution_time:.2f}秒")
        
        # 重大問題
        if assessment.critical_issues:
            print(f"\n🚨 重大問題 ({len(assessment.critical_issues)}件):")
            for issue in assessment.critical_issues:
                print(f"   🚨 {issue}")
        
        # 推奨事項
        if assessment.recommendations:
            print(f"\n💡 推奨事項:")
            for rec in assessment.recommendations:
                print(f"   💡 {rec}")
        
        # 最終判定
        print(f"\n🎯 最終判定:")
        if assessment.overall_grade == "A":
            print("   🟢 優秀 - システムは非常に高品質で本番環境に最適です")
        elif assessment.overall_grade == "B":
            print("   🟡 良好 - システムは良好な品質で本番環境に適しています")
        elif assessment.overall_grade == "C":
            print("   🟠 合格 - 一部改善が必要ですが本番環境展開可能です")
        elif assessment.overall_grade == "D":
            print("   🔴 要改善 - 重要な問題があり改善後の展開を推奨します")
        else:
            print("   ⚫ 不合格 - 重大な問題があり本番環境展開は推奨しません")
        
        print("\n" + "=" * 90)
    
    async def _generate_integrated_report(self, assessment: FinalAssessment):
        """統合レポート生成"""
        # 各検証ツールのレポートを統合
        integrated_data = {
            "phase6_5_final_assessment": {
                "overall_grade": assessment.overall_grade,
                "overall_score": assessment.overall_score,
                "production_ready": assessment.production_ready,
                "critical_issues": assessment.critical_issues,
                "recommendations": assessment.recommendations,
                "total_execution_time": assessment.total_execution_time
            },
            "verification_results": [
                {
                    "tool_name": result.tool_name,
                    "success": result.success,
                    "exit_code": result.exit_code,
                    "execution_time": result.execution_time,
                    "report_file": result.report_file,
                    "summary": result.summary
                }
                for result in assessment.verification_results
            ],
            "detailed_reports": {},
            "timestamp": datetime.now().isoformat(),
            "system": "MCP Drone Control System",
            "phase": "6-5",
            "verification_scope": "Complete System Verification"
        }
        
        # 詳細レポートを統合
        for result in assessment.verification_results:
            if result.report_file:
                try:
                    with open(self.project_root / result.report_file, 'r', encoding='utf-8') as f:
                        detailed_report = json.load(f)
                    integrated_data["detailed_reports"][result.tool_name] = detailed_report
                except Exception as e:
                    print(f"詳細レポート統合エラー ({result.report_file}): {str(e)}")
        
        # 統合レポートファイル出力
        output_file = "phase6_5_final_verification_report.json"
        with open(self.project_root / output_file, 'w', encoding='utf-8') as f:
            json.dump(integrated_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 統合検証レポートが生成されました: {output_file}")
        
        # エグゼクティブサマリーのテキスト版も生成
        await self._generate_executive_summary(assessment)
    
    async def _generate_executive_summary(self, assessment: FinalAssessment):
        """エグゼクティブサマリー生成"""
        summary_content = f"""# MCP Drone Control System - Phase 6-5 最終検証エグゼクティブサマリー

## 検証概要
実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
検証時間: {assessment.total_execution_time:.2f}秒
検証範囲: システム全体の包括的品質・機能・セキュリティ検証

## 総合評価
- **グレード**: {assessment.overall_grade}
- **総合スコア**: {assessment.overall_score:.1f}/100
- **本番環境準備状況**: {"✅ 準備完了" if assessment.production_ready else "❌ 準備未完了"}

## 検証結果サマリー
"""
        
        for result in assessment.verification_results:
            status = "✅ 成功" if result.success else "❌ 失敗"
            summary_content += f"- **{result.tool_name}**: {status} ({result.execution_time:.2f}秒)\n"
            if result.summary:
                if result.summary["type"] == "comprehensive_test":
                    summary_content += f"  - テスト成功率: {result.summary['success_rate']:.1f}%\n"
                elif result.summary["type"] == "api_compliance":
                    summary_content += f"  - API適合率: {result.summary['compliance_rate']:.1f}%\n"
                elif result.summary["type"] == "quality_assessment":
                    summary_content += f"  - 品質スコア: {result.summary['overall_score']:.1f}/100\n"
        
        if assessment.critical_issues:
            summary_content += f"\n## 重大問題 ({len(assessment.critical_issues)}件)\n"
            for issue in assessment.critical_issues:
                summary_content += f"- {issue}\n"
        
        summary_content += f"\n## 推奨事項\n"
        for rec in assessment.recommendations:
            summary_content += f"- {rec}\n"
        
        summary_content += f"\n## 最終判定\n"
        if assessment.overall_grade == "A":
            summary_content += "**優秀** - システムは非常に高品質で本番環境に最適です。\n"
        elif assessment.overall_grade == "B":
            summary_content += "**良好** - システムは良好な品質で本番環境に適しています。\n"
        elif assessment.overall_grade == "C":
            summary_content += "**合格** - 一部改善が必要ですが本番環境展開可能です。\n"
        elif assessment.overall_grade == "D":
            summary_content += "**要改善** - 重要な問題があり改善後の展開を推奨します。\n"
        else:
            summary_content += "**不合格** - 重大な問題があり本番環境展開は推奨しません。\n"
        
        # ファイル出力
        with open(self.project_root / "PHASE6_5_EXECUTIVE_SUMMARY.md", 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"📄 エグゼクティブサマリーが生成されました: PHASE6_5_EXECUTIVE_SUMMARY.md")


async def main():
    """メイン実行関数"""
    print("🚀 Phase 6-5: MCP Drone Control System 完全検証ツール")
    print("Complete System Verification and Production Readiness Assessment")
    print("=" * 90)
    
    # 完全検証ランナー初期化
    runner = Phase6CompleteVerificationRunner()
    
    # 完全検証実行
    final_assessment = await runner.run_complete_verification()
    
    # 終了コード決定
    if final_assessment.production_ready and final_assessment.overall_grade in ["A", "B"]:
        return 0  # 本番環境準備完了
    elif final_assessment.overall_grade in ["C", "D"]:
        return 1  # 改善必要
    else:
        return 2  # 重大問題


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"\n🏁 Phase 6-5 完全検証完了 (終了コード: {exit_code})")
    sys.exit(exit_code)