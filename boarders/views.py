from django.shortcuts import render, get_object_or_404
from .models import Boarder
from django.contrib.auth.decorators import login_required
from .forms import BoarderForm
from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
@login_required
def boarder_list(request):
    boarders = Boarder.objects.all()
    return render(request, 'boarders/boarder_list.html', {'boarders': boarders})

@login_required
def add_boarder(request):
    if request.method == 'POST':
        form = BoarderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boarder-list')
    else:
        form = BoarderForm()
    return render(request, 'boarders/add_boarder.html', {'form': form})

@login_required
def edit_boarder(request, pk):
    boarder = get_object_or_404(Boarder, pk=pk)

    if request.method == 'POST':
        form = BoarderForm(request.POST, instance=boarder)
        if form.is_valid():
            form.save()
            return redirect('boarder-list')
    else:
        form = BoarderForm(instance=boarder)

    return render(request, 'boarders/edit_boarder.html', {'form': form})


class BoarderDeleteView(LoginRequiredMixin, DeleteView):
    model = Boarder
    template_name = 'boarders/delete_boarder.html'
    success_url = reverse_lazy('boarder-list')