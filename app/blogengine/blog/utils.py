from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Post, Commets, Profile
from .forms import CommentForm


class ObjectDetailMixin:
    model = None
    template = None

    def get(self, request, slug, *args, **kwargs):
        commnet = Commets.objects.filter(post__slug=slug) # ищем все коментарии , которые на данном странице с постом
        obj = get_object_or_404(Post, slug__iexact=slug)
        form = CommentForm()
        # Определение , является ли текущеий пользователь автором поста
        context = Profile.objects.filter(author=request.user)
        if context:
            context = context[0]
        return render(request, self.template,
                      context={Post.__name__.lower(): obj,
                               'admin_object': obj, 'detail': True, "comments": commnet, "form": form,
                               'current_user':context})

    def post(self, request, slug):
        form = CommentForm(request.POST)
        post = get_object_or_404(Post, slug__iexact=slug)
        #  проверка того , что форма подходит под все параметры Django, указанные в моделях и в фале форм
        if form.is_valid():
            form = form.save(commit=False)
            #  Сохраняем текущего пользователя, и таким образом понимаем, кто написал комментарий
            form.user = request.user
            form.post = post # Сохраняем текущий пост в модели коментариев
            form.save()
            return redirect('post_detail_url', slug)

    def comment_delete(request, id, slug):
        """
        Функция фильтрации и удаления коментария пользователя
        :param id: айди самого окментария, передается из html
        :param slug: url поста, передаётся из html
        """
        Commets.objects.filter(id=id).delete()
        return redirect('post_detail_url', slug)


class ObjectCreateMixin:
    model_form = None
    template = None

    def get(self, request):
        form = self.model_form()
        return render(request, self.template, context={'form': form})

    def post(self, request):

        bound_form = self.model_form(request.POST, request.FILES)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            #  Сохраняем текущего пользователя, который создал пост
            new_obj.author_post = request.user
            new_obj.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form})


class ObjectUpdateMixin:
    model = None
    model_form = None
    template = None

    def get(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(instance=obj)
        return render(request, self.template, context={'form': bound_form,
                                                       'self.model__name__.lower()': obj})

    def post(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(request.POST, request.FILES, instance=obj)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form,
                                                       'self.model__name__.lower()': obj})


class ObjectDeleteMixin:
    model = None
    template = None
    redirect_url = None

    def get(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        return render(request, self.template, context={self.model.__name__.lower(): obj})

    def post(self, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        obj.delete()
        return redirect(reverse(self.redirect_url))
