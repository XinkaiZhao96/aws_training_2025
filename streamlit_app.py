import streamlit as st
import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError
import os

# Configure Streamlit page settings and layout
st.set_page_config(
    page_title="🧠 Weather Agent - 智能天氣助手",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': None,
        'About': "智能天氣助手 - 基於 Amazon Bedrock AgentCore 的天氣資訊服務"
    }
)

# Agent configuration
AGENT_ARN = 'arn:aws:bedrock-agentcore:us-east-1:318747609494:runtime/weather_agent-E87KKC6j1D'
AWS_REGION = 'us-east-1'

class WeatherAgentClient:
    """Weather Agent client with comprehensive error handling"""
    
    def __init__(self, region_name='us-east-1'):
        self.region_name = region_name
        self.agent_arn = AGENT_ARN
        self.client = None
        self.session = None
        self.connection_status = "disconnected"
        self.last_error = None
        self.connection_verified = False
        
        # Initialize AWS SDK integration
        self._initialize_aws_session()
    
    def _initialize_aws_session(self):
        """Initialize boto3 session with workshop-profile and proper error handling"""
        try:
            # Create session with workshop-profile
            self.session = boto3.Session(profile_name='workshop-profile')
            
            # Verify credentials by getting caller identity
            sts_client = self.session.client('sts', region_name=self.region_name)
            identity = sts_client.get_caller_identity()
            
            # Create bedrock-agentcore client
            self.client = self.session.client('bedrock-agentcore', region_name=self.region_name)
            
            # Update connection status
            self.connection_status = "connected"
            self.last_error = None
            self.connection_verified = True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['InvalidUserID.NotFound', 'AccessDenied', 'UnauthorizedOperation']:
                self.connection_status = "auth_error"
                self.last_error = f"AWS認證失敗: {e.response['Error']['Message']}"
            else:
                self.connection_status = "aws_error"
                self.last_error = f"AWS服務錯誤: {error_code}"
        except Exception as e:
            self.connection_status = "error"
            self.last_error = f"初始化失敗: {str(e)}"
            self.client = None
            self.session = None
    
    def get_connection_status(self):
        """Get detailed connection status information"""
        return {
            'status': self.connection_status,
            'verified': self.connection_verified,
            'error': self.last_error,
            'region': self.region_name,
            'agent_arn': self.agent_arn
        }
    
    def test_connection(self):
        """Test connection with a simple query and return detailed results"""
        if not self.client:
            return {
                'success': False,
                'error': {
                    'type': 'connection_error',
                    'message': f'AWS客戶端未初始化: {self.last_error}',
                    'retryable': False
                }
            }
        
        try:
            # Test with a simple query
            test_result = self.query_weather("Hello, test connection")
            if test_result['success']:
                self.connection_verified = True
                return {
                    'success': True,
                    'message': '連線測試成功',
                    'response_time': test_result.get('metadata', {}).get('timestamp')
                }
            else:
                return test_result
                
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'connection_test_error',
                    'message': f'連線測試失敗: {str(e)}',
                    'retryable': True
                }
            }
    
    def _categorize_error(self, error_type: str, error_code: str = None, error_message: str = None) -> dict:
        """Categorize errors and provide user guidance"""
        error_categories = {
            'auth': {
                'codes': ['AccessDenied', 'UnauthorizedOperation', 'InvalidUserID.NotFound', 'TokenRefreshRequired'],
                'message': '❌ AWS 認證失敗\n\n請檢查：\n- workshop-profile 配置\n- IAM 權限設定\n- AWS 憑證有效性',
                'retryable': False,
                'guidance': '請確認 AWS 憑證配置正確'
            },
            'network': {
                'codes': ['NetworkingError', 'EndpointConnectionError', 'ConnectTimeoutError'],
                'message': '❌ 網路連線問題\n\n建議：\n- 檢查網路連線\n- 確認 AWS 服務狀態\n- 稍後重試',
                'retryable': True,
                'guidance': '請檢查網路連線並稍後重試'
            },
            'service': {
                'codes': ['ThrottlingException', 'ServiceUnavailableException', 'InternalServerError'],
                'message': '❌ 服務暫時不可用\n\n建議：\n- 稍後重試\n- 檢查 AWS 服務狀態',
                'retryable': True,
                'guidance': '服務繁忙，請稍後重試'
            },
            'validation': {
                'codes': ['ValidationException', 'InvalidParameterException', 'MalformedPolicyDocument'],
                'message': '❌ 請求格式錯誤\n\n可能原因：\n- 查詢格式不正確\n- 參數無效',
                'retryable': False,
                'guidance': '請檢查查詢格式'
            },
            'parsing': {
                'codes': ['JSONDecodeError', 'ResponseParsingError'],
                'message': '❌ 回應格式錯誤\n\n系統無法解析 Agent 回應，請重試或聯繫管理員',
                'retryable': True,
                'guidance': '回應解析失敗，請重試'
            }
        }
        
        # Find matching category
        for category, config in error_categories.items():
            if error_code in config['codes'] or error_type == category:
                return {
                    'category': category,
                    'message': config['message'],
                    'retryable': config['retryable'],
                    'guidance': config['guidance']
                }
        
        # Default for unknown errors
        return {
            'category': 'unknown',
            'message': f'❌ 未知錯誤\n\n錯誤訊息: {error_message or "無詳細資訊"}',
            'retryable': False,
            'guidance': '發生未知錯誤，請聯繫管理員'
        }
    
    def _create_standardized_response(self, success: bool, data: str = None, error_info: dict = None, metadata: dict = None) -> dict:
        """Create standardized response format"""
        response = {
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if success and data is not None:
            response['data'] = data
            if metadata:
                response['metadata'] = metadata
        elif not success and error_info:
            response['error'] = error_info
        
        return response
    
    def query_weather(self, prompt: str) -> dict:
        """Query weather information with comprehensive error handling and standardized responses"""
        # Check client availability
        if not self.client:
            error_info = self._categorize_error('auth', error_message=self.last_error)
            return self._create_standardized_response(
                success=False,
                error_info={
                    'type': 'connection_error',
                    'code': 'CLIENT_NOT_INITIALIZED',
                    'message': error_info['message'],
                    'category': error_info['category'],
                    'retryable': error_info['retryable'],
                    'guidance': error_info['guidance']
                }
            )
        
        try:
            # Prepare payload
            payload = {"prompt": prompt}
            
            # Make API call
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_arn,
                payload=json.dumps(payload)
            )
            
            # Parse response body - handle different response formats
            response_body = None
            if 'response' in response:
                response_body = json.loads(response['response'].read())
            elif 'body' in response:
                response_body = json.loads(response['body'].read())
            else:
                response_body = response
            
            # Extract response text with multiple fallback strategies
            response_text = self._extract_response_text(response_body)
            
            # Create metadata
            metadata = {
                'request_id': response.get('ResponseMetadata', {}).get('RequestId'),
                'http_status': response.get('ResponseMetadata', {}).get('HTTPStatusCode'),
                'agent_arn': self.agent_arn,
                'region': self.region_name
            }
            
            return self._create_standardized_response(
                success=True,
                data=response_text,
                metadata=metadata
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            error_info = self._categorize_error('service', error_code, error_message)
            
            return self._create_standardized_response(
                success=False,
                error_info={
                    'type': 'aws_client_error',
                    'code': error_code,
                    'message': error_info['message'],
                    'category': error_info['category'],
                    'retryable': error_info['retryable'],
                    'guidance': error_info['guidance'],
                    'raw_message': error_message
                }
            )
            
        except json.JSONDecodeError as e:
            error_info = self._categorize_error('parsing', 'JSONDecodeError', str(e))
            
            return self._create_standardized_response(
                success=False,
                error_info={
                    'type': 'json_decode_error',
                    'code': 'RESPONSE_PARSING_FAILED',
                    'message': error_info['message'],
                    'category': error_info['category'],
                    'retryable': error_info['retryable'],
                    'guidance': error_info['guidance']
                }
            )
            
        except (ConnectionError, TimeoutError) as e:
            error_info = self._categorize_error('network', error_message=str(e))
            
            return self._create_standardized_response(
                success=False,
                error_info={
                    'type': 'network_error',
                    'code': 'CONNECTION_FAILED',
                    'message': error_info['message'],
                    'category': error_info['category'],
                    'retryable': error_info['retryable'],
                    'guidance': error_info['guidance']
                }
            )
            
        except Exception as e:
            error_info = self._categorize_error('unknown', error_message=str(e))
            
            return self._create_standardized_response(
                success=False,
                error_info={
                    'type': 'unexpected_error',
                    'code': 'UNKNOWN_ERROR',
                    'message': error_info['message'],
                    'category': error_info['category'],
                    'retryable': error_info['retryable'],
                    'guidance': error_info['guidance']
                }
            )
    
    def _extract_response_text(self, response_body: dict) -> str:
        """Extract response text from various response body formats"""
        if not response_body:
            return '無回應資料'
        
        # Strategy 1: Check for 'result' field
        if 'result' in response_body:
            result = response_body['result']
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                if 'content' in result and len(result['content']) > 0:
                    if 'text' in result['content'][0]:
                        return result['content'][0]['text']
        
        # Strategy 2: Check for direct 'content' field
        if 'content' in response_body and len(response_body['content']) > 0:
            content_item = response_body['content'][0]
            if isinstance(content_item, dict) and 'text' in content_item:
                return content_item['text']
            elif isinstance(content_item, str):
                return content_item
        
        # Strategy 3: Check for 'response' or 'message' fields
        for field in ['response', 'message', 'text', 'output']:
            if field in response_body:
                return str(response_body[field])
        
        # Fallback: Return string representation of the response
        return f'無法解析回應格式: {str(response_body)[:200]}...'

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'weather_client' not in st.session_state:
    st.session_state.weather_client = WeatherAgentClient()
if 'loading' not in st.session_state:
    st.session_state.loading = False

def render_sidebar():
    """Render sidebar with connection status and controls"""
    with st.sidebar:
        st.header("🔧 系統狀態")
        
        # Connection status display system
        client = st.session_state.weather_client
        status_info = client.get_connection_status()
        
        # Enhanced connection status with clear visual indicators
        st.subheader("🔗 連線狀態")
        if status_info['status'] == "connected":
            st.success("🟢 **連線正常**")
            if status_info['verified']:
                st.success("✅ **連線已驗證**")
            else:
                st.warning("⚠️ **連線未驗證** - 建議執行連線測試")
        elif status_info['status'] == "auth_error":
            st.error("🔴 **認證錯誤**")
            with st.expander("查看錯誤詳情", expanded=False):
                st.error(f"**錯誤訊息:** {status_info['error']}")
                st.info("**解決方案:**\n- 檢查 workshop-profile 配置\n- 確認 AWS 憑證有效性\n- 驗證 IAM 權限設定")
        elif status_info['status'] == "aws_error":
            st.error("🔴 **AWS 服務錯誤**")
            with st.expander("查看錯誤詳情", expanded=False):
                st.error(f"**錯誤訊息:** {status_info['error']}")
                st.info("**解決方案:**\n- 檢查 AWS 服務狀態\n- 確認網路連線\n- 稍後重試")
        else:
            st.error("🔴 **連線錯誤**")
            if status_info['error']:
                with st.expander("查看錯誤詳情", expanded=False):
                    st.error(f"**錯誤訊息:** {status_info['error']}")
                    st.info("**解決方案:**\n- 檢查網路連線\n- 重新啟動應用程式\n- 聯繫系統管理員")
        
        # System configuration information
        st.subheader("📋 系統配置")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.text("🌍 AWS Region:")
            st.text("🤖 Agent ID:")
            st.text("🔧 Profile:")
        with col2:
            st.text(f"{AWS_REGION}")
            st.text("weather_agent-E87KKC6j1D")
            st.text("workshop-profile")
        
        # Last update timestamp
        if 'last_update_time' not in st.session_state:
            st.session_state.last_update_time = datetime.now()
        
        st.info(f"⏰ **最後更新:** {st.session_state.last_update_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Interactive sidebar controls
        st.subheader("🎛️ 控制面板")
        
        # Clear conversation button with session state reset
        if st.button("🗑️ 清除對話", use_container_width=True, help="清除所有對話記錄並重置聊天狀態"):
            st.session_state.messages = []
            st.session_state.last_update_time = datetime.now()
            st.success("✅ 對話已清除")
            st.rerun()
        
        # Test connection functionality with result display
        if st.button("🔄 測試連線", use_container_width=True, help="測試與 Weather Agent 的連線狀態"):
            with st.spinner("正在測試連線..."):
                test_result = client.test_connection()
                st.session_state.last_update_time = datetime.now()
                
                if test_result['success']:
                    st.success(f"✅ **{test_result['message']}**")
                    if test_result.get('response_time'):
                        st.info(f"📊 **回應時間:** {test_result['response_time']}")
                    # Update connection status in session
                    client.connection_verified = True
                else:
                    error_info = test_result['error']
                    st.error(f"❌ **連線測試失敗**")
                    with st.expander("查看測試結果詳情", expanded=True):
                        st.error(f"**錯誤類型:** {error_info.get('type', '未知')}")
                        st.error(f"**錯誤訊息:** {error_info['message']}")
                        if error_info.get('retryable'):
                            st.warning("🔄 **此錯誤可重試**")
                        else:
                            st.warning("⚠️ **需要修正配置後重試**")
                        if error_info.get('guidance'):
                            st.info(f"💡 **建議:** {error_info['guidance']}")
        
        # Additional configuration details
        with st.expander("🔍 詳細配置資訊", expanded=False):
            st.text(f"Agent ARN: {AGENT_ARN}")
            st.text(f"連線狀態: {status_info['status']}")
            st.text(f"驗證狀態: {'已驗證' if status_info['verified'] else '未驗證'}")
            if hasattr(client, 'session') and client.session:
                try:
                    sts_client = client.session.client('sts')
                    identity = sts_client.get_caller_identity()
                    st.text(f"AWS Account: {identity.get('Account', 'N/A')}")
                    st.text(f"User ARN: {identity.get('Arn', 'N/A')}")
                except:
                    st.text("AWS Account: 無法取得")
                    st.text("User ARN: 無法取得")

def render_chat_message(role: str, content: str, timestamp: str = None):
    """Render chat message with proper styling"""
    with st.chat_message(role):
        if role == "user":
            st.markdown(f"**您:** {content}")
        else:
            st.markdown(f"**🧠 天氣助手:**")
            # Use st.markdown to properly render weather information with formatting
            st.markdown(content)
        
        if timestamp:
            st.caption(f"時間: {timestamp}")

def process_user_input(user_input: str):
    """Process user input and get agent response with enhanced error handling"""
    try:
        st.session_state.loading = True
        
        # Add user message to chat
        user_timestamp = datetime.now().strftime('%H:%M:%S')
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": user_timestamp
        })
        
        # Get agent response
        with st.spinner("正在獲取天氣資訊..."):
            result = st.session_state.weather_client.query_weather(user_input)
        
        if result['success']:
            # Add successful response to chat
            agent_timestamp = datetime.now().strftime('%H:%M:%S')
            st.session_state.messages.append({
                "role": "assistant",
                "content": result['data'],
                "timestamp": agent_timestamp,
                "metadata": result.get('metadata', {})
            })
        else:
            # Create comprehensive error message using standardized error info
            error_info = result['error']
            error_msg = error_info['message']
            
            # Add guidance if available
            if error_info.get('guidance'):
                error_msg += f"\n\n💡 **建議:** {error_info['guidance']}"
            
            # Add retry information
            if error_info.get('retryable'):
                error_msg += "\n\n🔄 **此錯誤可重試**"
            else:
                error_msg += "\n\n⚠️ **此錯誤需要修正後才能重試**"
            
            # Add technical details for debugging (collapsed)
            if error_info.get('code') or error_info.get('category'):
                error_msg += f"\n\n<details><summary>技術詳情</summary>"
                if error_info.get('category'):
                    error_msg += f"\n錯誤類別: {error_info['category']}"
                if error_info.get('code'):
                    error_msg += f"\n錯誤代碼: {error_info['code']}"
                error_msg += f"\n</details>"
            
            agent_timestamp = datetime.now().strftime('%H:%M:%S')
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": agent_timestamp,
                "error_info": error_info
            })
    
    finally:
        st.session_state.loading = False
        st.rerun()

def main():
    """Main application with proper component organization and structured layout"""
    # Ensure proper state management and UI flow
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        st.session_state.last_update_time = datetime.now()
    
    # Initialize and render sidebar with system status
    render_sidebar()
    
    # Main application header with title and description
    st.title("🧠 Weather Agent - 智能天氣助手")
    st.markdown("""
    ### 歡迎使用智能天氣助手！🌍
    
    這是一個基於 Amazon Bedrock AgentCore 的智能天氣服務，為您提供：
    - 🌤️ **即時天氣資訊** - 全球城市的詳細天氣狀況
    - 🎉 **當地活動推薦** - 發現有趣的本地事件和活動  
    - ☀️ **日出日落時間** - 精確的日照時間資訊
    - 🤖 **智能對話** - 自然語言查詢，支援中英文
    
    ---
    """)
    
    # Enhanced example queries section with categorized examples
    with st.expander("💡 範例查詢與使用說明", expanded=False):
        # Welcome message and clear instructions
        st.markdown("""
        ### 🎯 歡迎使用智能天氣助手！
        
        這個助手可以為您提供全球城市的即時資訊，包括天氣狀況、當地活動和日出日落時間。
        您可以用自然語言提問，系統會智能理解您的需求。
        
        ### 📝 使用說明
        - 💬 **直接對話**: 在下方輸入框中用自然語言提問
        - 🚀 **快速查詢**: 點擊快速按鈕獲取熱門城市天氣
        - 🔄 **組合查詢**: 可以同時詢問多種資訊類型
        - 🌍 **全球支援**: 支援世界各大城市查詢
        """)
        
        st.divider()
        
        # Categorized example queries
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🌤️ 天氣資訊查詢
            **基本天氣查詢:**
            - "台北今天天氣如何？"
            - "東京現在的溫度是多少？"
            - "倫敦今天會下雨嗎？"
            - "巴黎的濕度和風速如何？"
            
            **詳細天氣資訊:**
            - "紐約今天的完整天氣報告"
            - "雪梨現在的天氣狀況和體感溫度"
            - "新加坡今天適合戶外活動嗎？"
            
            ### 🎉 活動與事件查詢
            **當地活動搜尋:**
            - "紐約有什麼有趣的活動？"
            - "倫敦這週末有什麼事件？"
            - "東京最近有什麼展覽或演出？"
            - "巴黎有什麼文化活動推薦？"
            
            **特定類型活動:**
            - "洛杉磯有什麼音樂會？"
            - "柏林的藝術展覽有哪些？"
            """)
        
        with col2:
            st.markdown("""
            ### ☀️ 日出日落時間查詢
            **基本日照時間:**
            - "雪梨今天日出時間？"
            - "東京的日落是幾點？"
            - "倫敦今天的日照時長？"
            - "紐約明天日出日落時間？"
            
            **日照相關資訊:**
            - "巴黎今天適合看日出嗎？"
            - "洛杉磯的黃金時刻是什麼時候？"
            
            ### 🔄 綜合查詢範例
            **多重資訊組合:**
            - "告訴我倫敦的天氣、活動和日出時間"
            - "台北今天的完整旅遊資訊"
            - "我想了解東京今天的天氣和有什麼好玩的"
            - "紐約今天適合外出嗎？包括天氣和活動"
            
            **旅行規劃查詢:**
            - "巴黎今天的天氣和推薦活動"
            - "雪梨現在的情況，包括天氣和日照"
            - "洛杉磯今天的完整城市資訊"
            """)
        
        st.divider()
        
        # Additional tips and guidance
        st.markdown("""
        ### 💡 使用小貼士
        
        **🎯 查詢技巧:**
        - 可以使用中文或英文城市名稱
        - 支援模糊查詢，如"台北"、"Taipei"都可以
        - 可以詢問"今天"、"現在"、"這週末"等時間相關問題
        
        **🌟 最佳實踐:**
        - 一次查詢可以包含多個問題
        - 使用自然語言，就像和朋友聊天一樣
        - 如果結果不滿意，可以換個方式重新提問
        
        **⚠️ 注意事項:**
        - 天氣資料為即時資訊，可能會有輕微延遲
        - 活動資訊來源於公開平台，建議查詢前確認
        - 日出日落時間基於標準時區計算
        """)
        
        # Quick start suggestion
        st.info("💫 **快速開始**: 試試問「台北今天天氣如何？」或點擊下方的快速查詢按鈕！")
    
    # Quick action buttons section - placed before chat for better UX
    st.subheader("🚀 快速查詢")
    st.markdown("點擊下方按鈕快速獲取熱門城市的天氣資訊：")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🌤️ 台北天氣", use_container_width=True, help="獲取台北即時天氣資訊"):
            if not st.session_state.loading:
                process_user_input("台北今天天氣如何？")
    
    with col2:
        if st.button("🗼 東京天氣", use_container_width=True, help="獲取東京即時天氣資訊"):
            if not st.session_state.loading:
                process_user_input("東京現在天氣怎樣？")
    
    with col3:
        if st.button("🏛️ 倫敦天氣", use_container_width=True, help="獲取倫敦即時天氣資訊"):
            if not st.session_state.loading:
                process_user_input("倫敦今天天氣如何？")
    
    with col4:
        if st.button("🗽 紐約天氣", use_container_width=True, help="獲取紐約即時天氣資訊"):
            if not st.session_state.loading:
                process_user_input("紐約現在天氣怎樣？")
    
    # Chat interface section
    st.subheader("💬 智能對話")
    st.markdown("在下方輸入框中用自然語言提問，或查看上方的範例查詢：")
    
    # Chat input - placed before messages for better UX
    if not st.session_state.loading:
        user_input = st.chat_input("請輸入您的問題，例如：「台北今天天氣如何？」")
        if user_input:
            process_user_input(user_input)
    else:
        st.chat_input("正在處理中，請稍候...", disabled=True)
    
    # Display chat messages with proper container
    if st.session_state.messages:
        st.markdown("#### 對話記錄")
        # Create a container for chat messages with better styling
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                render_chat_message(
                    message["role"], 
                    message["content"], 
                    message.get("timestamp")
                )
    else:
        # Show welcome message when no chat history
        st.info("👋 歡迎！請在上方輸入框中提問，或點擊快速查詢按鈕開始對話。")

if __name__ == "__main__":
    main()