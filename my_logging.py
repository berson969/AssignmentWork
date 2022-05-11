import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename = "app_log.log",
    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )

logging.info('Hello')

log = logging.getLogger("main")

FH = logging.FileHandler('app_log.log')
basic_formater = logging.Formatter('%(asctime)s : [%(levelname)s] : %(message)s')
FH.setFormatter(basic_formater)
log.addHandler(FH)


log.info('info message')
