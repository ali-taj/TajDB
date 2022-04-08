import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urls import valid_urls
import socketserver

hostName = "0.0.0.0"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):

    def _set_headers(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def main(self, request):
        url_path = request.path
        query_dictionary = {}
        if "?" in url_path:
            for key in url_path.split("/?")[1].split("&"):
                query_dictionary[key.split("=")[0].strip()] = key.split("=")[1].split(",")
            url_path = url_path.split("/?")[0]

        url = url_path.split("/")[1]

        if url not in valid_urls:
            response = {"NOT_FOUND": f"url '{url}' not found!"}
            request._set_headers(404)
            request.wfile.write(json.dumps(response).encode(encoding='utf_8'))
        else:
            class_name = valid_urls[url]
            class_function = url_path.split("/")[2] if len(url_path.split("/")) > 2 else None
            data_id = url_path.split("/")[3] if len(url_path.split("/")) > 3 else None
            inefficient_data = url_path.split("/")[4] if len(url_path.split("/")) > 4 else None
            if inefficient_data is not None:
                response = {"KEY_ERROR": inefficient_data}
                request._set_headers(400)
                request.wfile.write(json.dumps(response).encode(encoding='utf_8'))
            else:
                try:
                    if class_function is not None:
                        call_able_function = eval("class_name." + class_function)

                    else:
                        call_able_function = eval("class_name")

                    if query_dictionary != {}:
                        request["query"] = query_dictionary

                    if data_id is not None and data_id != "":
                        api_response = call_able_function(class_name, request=request, id=data_id)
                    else:
                        api_response = call_able_function(class_name, request=request)

                    request._set_headers(api_response["status"])
                    request.wfile.write(json.dumps(api_response["response"]).encode(encoding='utf_8'))
                except AttributeError as e:
                    response = {"BAD_REQUEST": f"{class_function} is not allowed in {class_name}."}
                    request._set_headers(400)
                    request.wfile.write(json.dumps(response).encode(encoding='utf_8'))
                except Exception as e:
                    response = {"BAD_REQUEST": str(e)}
                    request._set_headers(400)
                    request.wfile.write(json.dumps(response).encode(encoding='utf_8'))

    def do_GET(self):
        print(8, self.server.socket)
        print(9, self.client_address)
        self.main(self)

    def do_POST(self):
        self.main(self)


if __name__ == "__main__":
    with socketserver.TCPServer((hostName, serverPort), MyServer) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print("Server started http://%s:%s" % (hostName, serverPort))
        server.serve_forever()

    # webServer = HTTPServer((hostName, serverPort), MyServer)

    # webServer.socket = ssl.wrap_socket(
    #     webServer.socket,
    #     keyfile="path/to/key.pem",
    #     certfile='path/to/cert.pem',
    #     server_side=True)

    # try:
    #     webServer.serve_forever()
    # except:
    #     pass
