import logging
import traceback
import sys


log = logging.getLogger("main")
log.setLevel(logging.INFO)
FH = logging.FileHandler('app_log.log')

class My_logging:
    def __init__(self) -> None:
        pass

def info_log(info: str):
    basic_formater = logging.Formatter('%(asctime)s : [%(levelname)s] : %(message)s')
    FH.setFormatter(basic_formater)
    log.addHandler(FH)

def error_log(line_no: str):
    err_formater = logging.Formatter('%(asctime)s : [%(levelname)s][LINE ' + line_no + '] : %(message)s')
    FH.setFormatter(err_formater)
    log.addHandler(FH)
    log.error(traceback.format_exc())
    log.addHandler(FH)


info_log('info')


frame = traceback.extract_tb(sys.exc_info()[2])
line_no = str(frame[0]).split()[4]
## вызываем функцию записи ошибки и передаем в нее номер строки с ошибкой
error_log(line_no)
