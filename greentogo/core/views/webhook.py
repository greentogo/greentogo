import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.stripe import stripe


@require_POST
@csrf_exempt
def stripe_webhook(request):
    logger = logging.getLogger('stripe_webhook')

    # Retrieve the request's body and parse it as JSON
    event_json = json.loads(request.body.decode("utf-8"))
    logger.info(event_json)

    # Do something with event_json
    return HttpResponse(status=200)
