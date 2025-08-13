from loguru import logger

logger.add("logs/agent_project.log", level="TRACE", rotation="10 MB", retention="10 days")

def get_logger():
    return logger

if __name__ == "__main__":
    get_logger().info("INTIALIZING LOGGER")