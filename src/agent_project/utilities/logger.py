from loguru import logger as log

_configured = False


def init_logger(enable_logging: bool = True, log_file: str = "logs/agent_project.log"):
    global _configured
    if _configured:
        return log
    
    # Ensure no duplicate sinks
    log.remove()
    
    if enable_logging:
        log.add(log_file, level="TRACE", rotation="10 MB", retention="10 days")
    else:
        # Swallow all logs when disabled
        log.add(lambda *args, **kwargs: None)
    
    _configured = True
    return log