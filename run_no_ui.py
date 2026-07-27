"""
vnpy 无界面模式运行示例
集成了 CTP 接口、CTA 策略引擎和数据管理模块

使用方法：
1. 先填写下方的 CTP 账号信息（实盘/模拟盘）
2. 准备好策略文件（默认放在 ./strategies 目录）
3. 运行：/workspace/venv_vnpy/bin/python run_no_ui.py
4. 按 Ctrl+C 安全退出
"""
from time import sleep
import signal
import sys

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine, LogEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.logger import INFO, logger

from vnpy_ctp import CtpGateway
from vnpy_ctastrategy import CtaStrategyApp, CtaEngine
from vnpy_ctastrategy.base import EVENT_CTA_LOG
from vnpy_datamanager import DataManagerApp

# ========== 日志配置 ==========
SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

# ========== CTP 账号配置 ==========
# ⚠️ 请填写你的 CTP 账号信息，否则不会连接实盘/模拟盘
CTP_SETTING = {
    "用户名": "",
    "密码": "",
    "经纪商代码": "",
    "交易服务器": "",
    "行情服务器": "",
    "产品名称": "",
    "授权编码": "",
    "产品信息": ""
}

running = True


def handle_signal(signum, frame):
    """处理 Ctrl+C 退出信号"""
    global running
    logger.info("收到退出信号，正在关闭引擎...")
    running = False


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def main():
    """主函数"""
    # 创建事件引擎和主引擎
    event_engine: EventEngine = EventEngine()
    main_engine: MainEngine = MainEngine(event_engine)

    # 注册 CTP 网关
    main_engine.add_gateway(CtpGateway)

    # 注册应用模块
    cta_engine: CtaEngine = main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(DataManagerApp)

    # 注册 CTA 日志事件监听
    log_engine: LogEngine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)

    logger.info("=" * 60)
    logger.info("vnpy 无界面模式启动成功")
    logger.info("已加载：CTP 网关 / CTA 策略 / 数据管理")
    logger.info("按 Ctrl+C 退出")
    logger.info("=" * 60)

    # ========== 连接 CTP（仅在填写了账号信息后执行） ==========
    if all(CTP_SETTING.values()):
        main_engine.connect(CTP_SETTING, "CTP")
        logger.info("CTP 连接请求已发送")
        sleep(10)  # 等待连接完成

        # 初始化并启动 CTA 策略
        cta_engine.init_engine()
        logger.info("CTA 策略引擎初始化完成")

        cta_engine.init_all_strategies()
        sleep(60)  # 等待策略初始化完成
        logger.info("CTA 策略全部初始化")

        cta_engine.start_all_strategies()
        logger.info("CTA 策略全部启动")
    else:
        logger.warning("CTP 账号信息未填写，跳过连接和策略启动")
        logger.info("请在脚本中填写 CTP_SETTING 后再运行实盘/模拟盘")

    # ========== 主循环 ==========
    while running:
        sleep(1)

    # 关闭引擎
    main_engine.close()
    logger.info("vnpy 引擎已安全关闭")


if __name__ == "__main__":
    main()
