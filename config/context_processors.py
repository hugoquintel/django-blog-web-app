def GET_params_str(request):
    result = "&".join(
        f"{key}={value}"
        for key, value in request.GET.items()
        if key not in {"page", "snapshot"}
    )

    return {"GET_params_str": result}
