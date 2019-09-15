import logging
import socket
import sys

def retrieve_url(url):
    """
    return bytes of the body of the document at url
    """

    return b"this is unlikely to be correct"

if __name__ == "__main__":
    sys.stdout.buffer.write(retrieve_url(sys.argv[1])) # pylint: disable=no-member
