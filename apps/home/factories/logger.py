""" Logger factory defitions. """
import logging
import logging.config
import os

import yaml


class LoggerFactory:
    """Factory used to confgure and use the logger.
    It reads default values such as:
    ENV_KEY = "LOG_CFG"; DEFAULT_PATH="./owl/resources/logging.yaml"
    """

    __ENV_KEY = "LOG_CFG"
    __DEFAULT_PATH = f"{os.path.dirname(os.path.abspath(__file__)).split('/owl_ms/')[0]}/owl_ms/resources/logging.yaml"

    @staticmethod
    def configure(
        path=None,
        default_level=logging.INFO,
    ):
        """Initiliazes the log configuration for further use inside the library
        Args:
            path (str, optional): Configuration file path. Defaults to 'owl_ms/resources/logging.yaml'.
            default_level ([type], optional): Default log level to the application. Defaults to logging.INFO.
            env_key (str, optional): [description]. Defaults to 'LOG_CFG'.
        """
        config = None
        if not path:
            path = os.getenv(LoggerFactory.__ENV_KEY, LoggerFactory.__DEFAULT_PATH)
        if os.path.exists(path):
            try:
                with open(path, "rt") as f:
                    config = yaml.safe_load(f.read())
                    logging.config.dictConfig(config)
            except OSError:
                print(f"Path for logger config file {path} not found.")
        if not config:
            logging.basicConfig(level=default_level)
            print(f"Couldn't read the config {path}, created a default logger.")

    @staticmethod
    def get_logger(name: str = "", configure=True) -> logging.Logger:
        """returns the logger handler
        Args:
            name (str): Module name. Default '', returns the root logger.
            configure(bool): Run the configure method to load the yaml file.
        Returns:
            logging.Logger: logger handler
        """
        if configure:
            LoggerFactory.configure()
        return logging.getLogger(name)