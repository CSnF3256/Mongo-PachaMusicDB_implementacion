def app_context(request):
    return {
        "usuario_sesion": request.session.get("usuario"),
        "app_name": "PachaMusicDB MongoDB",
    }
