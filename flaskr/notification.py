import pycurl
import json
from io import BytesIO, StringIO


class Curl(object):
    def __init__(self):
        self.buffer = BytesIO()
        self.curl = pycurl.Curl()

    def __del__(self):
        pass

    def curl_request(self, url, request_type, json_info=''):
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.HTTPHEADER, [
            'Content-type:application/json;charset=utf-8'
        ])
        if request_type == 'GET':
            r_type = self.curl.GET
        elif request_type == 'POST':
            r_type = self.curl.POST
            self.curl.setopt(self.curl.READDATA, StringIO(json.dumps(json_info)))
            self.curl.setopt(self.curl.POSTFIELDSIZE, len(json.dumps(json_info)))
        else:
            return False

        self.curl.setopt(r_type, 1)
        self.curl.setopt(self.curl.WRITEDATA, self.buffer)
        self.curl.setopt(self.curl.SSL_VERIFYPEER, False)
        self.curl.perform()
        self.curl.close()
        return self.buffer.getvalue()

        # body = self.buffer.getvalue()
        # # print(url)
        # # print(body.decode('iso-8859-1'))
        # return json.loads(body)
        # print(self.buffer.getvalue().decode('utf-8'))

