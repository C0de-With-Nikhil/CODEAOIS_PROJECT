def route_task(task):

    if len(task) < 50:
        return "local_model"

    return "cloud_model"