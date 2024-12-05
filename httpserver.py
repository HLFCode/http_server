#!/usr/bin/env python

# Original: https://github.com/ksmith97/GzipSimpleHTTPServer/blob/master/GzipSimpleHTTPServer.py

"""Simple HTTP Server.

Specific simple htttp

"""


__version__ = "1.1"

#__all__ = ["SimpleHTTPRequestHandler"]

import os
import time
import logging
import os.path
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

OPTIONS = None

def parse_options():
    # Option parsing logic.
    global OPTIONS
    parser = argparse.ArgumentParser(description="Simple http server for testing transfer-encoding: chunked")
    parser.add_argument("-ck", "--chunked", 
                        dest="chunked", 
                        help="If set the response will use Transfer-Encoding: chunked [False]",
                        action="store_true"
                        )
    parser.add_argument("-cs", "--chunk-size", 
                        dest="chunk_size", 
                        help="Chunk size for chunked transfers [1024]", 
                        type=int, 
                        default=1024)
    parser.add_argument("-sc", "--single-chunk", 
                        dest="single_chunk", 
                        help="Sends chunked response in a single transmission [False]", 
                        action='store_true')
    parser.add_argument("-p", "--port", dest="port", type=int,
                        help="The port to serve the files on [8000]",
                        default=8000)
    parser.add_argument("-rc", "--response-code", dest="response_code", type=int,
                        help="Response code to use [200]", 
                        default=200)
    parser.add_argument("-w", "--waitms", 
                        dest="wait_ms", 
                        help="Wait time in ms between chunked responses [0]", 
                        type=int, 
                        default=0)
    parser.add_argument("-f", "--content-file", 
                        dest="content_file", 
                        help="File name containing the content to dispatch [content.txt]", 
                        default="content.txt")
    OPTIONS = parser.parse_args()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler 

    """

    server_version = "SimpleHTTP/" + __version__
    content = "dummy content"

    def write_content(self, content, log = True) -> bool:
        if log:
            logging.debug("Sent: '" + content.replace("\r","<cr>").replace("\n", "<lf>") + "'")
        try:
            if isinstance(content, str):
                self.wfile.write(content.encode('utf-8'))
            else:
                self.wfile.write(content)
        except Exception as ex:
            logging.error(ex)
            return False
        return True

    def get_chunk(self, data) -> str:
        return '%X\r\n%s\r\n'%(len(data), data)
    
    def write_chunk(self, data) -> bool:
        tosend = self.get_chunk(data)
        logging.debug("Sent chunk: '" + tosend.replace("\r","<cr>").replace("\n", "<lf>") + "'")
        return self.write_content(tosend, False)

    def do_GET(self):
        """Serve a GET request."""
        logging.info("GET received")
        self.do_POST

    def do_PUT(self):
        logging.info("PUT received")
        self.do_POST()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nPOST Body:\n%s\n", str(self.path), str(self.headers).rstrip(), post_data.decode('utf-8'))

        self.send_response(int(OPTIONS.response_code))
        logging.debug("Sent response %d", int(OPTIONS.response_code))

        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Content-Type","application/json")

        if OPTIONS.chunked:
            logging.debug("Sending chunked...")
            self.send_header("Transfer-Encoding", "chunked")
        else:
            self.send_header("Content-Length", str(len(self.content)))
        self.end_headers()

        if OPTIONS.chunked:
            # Data is sent in a series of chunks. 
            # The Content-Length header is omitted in this case and at the beginning of each chunk you need to add the length of the current chunk in hexadecimal format, 
            # followed by \r\n and then the chunk itself, followed by another \r\n. 
            # The terminating chunk is a regular chunk, with the exception that its length is zero. 
            # It is followed by the trailer, which consists of a (possibly empty) sequence of header fields.
            chunk_size = OPTIONS.chunk_size
            index = 0
            waitms = OPTIONS.wait_ms
            content_data = ""
            while index < len(self.content):
                if index + chunk_size > len(self.content):
                    bytes_to_write = len(self.content) - index
                else:
                    bytes_to_write = chunk_size
                if OPTIONS.single_chunk:
                    content_data += self.get_chunk(self.content[index:index + bytes_to_write])
                elif not self.write_chunk(self.content[index:index + bytes_to_write]):
                    return
                index += chunk_size
                if waitms > 0:
                    logging.debug("Waiting " + str(waitms) + "ms")
                    time.sleep(waitms / 1000)
            # get/write the terminating (empty) chunk
            if OPTIONS.single_chunk:
                content_data += self.get_chunk('')
                self.write_content(content_data, True)
            else:
                self.write_chunk('')
        else:
            self.write_content(self.content)

    def do_HEAD(self):
        """Serve a HEAD request."""
        logging.info("HEAD request received")
        self.send_header("Content-Type","application/json")
        self.end_headers()

def run(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = HTTPServer):
    """Run the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the -p argument).

    """

    parse_options()
    port = OPTIONS.port
    server_address = ('', port)
    
    SimpleHTTPRequestHandler.protocol_version = "HTTP/1.1"
    SimpleHTTPRequestHandler.server_version = "HTTP/1.1"
    
    content_file = OPTIONS.content_file
    if os.path.exists(content_file):
        logging.info("Reading content from " + content_file)
        f = open(content_file, "r")
        content = f.read()
        f.close()
        SimpleHTTPRequestHandler.content = content
    else:
        logging.warning("File '" + OPTIONS.content_file + "' does not exist, reply content will be '" + SimpleHTTPRequestHandler.content + "'")

    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

    logging.info('Starting httpd on port %d...', port)
    if OPTIONS.chunked:
        logging.info("Transfer encoding chunked, chunk size %d", OPTIONS.chunk_size)
        if OPTIONS.single_chunk:
            logging.info("Sending data in a single transmission")
        else:
            logging.info("Sending data in one transmission per chunk")
        if OPTIONS.wait_ms > 0:
            logging.info("Each chunk will be delayed by " + str(OPTIONS.wait_ms) + "ms")

    logging.info("Press ctrl-c to exit")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopped httpd')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run()