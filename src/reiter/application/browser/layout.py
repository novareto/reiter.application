from reiter.application.browser.registries import UIRegistry


def render_template(template, **ns):
    return template.render(**ns)


def ui_layout(registry: UIRegistry):
    def render_layout(template, layout_name=None, request=None, **ns):
        layout = registry.get_layout(request, layout_name)
        content = template.render(
            macros=layout.macros, request=request, **ns)
        if request is not None:
            path = request.environ["PATH_INFO"]
            baseurl = "{}://{}{}/".format(
                request.environ["wsgi.url_scheme"],
                request.environ["HTTP_HOST"],
                request.environ["SCRIPT_NAME"],
            )
            return layout.render(
                content,
                path=path,
                baseurl=baseurl,
                request=request,
                **ns
            )
        return layout.render(content, request=request, **ns)
    return render_layout
