from __future__ import annotations

from django.db.models import F
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from django_admin_home.models import MenuAccess, MenuFavorite


@require_POST
def toggle_favorite(request):
    menu_key = (request.POST.get("menu_key") or "").strip()
    if not menu_key:
        return HttpResponseBadRequest("menu_key is required")

    obj, created = MenuFavorite.objects.get_or_create(user=request.user, menu_key=menu_key)
    if not created:
        obj.delete()
        is_favorite = False
    else:
        is_favorite = True
    return JsonResponse({"menu_key": menu_key, "is_favorite": is_favorite})


@require_POST
def track_access(request):
    menu_key = (request.POST.get("menu_key") or "").strip()
    if not menu_key:
        return HttpResponseBadRequest("menu_key is required")

    obj, created = MenuAccess.objects.get_or_create(user=request.user, menu_key=menu_key, defaults={"access_count": 1})
    if not created:
        MenuAccess.objects.filter(pk=obj.pk).update(access_count=F("access_count") + 1)
    return JsonResponse({"menu_key": menu_key, "ok": True})
