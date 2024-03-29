from django.shortcuts import render
from authentication.models import UserProfile
from nip.models import ShiftAssignments
from django.http import HttpResponse


def model(request, pk):
    user = request.user
    print(user)
    context = {'data': {'input': {'value': pk}}}
    if user.is_anonymous:
        return HttpResponse('شما به این شیفت دسترسی ندارین ... !', status=403)
    if user.is_superuser:
        return render(request, 'nip/table.html', context)

    profile = UserProfile.objects.get(User=user)
    user_work_sec = profile.WorkSection
    assignment_id = pk
    shift_ass = ShiftAssignments.objects.get(pk=assignment_id)
    shift_work_sec = shift_ass.WorkSection

    # print(f'user_work_sec = {user_work_sec.id}, shift_work_sec = {shift_work_sec.id}')

    if user_work_sec.id != shift_work_sec.id:
        return HttpResponse('شما به این شیفت دسترسی ندارین ... !', status=401)

    return render(request, 'nip/table.html', context)
