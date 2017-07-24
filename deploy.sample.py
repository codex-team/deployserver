"""
Here is a sample script which uses DeployServer

Run and test your script:
$ python3 myProject_autodeploy.py

To run script with Screen silently:
$ screen -dmS myProject_autodeploy python3 myProject_autodeploy.py

DeployServer repo: https://github.com/codex-team/deploy
Screen docs: https://www.gnu.org/software/screen/manual/screen.html
"""

from DeployServer import DeployServer


DeployServer({
    'server_address': 'http://mydomain.com',
    'port': 1234,
    'deploy': 'cd /var/www/myProject; git pull;'
})
