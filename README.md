# http_server
Simple Python http server for testing Esphome http_request component

Will respond to POSTs with Transfer-Encoding: chunked or as plain text

Edit content.txt to change the content sent back to the client

Optional chunk size

Best to run in a virtual environment

Python httpserver.py -h shows the options

e.g.

Python httpserver.py -rc 200 -ck -cs 10

Response code 201

Chunked response

Chunk size 10 bytes

Access the server by default on port 8000. To change the port start the server using the -p <port> argument 

E.g. http://127.0.0.1:8000

For a sanity check of the server use curl to test it

E.g.

curl -v -i -k  --request POST --data "hello" http://127.0.0.1:8000
