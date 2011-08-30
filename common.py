import web
import os
from web.contrib.template import render_mako

# Common variables.
db = web.database(dbn='mysql', user='anvil', pw='anvil', db='anvil')
title = "Anvil"
host = "bzr.ath.cx"
prefix = "/anvil"
session = None
env_info = None
msgs = None
render = render = render_mako(
    directories=['templates'],
    input_encoding='utf-8',
    output_encoding='utf-8',
    )

web.config.debug = False

os.environ['SCRIPT_NAME'] = prefix
os.environ['REAL_SCRIPT_NAME'] = prefix
