from logger_config import zomboid_logger

def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        zomboid_logger.info(line)
