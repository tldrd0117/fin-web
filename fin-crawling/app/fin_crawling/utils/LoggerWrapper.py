import logging
import logging.config


def log_setup() -> None:
    config = {
        "version": 1,
        "formatters": {
            "simple": {"format": "[%(name)s] %(message)s"},
            "complex": {
                "format": "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "/usr/src/app/log/log.log",
                "formatter": "complex",
            },
        },
        "root": {"handlers": ["console", "file"], "level": "WARNING"},
        "loggers": {
            "mongo": {"level": "DEBUG"},
            "eventemitter": {"level": "DEBUG"},
            "parent": {"level": "INFO"},
            "parent.child": {"level": "DEBUG"},
            "socketio": {"level": "INFO"},
            "engineio": {"level": "INFO"}
        },
    }

    logging.config.dictConfig(config)

    
