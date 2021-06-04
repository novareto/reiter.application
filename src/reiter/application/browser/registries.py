import reg
import horseman.response


generic = object


class UIRegistry:

    def __init__(self, default_layout_name='default'):
        self.default_layout_name = default_layout_name

    @reg.dispatch_method(
        reg.match_instance('request'), reg.match_key('name'))
    def layout(self, request, name):
        raise LookupError("Unknown layout.")

    def register_layout(self, request, name: str = None):
        if name is None:
            name = self.default_layout_name
        def add_layout(layout):
            return self.layout.register(
                reg.methodify(layout), request=request, name=name)
        return add_layout

    def get_layout(self, request, name=...):
        if name is ...:
            name = self.default_layout_name
        return self.layout(request, name)

    @reg.dispatch_method(
        reg.match_instance('request'),
        reg.match_key("name"),
        reg.match_instance('view'),
    )
    def slot(self, request, name, view):
        raise LookupError("Unknown slot.")

    def register_slot(self, request, name, view=generic):
        def add_slot(slot):
            self.slot.register(
                reg.methodify(slot), request=request, name=name, view=view)
            return slot
        return add_slot

    def render(self, template, request, layout=..., **namespace):
        namespace['request'] = request
        namespace['ui'] = self
        if layout is not None:
            layout = self.get_layout(request, name=layout)
            content = template.render(macros=layout.macros, **namespace)
            namespace['path'] = request.environ["PATH_INFO"]
            namespace['baseurl'] = "{}://{}{}/".format(
                request.environ["wsgi.url_scheme"],
                request.environ["HTTP_HOST"],
                request.environ["SCRIPT_NAME"]
            )
            return layout.render(content, **namespace)
        return template.render(**namespace)

    def response(self, template, request, code=200, headers=None, **kwargs):
        if not headers:
            headers = {"Content-Type": "text/html; charset=utf-8"}
        elif 'Content-Type' not in headers:
            headers["Content-Type"] = "text/html; charset=utf-8"
        return horseman.response.reply(
            code=code,
            body=self.render(template, request, **kwargs),
            headers=headers,
        )
