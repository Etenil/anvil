import web

db = web.database(dbn='mysql', user='anvil', pw='anvil', db='anvil')

title = "Anvil"

web.config.debug = False
