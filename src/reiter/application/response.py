import horseman.response


class Response(horseman.response.Response):

    @classmethod
    def from_template(
            cls, template: str, code: HTTPCode = 200,
            headers: Optional[dict] = None, **namespace):

        if request := namespace.get('request') is not None:
            if layout_name := namespace.get('layout_name') is not None:
                layout = request.app.ui.layout(request, layout_name)
                content = template.render(macros=layout.macros, **namespace)
                path = request.environ["PATH_INFO"]
                baseurl = "{}://{}{}/".format(
                    request.environ["wsgi.url_scheme"],
                    request.environ["HTTP_HOST"],
                    request.environ["SCRIPT_NAME"],
                )
                body = layout.render(
                    content,
                    path=path,
                    baseurl=baseurl,
                    request=request,
                    context=object(),
                    user=None,
                    messages=flash_messages,
                    view=instance,
                )
                return horseman.response.reply(
                    body=body,
                    headers={"Content-Type": "text/html; charset=utf-8"}
            )

        return cls(code, body, headers)
