from django.conf import settings  # import the settings file


def _env_color(env):
    if env == "production":
        return '#FF4136'
    elif env == 'staging':
        return '#FFDC00'
    else:
        return '#7FDBFF'


def django_env(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'DJANGO_ENV': settings.DJANGO_ENV, 'DJANGO_ENV_COLOR': _env_color(settings.DJANGO_ENV)}
