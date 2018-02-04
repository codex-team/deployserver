"""
DeployServer
============

Autodeploy your project when git branch was updated.

Usage
-----

>>> import deployserver
>>> deployserver.init({
...     'server_address': 'http://mydomain.com',
...     'port': 1234,
...     'deploy': 'cd /var/www/myProject; git pull;'
... })

Links
-----

Repository: https://github.com/codex-team/deploy
Report bug: https://github.com/codex-team/deploy/issues
"""
import asyncio
import os
import hashlib
import hmac

from aiohttp import web


def init(settings):
    """
    Run DeployServer

    Parameters
    ----------
    params['server_address'] : string
        Enter a domain name for this server with http protocol.
        example: 'http://mydomain.com'
                 'http://8.8.8.8'
                 'http://0a1b2c3d.ngrok.io'

    params['port'] : integer
        DeployServer will listen this local port.
        example: 2345

    params['deploy'] : string
        Bash commands sequence which should be initiated on branch update.
        example: 'cd /var/www/myProject; git pull;'
                 '/var/www/myProject/deploy.sh'

    params['branch'] : string
        (optional) Which branch push event should initiate deploy function.
        default: 'master'
        example: 'current-sprint'
                 'ver2'

    params['uri'] : string
        (optional) Callback uri.
        default: '/callback'
        example: '/'

    params['secret_token'] : string
        (optional) Secret token.
        default: None
        example: 'a96529a4af7864e7f6e11035d10b7db5'
    """

    params = {
        'server_address': settings.get('server_address'),
        'port': settings.get('port'),
        'deploy': settings.get('deploy', ''),
        'uri': settings.get('uri', '/callback'),
        'branch': 'refs/heads/' + settings.get('branch', 'master'),
        'secret_token': settings.get('secret_token', None)
    }

    def show_welcome_message():
        """
        Show welcome message with set up guide
        """
        # hack for showing correct webhook url for ngrok urls
        try:
            if params['server_address'][-8:] != 'ngrok.io':
                URL = '{}:{}{}'.format(params['server_address'], params['port'], params['uri'])
            else:
                URL = '{}{}'.format(params['server_address'], params['uri'])
        except:
            print('Cannot create webhook url. Check \'server_address\' param.')
            exit()

        message = 'DeployServer is ready to get requests from Github.\n' \
                  '\n' \
                  'Please set up a new webhook in project settings with following params:\n' \
                  '- Payload URL: ' + URL + '\n' \
                  '- Content type: application/json \n' \
                  + ('- Secret: ' + params['secret_token'] + '\n' if params['secret_token'] else '') + \
                  '- Which events would you like to trigger this webhook?\n'\
                  '  [x] Just the push event.\n' \
                  '\n' \
                  'Web Application logs:'

        print(message)

    def run():
        """
        Run aiohttp app on your server
        """
        loop = asyncio.get_event_loop()
        app = web.Application(loop=loop)
        app.router.add_post('/callback', github_callback)
        web.run_app(app, port=params['port'])

    def verify_callback(signature, body):
        if not params['secret_token']:
            return True

        if not signature.startswith("sha1="):
            return False

        return signature[5:] == hmac.new(params['secret_token'].encode(), body, hashlib.sha1).hexdigest()

    async def github_callback(request):
        """
        Web App function for processing callback
        """
        try:
            data = await request.json()
            headers = request.headers
            event = headers.get("X-GitHub-Event", "")
            signature = headers.get("X-Hub-Signature", "")

            # Verify signature if it is set in configuration
            if params['secret_token']:
                body = await request.read()
                if not verify_callback(signature, body):
                    print('Signature verification failed...')
                    return web.Response(status=web.HTTPUnauthorized.status_code)

            if event == "push":
                ref = data.get("ref", "")

                print('Got a {} event in {} branch.'.format(event, ref))

                if params['branch'] == ref:
                    print('Run deploy script...')
                    os.system(params['deploy'])

        except Exception as e:
            print("[github callback] Message process error: [%s]" % e)

        return web.Response(text='OK')

    show_welcome_message()
    run()
