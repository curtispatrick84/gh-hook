#!/usr/bin/env python
import hug
import logging
import json
import requests
import os

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

    logging.debug(data)
    logging.debug(response.status_code)
    logging.debug(response.json())


@hug.post(versions=1)
def listen(request, body):
    logging.info("Received new event")

    if 'X-GITHUB-EVENT' not in request.headers:
        logging.debug("GitHub event header not set - Ignoring")
        return

    if request.headers['X-GITHUB-EVENT'] == 'pull_request':
        logging.debug("GitHub pull request event received")

        event = json.loads(body['payload'])

        if 'opened' in event['action']:
            createstatus(
                url=event['pull_request']['statuses_url'],
                state='pending',
                description='Initializing',
                context='gh-hook'
            )


@hug.not_found()
def not_found_handler():
    return "Not Found"


if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(funcName)s: %(message)s', level=logging.DEBUG)

    hug.API(__name__).http.serve(port=8080)
