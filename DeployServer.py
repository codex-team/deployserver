"""
DeployServer
Autodeploy your project when git branch was updated.


Repository: https://github.com/codex-team/deploy
Report bug: https://github.com/codex-team/deploy/issues
"""

from aiohttp import web
import asyncio
import os


class DeployServer(object):

    def __init__(self, params):
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
        self.SERVER_ADDRESS = params.get('server_address')
        self.WEB_PORT = params.get('port')
        self.DEPLOY = params.get('deploy', '')
        self.WEB_URI = params.get('uri', '/callback')
        self.BRANCH = 'refs/heads/' + params.get('branch', 'master')

        self.show_welcome_message()
        self.run()

    def show_welcome_message(self):
        """
        Show welcome message with set up guide
        """
        # hack for showing correct webhook url for ngrok urls
        try:
            if self.SERVER_ADDRESS[-8:] != 'ngrok.io':
                URL = '{}:{}{}'.format(self.SERVER_ADDRESS, self.WEB_PORT, self.WEB_URI)
            else:
                URL = '{}{}'.format(self.SERVER_ADDRESS, self.WEB_URI)
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

    async def github_callback(self, request):
        """
        Web App function for processing callback
        """
        try:
            data = await request.json()
            headers = request.headers
            event = headers.get("X-GitHub-Event", "")

            if event == "push":
                ref = data.get("ref", "")

                if self.BRANCH:
                    os.system(self.DEPLOY)

                print('Got a {} event in {} branch.'.format(event, data.get("ref")))

        except Exception as e:
            print("[github callback] Message process error: [%s]" % e)

        return web.Response(text='OK')

    def run(self):
        """
        Run aiohttp app on your server
        """
        loop = asyncio.get_event_loop()
        app = web.Application(loop=loop)
        app.router.add_post('/callback', self.github_callback)
        web.run_app(app, port=self.WEB_PORT)
