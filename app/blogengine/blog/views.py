# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Tag, Commets, Profile, Commets_profile
from .utils import ObjectDetailMixin, ObjectCreateMixin, ObjectUpdateMixin, ObjectDeleteMixin
from .forms import TagForm, PostForm, CommentFormForProfile
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
import mimetypes
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import  mm
from reportlab.lib.styles import  ParagraphStyle as PS
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.contrib.auth.models import User
from django.http import JsonResponse



def posts_list(request, pk=None):
    search_query = request.GET.get('search', '')

    if search_query:
        posts = Post.objects.filter(Q(title__icontains=search_query)| Q(body__icontains=search_query))
    else:
        """
       Сортировка вывода постов на главной странице, работает с помощью передавния переменной pk, и в зависимости
       от её значения посты сортируются по полям модели Post.

       """
        posts = Post.objects.all()
        if pk == "rating_up":
            posts = posts.order_by("rating")
        elif pk == "rating_down":
            posts = posts.order_by("-rating")
        elif pk == "date_up":
            posts = posts.order_by("date_pub")
        elif pk == "date_down":
            posts = posts.order_by("-date_pub")
        else:
            posts.order_by("date_pub")

    number_of_objects_on_page = 5
    paginator = Paginator(posts, number_of_objects_on_page)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    is_paginated = page.has_other_pages()

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    context = {'page_object': page,
               'is_paginated': is_paginated,
               'next_url': next_url,
               'prev_url': prev_url}

    return render(request, 'blog/index.html', context=context)


def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'blog/tags_list.html', context={'tags': tags})


class PostDetail(ObjectDetailMixin, View):
    """
   Для деталей конкретного поста нужно две модели, которые не имеют общей связей, поэтому нужно импортировать сразу две
   """
    model = Post, Commets
    template = 'blog/post_detail.html'


class TagDetail(ObjectDetailMixin, View):
    model = Tag
    template = 'blog/tag_detail.html'


class PostCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    model_form = PostForm
    template = 'blog/post_create.html'
    template_index = 'blog/post_create.html'
    raise_exception = True


class TagCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    model_form = TagForm
    template = 'blog/tag_create.html'
    template_index = 'blog/tags_list.html'
    raise_exception = True


class PostUpdate(LoginRequiredMixin, ObjectUpdateMixin, View):
    model = Post
    model_form = PostForm
    template = 'blog/post_update.html'
    raise_exception = True


class TagUpdate(LoginRequiredMixin, ObjectUpdateMixin, View):
    model = Tag
    model_form = TagForm
    template = 'blog/tag_update.html'
    raise_exception = True


class PostDelete(LoginRequiredMixin, ObjectDeleteMixin, View):
    model = Post
    template = 'blog/post_delete.html'
    redirect_url = 'posts_list_url'
    raise_exception = True


class TagDelete(LoginRequiredMixin, ObjectDeleteMixin, View):
    model = Tag
    template = 'blog/tag_delete.html'
    redirect_url = 'tags_list_url'
    raise_exception = True


def download_file_pdf(request, slug):
    """
   Функция для скачивания пдв файла в посте
   Для конвертирования текста из поля content в pdf , нужна специальная библеотека,
    в которую передаются параметры для обработки
   :param slug:  url текущего поста
   :return: возвращает ссылку на скачивания файла,
   для пользователя это выглядит как всплывающее окно с продложенем сохранить файл
   """
    # С помощью генератора берётся поле из можеди, поста на котором пользователь нажал скачать,
    # и поле переводится в стрингу для обработки
    your_string = '-'.join([str(i) for i in Post.objects.filter(slug=slug)])
    #  Добавление и настройка шрифтов
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    style = PS(name='NormalFreeSans', fontName='FreeSans', fontSize=12)
    # Настройка отступов и создание файля для хранения пдф на сервере
    doc = SimpleDocTemplate('blog/files/post.pdf', pagesize=letter,
                            rightMargin=25 * mm, leftMargin=25 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm)
    # Сопоставление текстовой стринги с телом поста и параметров настройки файла пдф
    content = []
    content.append(Paragraph(your_string, style))
    content.append(Spacer(1, 18))
    doc.build(content)
    the_file = 'blog/files/post.pdf'
    # Формирование ссылки на скачивание пдф файла с текущей страницы
    response = download(the_file, slug)
    return response


def download_file_txt(request, slug):
    """
    Функция для скачивания txt файла в посте
    Запись в файл осуществяется стандартными библиотеками питона
    :param slug:  url текущего поста
    :return: возвращает ссылку на скачивания файла,
    для пользователя это выглядит как всплывающее окно с продложенем сохранить файл
    """
    your_string = '-'.join([str(i) for i in Post.objects.filter(slug=slug)])
    f = open('blog/files/blog.txt', 'w')
    f.write(your_string)
    f.close()  # Закрытие файла нужно для дальнейшей работы с ним
    # Формирование ссылки на скачивание пдф файла с текущей страницы
    the_file = 'blog/files/blog.txt'
    response = download(the_file, slug)
    return response


def download(the_file, slug):
    """
   Функция для формирования ссылки для скачивания, а так же заворачивание файла с помощью библиотек в нужный респонс
   :param the_file: Файл для обработки
   :return:респонс с ссылкой на скачивание
   """
    filename = os.path.basename(the_file)
    chunk_size = 8192  # Размер символов в имени файла, используется стандартный для бд
    response = StreamingHttpResponse(FileWrapper(open(the_file, 'rb'), chunk_size),
                                     content_type=mimetypes.guess_type(the_file)[0])
    response['Content-Length'] = os.path.getsize(the_file)  # Определение длины файла
    response['Content-Disposition'] = "attachment; filename=%s" % filename  # Отображение при скачивании файла
    return response


def add_like(request, slug):
    """
    Функция для добавлления лайка, работатет прсотым методом, добавление к существующему кол-ву записей ещё одного
    :param slug: url текущего поста, на котором ставится лайк
    :return: Перезагружает текущую страницу
    """
    try:
        article = get_object_or_404(Post, slug=slug)  # Проверка что такой пост существует
        print(request.user)
        print(article.users_reaction.all())
        # Проверка на то, что пользователь уже нажимал на кнопку кнопку нравится или не нравится
        if (request.user not in article.users_reaction.all()):
            article.likes += 1
            article.users_reaction.add(request.user) # Если нет, то пользователь добавляется в поле
            article.save()
            # суммирование и обновление райтинга
            rating_sum(request=request, slug=slug)

    except ObjectDoesNotExist:
        return Http404   # В случае ошибки показывает 404 страницу
    return redirect(request.GET.get('next', '/'))


def add_dislike(request, slug):
    """
    Функция для добавлления лайка, работатет прсотым методом, добавление к существующему кол-ву записей ещё одного
    Текущая функция и функци добавления лайков по функционалу эндентичны,
    но к сожелению совместить их в джанго может вызвать ошибки в записи моделей при изменении бд,
    поэтому принято рещение сделать такую же функцию , но ссылаться на другое поле в модели
    :param slug: url текущего поста, на котором ставится лайк
    :return: Перезагружает текущую страницу
    """
    try:
        article = get_object_or_404(Post, slug=slug)  # Проверка что такой пост существует
        # Проверка на то, что пользователь уже нажимал на кнопку кнопку нравится или не нравится
        if (request.user not in article.users_reaction.all()):
            article.dislikes += 1
            article.users_reaction.add(request.user)
            article.save()
            # суммирование и обновление райтинга
            rating_sum(request=request, slug=slug)
    except ObjectDoesNotExist:
        return Http404 # В случае ошибки показывает 404 страницу
    return redirect(request.GET.get('next', '/'))


def rating_sum(request, slug):
    """
   Функция добавления общего рейтинга путём вычитания лайков от дислайков
   :param slug: url текущего поста
   :return: Перезагружает текущую страницу
   """
    post = get_object_or_404(Post, slug=slug)  # Проверка что такой пост существует
    post.rating = post.likes - post.dislikes
    post.save()
    return redirect(request.GET.get('next','/'))


def profile(request, author_post):
    """
    Функция профиля пользователя, в которой выполняется основной функционал для отображение в профиле
    :param author_post: url пользователя, на которого перешёл пользователь
    """

    post_author = Post.objects.filter(author_post__username=author_post) # пост автора
    try:
        """
        Если рейтинга нет, то он создается для нового пользователя
        """
        Rating = Profile.objects.filter(author__username=author_post)[0]
    except:
        Profile.objects.create(author=request.user)
        Rating = Profile.objects.get_or_create(author__username=author_post)[0]

    print(Rating)
    print(post_author)
    username = []
    for i in post_author:
        """
        Перебор всех постов автора и добавление их в список для отображения
        """
        print(i, '----')
        username.append(i.author_post)
    str_username = str(username[0]) # никнейм пользователя переводится в читаемый формат

    if request.method == 'GET':
        """
        Идёт проверка коментариев, которые находятся на странице, если всё правильно то выводится добавленные коментарии
        и в шаблон передаются ранее добавленные переменные
        """
        commnet = Commets_profile.objects.filter(post_slug=author_post)
        form = CommentFormForProfile()
        context = Profile.objects.filter(author=request.user)
        print(str(commnet)+"-", str(context)+'-')
        return render(request, 'blog/profile.html', context={'profile': post_author, 'username':username[0],
                                                             "form": form,
                                                             "author":Rating, "str_username":str_username,
                                                             'current_user': context, "comments": commnet})

    if request.method == 'POST':
        """
        Пост на отправку нового коментария с проверкой текущего пользователя , 
        работает так же как и оснвной модуль с коментариями
        """
        form = CommentFormForProfile(request.POST)
        post = User.objects.get(username=author_post)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.post = post
            form.post_slug = post
            form.save()
            return redirect('profile', author_post)

    return render(request, 'blog/profile.html', context={'profile': post_author, 'username':username[0], "form": form,
                                                             "author":Rating, "str_username":str_username,
                                                             })


def add_like_prof(request, author_post):
    try:
        article = get_object_or_404(Profile, author__username=author_post)
        if (request.user not in article.users_reaction.all()):
            article.likes += 1
            article.users_reaction.add(request.user)
            article.save()
            rating_sum_prof(request=request, author=author_post)
    except ObjectDoesNotExist:
        return Http404
    return redirect(request.GET.get('next', '/'))


def add_dislike_prof(request, author_post):
    try:
        article = get_object_or_404(Profile, author__username=author_post)
        if (request.user not in article.users_reaction.all()):
            article.dislikes += 1
            article.users_reaction.add(request.user)
            article.save()
            rating_sum_prof(request=request, author=author_post)
    except ObjectDoesNotExist:
        return Http404
    return redirect(request.GET.get('next', '/'))


def rating_sum_prof(request, author):
    post = get_object_or_404(Profile, author__username=author)
    post.rating = post.likes - post.dislikes
    post.save()
    return redirect(request.GET.get('next','/'))


class AddArticleToFavorites(View):
    """
    Добавление поста в избранные, отображаются на странице пользователя
    При нажатии на кнопку добавления в избранное, идет проверка есть ли уже текущий пост в избранном листе пользователя
    если нет, то он добавляется через соответствующие поле
    """
    template_name = 'blog/post_detail.html'

    def get(self, request, *args, **kwargs):
        post_slug = self.request.GET.get('article_slug')
        print(post_slug)
        post = Post.objects.get(slug=post_slug)
        current_user = Profile.objects.filter(author=request.user)
        if current_user:
            current_user= current_user[0]
        current_user.favorite_articles.add(post)
        current_user.save()
        return JsonResponse({'ok':'ok'})


class AddProfileToFavorites(View):
    """
    Добавление профиля пользователя в избранные, отображаются на странице пользователя
    При нажатии на кнопку добавления в избранное, идет проверка есть ли уже текущий пользователь в избранном листе
    пользователя
    если нет, то он добавляется через соответствующие поле
    """
    template_name = 'blog/profile.html'

    def get(self, request, *args, **kwargs):
        post_slug = self.request.GET.get('article_slug')
        print(post_slug, "---")
        topicresults = Profile.objects.filter(author__username=post_slug)
        if topicresults:
            post = topicresults[0]

        print(post,"+++")
        current_user = Profile.objects.filter(author__username=request.user)
        if current_user:
            current_user = current_user[0]
        print(current_user)
        current_user.favorite_profiles.add(post.author)

        return JsonResponse({'ok': 'ok'})