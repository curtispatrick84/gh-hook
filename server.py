#!/usr/bin/env python
import hug
import logging
import json
import requests
import os
import uuid
from subprocess import Popen, PIPE

USER = os.environ.get('GH_USER')
TOKEN = os.environ.get('GH_TOKEN')

logging.getLogger("requests").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def createstatus(url, state, context=None, description=None, target=None):
    data = {'state': state}

    if context is not None:
        data['context'] = context

    if description is not None:
        data['description'] = description

    if target is not None:
        data['target_url'] = target

    response = requests.post(
        url,
        auth=(USER, TOKEN),
        headers={'content-type': 'application/json'},
        data=json.dumps(data),
        verify=False
    )


def processpullrequest(pr):
    createstatus(
        url=pr['statuses_url'],
        state='pending',
        description='Initializing',
        context='gh-hook'
    )

    temprepo = uuid.uuid4()

    gitcommand = f"/usr/bin/git clone -b {pr['head']['ref']} --depth=1 https://github.com/{pr['head']['repo']['full_name']} ./{temprepo}"

    git_query = Popen(gitcommand.split(), cwd='./', stdout=PIPE, stderr=PIPE)
    (git_status, error) = git_query.communicate()

    if git_query.poll() == 0:
        createstatus(
            url=pr['statuses_url'],
            state='pending',
            description='Installing dependencies',
            context='gh-hook'
        )
        npm_install = Popen(['npm', 'install'], cwd=f'./{temprepo}', stdout=PIPE, stderr=PIPE)
        (npm_status, error) = npm_install.communicate()

        if npm_status == 0:
            createstatus(
                url=pr['statuses_url'],
                state='pending',
                description='Running tests',
                context='gh-hook'
            )
            test = Popen(['npm', 'test'], cwd=f'./{temprepo}', stdout=PIPE, stderr=PIPE)
            (test_status, error) = test.communicate()

            if test_status == 0:
                createstatus(
                    url=pr['statuses_url'],
                    state='success',
                    description='All tests passed',
                    context='gh-hook'
                )
            else:
                createstatus(
                    url=pr['statuses_url'],
                    state='failure',
                    description='One or more tests failed',
                    context='gh-hook'
                )
        else:
            createstatus(
                url=pr['statuses_url'],
                state='failure',
                description='Failed to install dependencies!',
                context='gh-hook'
            )
    else:
        createstatus(
            url=pr['statuses_url'],
            state='failure',
            description='Unable to clone git repo!',
            context='gh-hook'
        )


@hug.post(versions=1)
def listen(request, body):
    logging.info("Received new event")

    if 'X-GITHUB-EVENT' not in request.headers:
        logging.debug("GitHub event header not set - Ignoring")
        return

    if request.headers['X-GITHUB-EVENT'] == 'pull_request':
        logging.debug("GitHub pull request event received")

        event = json.loads(body['payload'])

        if 'opened' in event['action'] || event['action'] == 'synchronize':
            processpullrequest(event['pull_request'])


@hug.not_found()
def not_found_handler():
    return "Not Found"


if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(funcName)s: %(message)s', level=logging.DEBUG)

    hug.API(__name__).http.serve(port=8080)
