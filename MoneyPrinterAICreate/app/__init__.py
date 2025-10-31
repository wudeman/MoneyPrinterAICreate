"""MoneyPrinterAI应用包初始化"""

import logging
from app.config.database import init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 初始化数据库
try:
    logger.info("开始初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")
except Exception as e:
    logger.error(f"数据库初始化失败: {e}")
    raise

__version__ = "1.0.0"