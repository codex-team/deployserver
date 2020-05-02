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
import re

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

    params['host'] : string
        (optional) DeployServer will listen this interface.
        default: '0.0.0.0'
        example: 'localhost' or '0.0.0.0'

    params['branch'] : string
        (optional) Which branch push event should initiate deploy function.
        default: 'master'
        example: 'current-sprint'
                 'ver2'

    params['branches'] : list of dict
        (optional) List of branches which push event should initiate deploy
        default: []
        example: [
                    {
                        'name': 'master',
                        'script': '/var/www/myProject/deploy.sh'
                    },
                    {
                        'regexp': r'testing/.*',
                        'script': '/var/www/myProject/deploy.sh'
                    }
                ]

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
        'host': settings.get('host', '0.0.0.0'),
        'port': settings.get('port'),
        'deploy': settings.get('deploy', ''),
        'uri': settings.get('uri', '/callback'),
        'branch': 'refs/heads/' + settings.get('branch', 'master'),
        'branches': settings.get('branches', []),
        'secret_token': settings.get('secret_token', None)
    }

    # check all regexps in branches
    for val in params['branches']:
        if val.get('regexp', False):
            try:
                val['regexp'] = re.compile(val.get('regexp'))
            except:
                print('Can not compile regexp' + val['regexp'] + ' in branches config')
                exit()

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
                  'Please set up a new webhook in project settings with following params:\n\n' \
                  'GitHub:\n' \
                  '- Payload URL: ' + URL + '\n' \
                  '- Content type: application/json \n' \
                  + ('- Secret: ' + params['secret_token'] + '\n' if params['secret_token'] else '') + \
                  '- Which events would you like to trigger this webhook?\n'\
                  '  [x] Just the push event.\n' \
                  '\n' \
                  'BitBucket:\n' \
                  '- URL: ' + URL + '\n' \
                  '- Triggers (Choose from a full list of triggers):\n' \
                  '  [x] Repository - Push\n' \
                  '  [x] Pull Request - Merged\n' \
                  '\n' \
                  'Web Application logs:'

        print(message)

    def run():
        """
        Run aiohttp app on your server
        """
        loop = asyncio.get_event_loop()
        app = web.Application(loop=loop)
        app.router.add_post(params['uri'], callback)
        web.run_app(app, host=params['host'], port=params['port'])

    async def process_gh_request(request):
        def verify_callback(signature, body):
            if not params['secret_token']:
                return True

            if not signature.startswith("sha1="):
                return False

            return signature[5:] == hmac.new(params['secret_token'].encode(), body, hashlib.sha1).hexdigest()

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
                if params.get('deploy', False):
                    os.system(params['deploy'])
                    return

            # current branch name without "refs/heads/"
            current_branch = ref[11:]

            _check_and_deploy_branches(current_branch)

    async def process_bb_request(request):
        data = await request.json()
        headers = request.headers
        event = headers.get('X-Event-Key', '')
        branch = ''

        can_deploy = False

        if event == 'repo:push':
            changes = data.get('push').get('changes', [{}])
            new_changes = changes[0].get('new', {})
            push_type = new_changes.get('type', None)

            if push_type is None or push_type != 'branch':
                return

            branch = new_changes.get('name', '')

            print('Got a {} event in {} branch.'.format(event, branch))

            # params branch name without "refs/heads/"
            if params['branch'][11:] == branch:
                can_deploy = True

        elif event == 'pullrequest:fulfilled':
            pullrequest = data.get('pullrequest')
            branch = pullrequest.get('destination').get('branch', {}).get('name', '')

            print('Got a {} event into {} branch.'.format(event, branch))

            # params branch name without "refs/heads/"
            if params['branch'][11:] == branch:
                can_deploy = True

        # if can deploy single branch config do it and exit
        if can_deploy:
            if params.get('deploy', False):
                print('Run deploy script...')
                os.system(params['deploy'])
                return

        # else check and deploy multiple branch config
        _check_and_deploy_branches(branch)

    async def callback(request):
        """
        Web App function for processing callback
        """
        try:
            user_agent = request.headers.get('User-Agent', '')

            if user_agent.startswith('Bitbucket-Webhooks'):
                await process_bb_request(request)
            elif user_agent.startswith('GitHub-Hookshot'):
                await process_gh_request(request)


        except Exception as e:
            print("[callback] Message process error: [%s]" % e)

        return web.Response(text='OK')

    def _check_and_deploy_branches(current_branch):
        """
        Compare current branch name with name or regexp
        in params['branches'] and run needed deploy script
        """
        for item in params['branches']:
            branch_name = item.get('name', None)
            regexp = item.get('regexp', None)

            can_deploy = False

            if branch_name and branch_name == current_branch:
                can_deploy = True
            elif regexp and re.match(regexp, current_branch):
                can_deploy = True

            if can_deploy:
                script = item.get('script', None)

                print('Run deploy script [{}] for branch [{}]...'.format(script, current_branch))

                os.system(script)

    show_welcome_message()
    run()
