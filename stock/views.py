from django.http import JsonResponse

from .api.kiwoom.kiwoom import Kiwoom


# Create your views here.
def index(request):
    return JsonResponse({'result': 'index'})


def kiwoom(request):
    api = Kiwoom()
    api.do()

    return JsonResponse({'result': 'index'})
