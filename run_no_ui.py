"""
vnpy 无界面模式运行示例
不启动 GUI，直接通过代码调用 vnpy 核心引擎
"""
from time import sleep
import signal
import sys

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.logger import INFO, logger

# 启用控制台日志输出
SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
SETTINGS["log.file"] = True

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

    logger.info("=" * 60)
    logger.info("vnpy 无界面模式启动成功")
    logger.info("主引擎已创建，可按 Ctrl+C 退出")
    logger.info("=" * 60)

    # 这里可以添加网关连接、策略加载等操作
    # 例如：
    # main_engine.add_gateway(CtpGateway)
    # main_engine.connect(ctp_setting, "CTP")

    # 保持运行，等待外部信号
    while running:
        sleep(1)

    # 关闭引擎
    main_engine.close()
    logger.info("vnpy 引擎已安全关闭")


if __name__ == "__main__":
    main()
