import logging
import socket
import sys
import ssl


def res_for_transfer_encoding(response_body):
    final_chunk = b""
    while True:
        chunks = response_body.split(b'\r\n', 1)
        identifier = chunks[0]
        if identifier == b'0':
            break
        identifier_int = int(identifier, 16)
        partial_chunk = chunks[1]
        final_chunk = final_chunk + partial_chunk[:identifier_int]
        response_body = partial_chunk[identifier_int+2:]
    return final_chunk


def retrieve_url(url):
    if "http://" in url:
        url = url.replace("http://", '')
        count = url.count("/")
        if count != 0:
            _, path = url.split('/', 1)
            path = "/" + path
            if "/" in url:
                index = url.find("/")
                host = url[0:index]
        elif count == 0:
            path = "/"
            host = url

        if ':' in host:
            colon_position = host.split(":")
            port = int(colon_position[1])
            host = colon_position[0]
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((bytes(host, 'utf-8'), port))
            except socket.error:
                return None
            http_request = "GET {} HTTP/1.1\r\nHost: {}:{}\r\nConnection: close\r\n\r\n"
            http_request = http_request.format(path, host, port)
            client_socket.send(http_request.encode())
        else:
            port = 80
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((bytes(host, 'utf-8'), port))
            except socket.error:
                return None
            http_request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n"
            client_socket.send(http_request.encode())
        data = client_socket.recv(4096)

        while data != b'':
            response_body = data
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                response_body += data

            if b'200 OK' in response_body:

                if b'Transfer-Encoding: chunked\r\n' not in response_body:
                    data1 = response_body.split(b'\r\n\r\n', 1)
                    data = data1[1]
                    return data

                elif b'Transfer-Encoding: chunked\r\n' in response_body:
                    pos = response_body.find(b'\r\n\r\n')
                    data = response_body.strip(b'\r\n\r\n')
                    data = data.replace(b'\r\n\r\n', b'')
                    data = data[pos:]
                    data = res_for_transfer_encoding(data)
                    return data

                else:
                    return None

            else:
                if b'301 Moved Permanently' in response_body:
                    start_position = response_body.find(b'Location: ')
                    end_position = response_body.find(b'\r\nHost-Header')
                    redirected_url = response_body[start_position + 10:end_position]
                    redirected_url = redirected_url.decode("utf-8")
                    retrieve_url(redirected_url)

    elif "https://" in url:
        url = url.replace("https://", '')
        if "/" in url:
            index = url.split("/", 1)
            host = index[0]
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ss.connect((host, 443))
            client_socket = context.wrap_socket(ss)
        except:
            return None
        path = index[1]
        path = "/" + path

        https_request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n"
        client_socket.send(https_request.encode())
        data = client_socket.recv(4096)

        while data != b'':
            response_body = data
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break

                response_body += data

            if b'200 OK' in response_body:
                if b'Transfer-Encoding: chunked\r\n' in response_body:
                    pos = response_body.find(b'\r\n\r\n')
                    data = response_body.strip(b'\r\n\r\n')
                    data = data.replace(b'\r\n\r\n', b'')
                    data = data[pos:]
                    data = res_for_transfer_encoding(data)
                    return data


if __name__ == "__main__":
    sys.stdout.buffer.write(retrieve_url(sys.argv[1]))