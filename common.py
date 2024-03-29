import web
import os
from anvillib import config
from web.contrib.template import render_mako

web.config.debug = False
web.config.debug_sql = False

# Common variables.
db = web.database(dbn='mysql', user=config.val('db.user'),
                  pw=config.val('db.pwd'), db=config.val('db.name'))
session = None
env_info = None
msgs = None
render = render = render_mako(
    directories=['templates'],
    input_encoding='utf-8',
    output_encoding='utf-8',
    )

os.environ['SCRIPT_NAME'] = config.val('prefix')
os.environ['REAL_SCRIPT_NAME'] = config.val('prefix')
