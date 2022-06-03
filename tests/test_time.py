from datetime import datetime
import yaml

now = datetime.now()

date_time_now = now.strftime("%d-%m-%Y-%H-%M-%S")

print(date_time_now)

with open("parameters.yaml", encoding='utf-8_sig') as cf:
    data = yaml.load(cf, Loader=yaml.FullLoader)

print(data['default']['ENVIRONMENT'])






