from hashlib import md5
from urllib import urlencode
import httplib
import re

def url_exists(site, path):
    try:
        conn = httplib.HTTPConnection(site)
        conn.request('HEAD', path)
        response = conn.getresponse()
        conn.close()
        return response.status == 200
    except:
        return False


def pavatar(url):
    if not re.match("^http://.+", str(url)):
        return False

    sep = url.find('/', 8)
    host = ""
    path = ""
    if sep == -1:
        host = url[7:]
    else:
        host = url[7:sep]
        path = url[sep:]

    if not path.endswith('/'):
        path += "/"
    path += "pavatar.png"

    if url_exists(host, path):
        return "http://" + host + path
    else:
        return False

def gravatar(email):
    url = "http://www.gravatar.com/avatar.php?"
    url += urlencode({'gravatar_id': md5(email.lower()).hexdigest(),
                      'size': str(80)})
    return url
