import web
import model
from web.contrib.template import render_mako

urls = (
    '/(.*)', 'test'
    )

app = web.application(urls, globals())
render = render_mako(
        directories=['templates'],
        input_encoding='utf-8',
        output_encoding='utf-8',
        )

title = "Anvil"


class test:
    def GET(self, name):
        return render.toto(name=name,
                           title=title,
                           htTitle="Welcome to Anvil!")
    #end GET
#end test

if __name__ == "__main__": app.run()
