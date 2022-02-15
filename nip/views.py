from django.shortcuts import render


def model(request, pk):
    context = {'data':{'input': {'value': pk}}}
    return render(request, 'table.html', context)
