import logging
from logging.handlers import RotatingFileHandler

megabytes_24 = 25165824

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)

api_file_rotator = RotatingFileHandler('./logs/api_logger.log', maxBytes=megabytes_24, backupCount=10)
api_file_rotator.setFormatter(formatter)

api_logger.addHandler(api_file_rotator)

zomboid_logger = logging.getLogger('zomboid')
zomboid_logger.setLevel(logging.DEBUG)

zomboid_file_rotator = RotatingFileHandler('./logs/zomboid_logger.log', maxBytes=megabytes_24, backupCount=10)
zomboid_file_rotator.setFormatter(formatter)

zomboid_logger.addHandler(zomboid_file_rotator)