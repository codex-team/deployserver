deployserver
============

Deploy your project automatically when git branch was updated via GitHub or BitBucket webhooks.

Usage
-----
Install deployserver from pip.

.. code:: bash

    $ pip3 install deployserver


To start your first autodeploy daemon you need to create `deploy.py` script file in your project.

.. code:: python

    import deployserver


    deployserver.init({
        'server_address': 'http://mydomain.com',
        'port': 1234,
        'deploy': 'cd /var/www/myProject;' \
                  'git pull;'
    })

Then you need to run this script.

.. code:: bash

    $ python3 deploy.py

If you want to run autodeploy daemon in background, use Screen.

.. code:: bash

    $ screen -dmS deployserver_myProject python3 deploy.py

Screen docs: https://www.gnu.org/software/screen/manual/screen.html

Initial params
--------------

For initiation deployserver params dict is required.

server\_address : string
~~~~~~~~~~~~~~~~~~~~~~~~

Enter a domain name for this server with http protocol.

.. code:: python

    'server_address': 'http://mydomain.com'

.. code:: python

    'server_address': 'http://8.8.8.8'

.. code:: python

    'server_address': 'http://0a1b2c3d.ngrok.io'

port : integer
~~~~~~~~~~~~~~

deployserver will listen this local port.

.. code:: python

    'port': 2345

deploy : string
~~~~~~~~~~~~~~~

Bash commands sequence which should be initiated on branch update.

.. code:: python

    'deploy': 'cd /var/www/myProject;' \
              'git pull;'

.. code:: python

    'deploy': '/var/www/myProject/deploy.sh'

(optional) branch : string
~~~~~~~~~~~~~~~~~~~~~~~~~~

Which branch push event should initiate deploy function.

.. code:: python

    # default
    'branch': 'master'

.. code:: python

    'branch': 'current-sprint'

.. code:: python

    'branch': 'ver2'

(optional) uri : string
~~~~~~~~~~~~~~~~~~~~~~~

Callback uri.

.. code:: python

    # default
    'uri': '/callback'

.. code:: python

    'uri': '/'

(optional) secret_token : string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Secret token. Check if it is set.

.. code:: python

    # default
    'secret_token': None

.. code:: python

    'secret_token': 'a96529a4af7864e7f6e11035d10b7db5'


Requirements
------------
- Python >= 3.5
- aiohttp
- asyncio

Links
-----

Repository: https://github.com/codex-team/deployserver

Report a bug: https://github.com/codex-team/deployserver/issues

PyPI Package: https://pypi.python.org/pypi/deployserver

CodeX Team: https://ifmo.su
