# DeployServer
Deploy your project automatically when git branch was updated.

# Usage
To start your first autodeploy daemon you need to create python script file for your project.

```python
# Import DeployServer class
from DeployServer import DeployServer

# Init DeployServer with params
DeployServer({
    'server_address': 'http://mydomain.com',
    'port': 1234,
    'deploy': 'cd /var/www/myProject; git pull;'
})
```

Then you need to run this script.
```bash
$ python3 deploy.py
```

If you want to run autodeploy daemon in background, use Screen.
```bash
$ screen -dmS DeployServer_myProject python3 deploy.py
```
Screen docs: https://www.gnu.org/software/screen/manual/screen.html

# Initial params
For initiation DeployServer params dict is required.


### server_address : string
Enter a domain name for this server with http protocol.
```
'server_address': 'http://mydomain.com'
```
```
'server_address': 'http://8.8.8.8'
```
```
'server_address': 'http://0a1b2c3d.ngrok.io'
```

### port : integer
DeployServer will listen this local port.
```
'port': 2345
```

### deploy : string
Bash commands sequence which should be initiated on branch update.
```
'deploy': 'cd /var/www/myProject; git pull;'
```
```
'deploy': '/var/www/myProject/deploy.sh'
```

### (optional) branch : string
Which branch push event should initiate deploy function.
```
# default
'branch': 'master'
```
```
'branch': 'current-sprint'
```
```
'branch': 'ver2'
```

### (optional) uri : string
Callback uri.
```
# default
'uri': '/callback'
```
```
'uri': '/'
```

# Links

Repository: https://github.com/codex-team/deployserver

Report a bug: https://github.com/codex-team/deployserver/issues

CodeX Team: https://ifmo.su
