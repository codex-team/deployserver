"""
DeployServer
Autodeploy your project when git branch was updated.

Repository: https://github.com/codex-team/deploy
Report bug: https://github.com/codex-team/deploy/issues
"""

from aiohttp import web
import asyncio
import os

params = {}

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
    """

    params['server_address'] = settings.get('server_address')
    params['port'] = settings.get('port')
    params['deploy'] = settings.get('deploy', '')
    params['uri'] = settings.get('uri', '/callback')
    params['branch'] = 'refs/heads/' + settings.get('branch', 'master')

    show_welcome_message()
    run()

def show_welcome_message():
    """
    Show welcome message with set up guide
    """
    # hack for showing correct webhook url for ngrok urls
    try:
        if params['server_address'][-8:] != 'ngrok.io':
            URL = '{}:{}{}'.format(params['server_address'], params['port'], params['uri'])
        else:
            URL = '{}{}'.format(params['server_address'], params['port'], params['uri'])
    except:
        print('Cannot create webhook url. Check \'server_address\' param.')
        exit()

    message = 'DeployServer is ready to get requests from Github.\n' \
              '\n' \
              'Please set up a new webhook in project settings with following params:\n' \
              '- Payload URL: ' + URL + '\n' \
              '- Content type: application/json \n' \
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

async def github_callback(request):
    """
    Web App function for processing callback
    """
    try:
        data = await request.json()
        headers = request.headers
        event = headers.get("X-GitHub-Event", "")

        if event == "push":
            ref = data.get("ref", "")

            if params['branch']:
                os.system(params['deploy'])

            print('Got a {} event in {} branch.'.format(event, data.get("ref")))

    except Exception as e:
        print("[github callback] Message process error: [%s]" % e)

    return web.Response(text='OK')
