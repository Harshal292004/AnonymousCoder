from loguru import logger


def get_logger(enable_logging: bool = True, log_file: str = "logs/agent_project.log"):
    if enable_logging:
        logger.add(log_file, level="TRACE", rotation="10 MB", retention="10 days")
        return logger
    else:
        class DummyLogger:
            def __getattr__(self, name):
                def no_op(*args, **kwargs):
                    pass
                return no_op
        return DummyLogger()