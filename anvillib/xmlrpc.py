import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:300/")

def _check_ack(ret, error):
    if str(ret) == "OK":
        return True
    else:
        raise Exception, error

def create_user(username):
    return _check_ack(proxy.create_user(username),
                      "User couldn't be created.")

def delete_user(username):
    return _check_ack(proxy.delete_user(username),
                      "User couldn't be deleted.")

def delete_branch(username, branch):
    return _check_ack(proxy.delete_branch(username, branch),
                      "Branch couldn't be deleted.")
