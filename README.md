# http_server
Simple Python http server for testing Esphome http_request component

Will respond to POSTs with Transfer-Encoding: chunked or as plain text

Optional chunk size

Best to run in a virtual environment

Python httpserver.py -h shows the options

e.g.

Python httpserver.py -rc 200 -ck -cs 10

Response code 201

Chunked response

Chunk size 10 bytes

