from web.form import Textbox

class AjaxTextbox(Textbox):
    ajax_target = "/"

    def __init__(self, name, target, *validators, **attrs):
        self.ajax_target = target
        super(self.__class__, self).__init__(name, validators, attrs)

    def render(self):
        stuff = super(self.__class__, self).render()
        stuff += '<div id="autocomplete_choices_%s" class="autocomplete"></div>' % self.name
        stuff += '<script type="text/javascript">new Ajax.Autocompleter("%s", "autocomplete_choices_%s", "%s", {paramName: "value", minChars: 2, tokens: ","});</script>' % (self.id, self.id, self.ajax_target)
        return stuff
