from django.conf import settings  # import the settings file


def django_env(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'DJANGO_ENV': settings.DJANGO_ENV}
