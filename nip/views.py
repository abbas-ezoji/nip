from django.shortcuts import render


def model(request, pk):
    context = {'data': {'pk': pk}}
    return render(request, 'table.html', context)
