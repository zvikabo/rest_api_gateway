import logging
import logging.handlers
import logging.handlers
import configparser


class CfgFile(object):
    def __init__(self, cfg_file_name):
        self.v_cfgFileName = cfg_file_name
        self.get_cfg_data()

    def get_cfg_data(self):
        config = configparser.ConfigParser()
        config.read(self.v_cfgFileName)
        dict_cfg = {s: dict(config.items(s)) for s in config.sections()}
        return dict_cfg


class MyLogger(object):
    def __init__(self, log_file, max_bytes=20000000, backup_count=5):
        self.v_log_file = log_file
        self.v_max_bytes = max_bytes
        self.v_backup_count = backup_count
        self.v_encoding='utf8'
        self.v_Fmt = "%(levelname)s:%(name)s | %(message)s '' | (%(asctime)s |  %(filename)s  |  %(lineno)d)"
        self.v_DateFmt = "%Y-%m-%d %H:%M:%S"
        # self.get_logger()

    def get_logger(self):
        f = logging.Formatter(fmt=self.v_Fmt, datefmt=self.v_DateFmt)
        handlers = [logging.handlers.RotatingFileHandler(self.v_log_file, encoding=self.v_encoding, maxBytes=self.v_max_bytes, backupCount=self.v_backup_count)]
        logger_file_name = logging.getLogger(self.v_log_file)
        logger_file_name.setLevel(logging.DEBUG)
        for h in handlers:
            h.setFormatter(f)
            h.setLevel(logging.DEBUG)
            logger_file_name.addHandler(h)
        return logger_file_name


