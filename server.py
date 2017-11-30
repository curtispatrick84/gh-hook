#!/usr/bin/env python
import hug
import logging
import json
import requests


def createstatus(url, state, context=None, description=None, target=None):
    data = {'state': state}

    if context is not None:
        data['context'] = context

    if description is not None:
        data['description'] = description

    if target is not None:
        data['target_url'] = target

    requests.post(
        url,
        auth=(USER, TOKEN),
        headers={'content-type': 'application/json'},
        data=json.dumps(data),
        verify=False
    )


@hug.post(versions=1)
def listen(request, body):
    logging.info("Received new event")

    if 'X-GITHUB-EVENT' not in request.headers:
        logging.info("GitHub event header not set - Ignoring")
        return

    if request.headers['X-GITHUB-EVENT'] == 'pull_request':
        logging.debug("GitHub pull request event received")

        if body['action'] == 'opened':
            createstatus(
                url=pr['statuses_url'],
                state='pending',
                description='Initializing',
                context='gh-runner'
            )


@hug.not_found()
def not_found_handler():
    return "Not Found"


if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(funcName)s: %(message)s', level=logging.INFO)

    hug.API(__name__).http.serve(port=8080)
