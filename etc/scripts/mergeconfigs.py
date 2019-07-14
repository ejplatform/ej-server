# Execute as python mergeconfigs.py
# It will print result to STDOUT
from pathlib import Path

repo = Path(__file__).parent.parent.parent

def no_blanks(st):
    return '\n'.join(ln for ln in st.splitlines() if ln.strip())

# Read files
with open(repo / 'docker/docker-compose.deploy.yml') as fd:
    deploy = fd.read()

with open(repo / 'docker/docker-compose.rocket.yml') as fd:
    rocket = fd.read()



deploy = '\n'.join(line for line in deploy.splitlines() if not line.strip().startswith('#'))
rocket = '\n'.join(line for line in rocket.splitlines() if not line.strip().startswith('#'))

deploy_head, _, deploy_volumes = deploy.rpartition('volumes:')

_, _, rocket = rocket.partition('services:')
rocket_services, _, rocket_volumes = rocket.rpartition('volumes:')

print(no_blanks(deploy_head))
print(no_blanks(rocket_services))
print(no_blanks('volumes:'))
print(no_blanks(deploy_volumes))
print(no_blanks(rocket_volumes))
