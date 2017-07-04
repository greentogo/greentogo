from rest_framework.response import Response


def jsend_success(data, status=200):
    return Response({"status": "success", "data": data}, status=status)


def jsend_fail(data, status=400):
    return Response({"status": "fail", "data": data}, status=status)


def jsend_error(message, status=500):
    return Response({"status": "error", "message": message}, status=status)
