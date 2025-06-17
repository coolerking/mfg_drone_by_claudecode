"""
ヘルスチェックページのPage Object
"""

import json
import requests
from selenium.webdriver.common.by import By
from .base_page import BasePage


class HealthPage(BasePage):
    """ヘルスチェックエンドポイントページ"""
    
    # ページ要素のロケーター
    BODY = (By.TAG_NAME, "body")
    PRE = (By.TAG_NAME, "pre")
    
    def __init__(self, driver, base_url="http://localhost:5001"):
        super().__init__(driver, base_url)
        self.page_path = "/health"
        self.endpoint_url = f"{base_url}/health"
    
    def open(self):
        """ヘルスチェックページを開く"""
        super().open(self.page_path)
        self.wait_for_page_load()
        return self
    
    def get_response_text(self):
        """レスポンステキストを取得"""
        return self.get_text(self.BODY)
    
    def get_json_response(self):
        """JSONレスポンスを解析"""
        response_text = self.get_response_text()
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON: {e}', 'raw_text': response_text}
    
    def validate_json_structure(self):
        """JSONレスポンス構造の妥当性確認"""
        json_data = self.get_json_response()
        
        if 'error' in json_data:
            return {
                'valid': False,
                'error': json_data['error'],
                'raw_response': json_data.get('raw_text', '')
            }
        
        # 期待されるフィールドの確認
        expected_fields = ['status']
        validation_result = {
            'valid': True,
            'has_status_field': 'status' in json_data,
            'status_value': json_data.get('status'),
            'all_expected_fields_present': all(field in json_data for field in expected_fields),
            'response_data': json_data
        }
        
        # ステータス値の妥当性
        if 'status' in json_data:
            validation_result['status_is_healthy'] = json_data['status'] == 'healthy'
        
        return validation_result
    
    def check_api_response_via_requests(self):
        """requests ライブラリ経由でのAPI応答確認"""
        try:
            response = requests.get(self.endpoint_url, timeout=10)
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'headers': dict(response.headers),
                'content_type': response.headers.get('Content-Type', ''),
                'response_time': response.elapsed.total_seconds(),
                'json_data': response.json() if response.headers.get('Content-Type', '').startswith('application/json') else None,
                'text_content': response.text
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
        except json.JSONDecodeError as e:
            return {
                'status_code': response.status_code,
                'success': False,
                'json_error': str(e),
                'text_content': response.text
            }
    
    def validate_response_headers_via_browser(self):
        """ブラウザ経由でのレスポンスヘッダー確認"""
        # JavaScriptでレスポンス情報を取得
        try:
            response_info = self.execute_javascript("""
                return {
                    'url': window.location.href,
                    'contentType': document.contentType,
                    'characterSet': document.characterSet,
                    'readyState': document.readyState
                };
            """)
            return response_info
        except Exception as e:
            return {'error': str(e)}
    
    def check_response_content_type(self):
        """レスポンスのContent-Type確認"""
        # requests経由での確認
        api_response = self.check_api_response_via_requests()
        
        if api_response.get('success'):
            content_type = api_response.get('content_type', '')
            return {
                'content_type': content_type,
                'is_json': content_type.startswith('application/json'),
                'is_valid_content_type': content_type in ['application/json', 'application/json; charset=utf-8']
            }
        else:
            return {
                'error': 'Failed to get response',
                'details': api_response
            }
    
    def perform_performance_test(self):
        """パフォーマンステスト"""
        import time
        
        # 複数回リクエストして平均応答時間を測定
        response_times = []
        success_count = 0
        total_requests = 5
        
        for i in range(total_requests):
            start_time = time.time()
            api_response = self.check_api_response_via_requests()
            end_time = time.time()
            
            if api_response.get('success'):
                success_count += 1
                response_times.append(end_time - start_time)
            
            time.sleep(0.1)  # 短い間隔
        
        if response_times:
            return {
                'success_rate': success_count / total_requests,
                'avg_response_time': sum(response_times) / len(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'total_requests': total_requests,
                'successful_requests': success_count
            }
        else:
            return {
                'success_rate': 0,
                'error': 'No successful requests'
            }
    
    def validate_endpoint_availability(self):
        """エンドポイントの可用性確認"""
        # ブラウザ経由での確認
        browser_check = {
            'page_accessible': self.get_current_url().endswith('/health'),
            'response_received': bool(self.get_response_text()),
            'page_loaded': self.wait_for_page_load()
        }
        
        # API経由での確認
        api_check = self.check_api_response_via_requests()
        
        return {
            'browser_check': browser_check,
            'api_check': api_check,
            'overall_available': (
                browser_check['page_accessible'] and 
                browser_check['response_received'] and 
                api_check.get('success', False)
            )
        }
    
    def check_error_handling(self):
        """エラーハンドリングの確認"""
        # 正常なエンドポイントの確認
        normal_response = self.check_api_response_via_requests()
        
        # 存在しないエンドポイントのテスト
        try:
            invalid_response = requests.get(f"{self.base_url}/nonexistent", timeout=5)
            invalid_status = invalid_response.status_code
        except requests.RequestException:
            invalid_status = None
        
        return {
            'normal_endpoint_works': normal_response.get('success', False),
            'invalid_endpoint_status': invalid_status,
            'handles_404_properly': invalid_status == 404
        }
    
    def comprehensive_health_check(self):
        """包括的なヘルスチェック"""
        return {
            'endpoint_availability': self.validate_endpoint_availability(),
            'json_structure': self.validate_json_structure(),
            'content_type': self.check_response_content_type(),
            'performance': self.perform_performance_test(),
            'error_handling': self.check_error_handling(),
            'browser_response_info': self.validate_response_headers_via_browser()
        }