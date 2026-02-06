import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("API_KEY", "2a7ec09588b14d14b66d730ac2e5266e.2ATkSDwtRBlgi6Rn")
    BASE_URL = os.getenv("BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    MODEL = os.getenv("MODEL", "glm-4.5-flash")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    STREAMLIT_TITLE = os.getenv("STREAMLIT_TITLE", "Excel智能数据操作助手")
    STREAMLIT_LAYOUT = os.getenv("STREAMLIT_LAYOUT", "wide")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "200"))
    
    TABLE_PREVIEW_ROWS = int(os.getenv("TABLE_PREVIEW_ROWS", "20"))
    TABLE_PREVIEW_COLS = int(os.getenv("TABLE_PREVIEW_COLS", "20"))
    
    OPERATION_HISTORY_LIMIT = int(os.getenv("OPERATION_HISTORY_LIMIT", "50"))

settings = Settings()