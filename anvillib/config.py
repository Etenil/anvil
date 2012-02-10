import ConfigParser

# This is a bullshit module used to contain configuration.
_values = {'port': '80',
           'mode': 'http',
           'home_dir': './',
           'db.name': 'anvil',
           'db.user': 'anvil',
           'db.pwd': 'anvil',
           'db.host': 'localhost',
           'prefix': '',
           'title': 'Anvil'}

prefix = ""

def val(key):
    global _values
    if key in _values:
        return _values[key]
    else:
        return None

def load_conf():
    conf = ConfigParser.RawConfigParser()
    conf.read("/etc/anvil.ini")
    global _values

    if conf.has_option('anvil', 'port'):
        _values['port'] = conf.get('anvil', 'port')

    if conf.has_option('anvil', 'mode'):
        _values['mode'] = conf.get('anvil', 'mode')

    if conf.has_option('anvil', 'home_dir'):
        _values['home_dir'] = conf.get('anvil', 'home_dir')

    if conf.has_option('db', 'name'):
        _values['db.name'] = conf.get('db', 'name')

    if conf.has_option('db', 'user'):
        _values['db.user'] = conf.get('db', 'user')

    if conf.has_option('db', 'pwd'):
        _values['db.pwd'] = conf.get('db', 'pwd')

    if conf.has_option('db', 'host'):
        _values['db.host'] = conf.get('db', 'host')

    if conf.has_option('anvil', 'title'):
        _values['title'] = conf.get('anvil', 'title')

    if conf.has_option('anvil', 'prefix'):
        _values['prefix'] = conf.get('anvil', 'prefix')
        global prefix
        prefix = _values['prefix']