#!/usr/bin/env python
import hug
import logging
import json


@hug.post(versions=1)
def listen(request, body):
    logging.debug("Received new event")

    if 'X-GITHUB-EVENT' not in request.headers:
        logging.debug("GitHub event header not set - Ignoring")
        return
    else:
        logging.debug(str(body))


@hug.not_found()
def not_found_handler():
    return "Not Found"


if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(funcName)s: %(message)s', level=logging.INFO)

    hug.API(__name__).http.serve(port=8080)
