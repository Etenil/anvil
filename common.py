import web
from web.contrib.template import render_mako

# Common variables.
db = web.database(dbn='mysql', user='anvil', pw='anvil', db='anvil')
title = "Anvil"
host = "anvil"
session = None
env_info = None
msgs = None
render = render = render_mako(
    directories=['templates'],
    input_encoding='utf-8',
    output_encoding='utf-8',
    )

web.config.debug = False
