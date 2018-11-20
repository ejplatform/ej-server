from django.core.management import call_command
    
def run_backup():
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d_%H%M%S")
    call_command(f'dumpdata > {date}.json')