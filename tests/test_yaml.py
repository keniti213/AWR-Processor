from datetime import datetime
import yaml
import sys

now = datetime.now()

date_time_now = now.strftime("%d-%m-%Y-%H-%M-%S")

print(date_time_now)


try:
    with open("parameters.yaml", encoding='utf-8_sig') as cf:
        data = yaml.load(cf, Loader=yaml.FullLoader)
except:
    print("parameters file not found: ")
    sys.exit()

print(data['default']['ENVIRONMENT'])

file_name = "test-file.txt"

class Logger:
    def __init__(self, file_name):
        self.log_file = open(file_name, "w+")

    def log_message(self, message, print_flag=False):
        self.log_file.write(message)
        if print_flag:
            print(message)

    def close_logger(self):
        self.log_file.close()


logger = Logger(file_name)
logger.log_message("\t\testa e' uma mensagem", True)
logger.close_logger()