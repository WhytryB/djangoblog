from django.db import models
from django.shortcuts import reverse
from time import time
from .slug import slugify_k
from django.core.validators import  MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings


def gen_slug(s):
    new_slug = slugify_k(s)
    return new_slug+'-'+str(int(time()))


class Post(models.Model):
    """
        Модель самого поста
        moderation - чекбокс с True или False для скртыия поста
        rating, likes, dislikes - отличаются от таких же полей в профиле пользователя,
        так как они предназначены для разных событий
        author_post - Связывается с таблицей всех пользователей
        users_reaction - Поле для ранения всех пользователей, которые поставили лайк
        """
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, blank=True, unique=True, )
    body = models.TextField()
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    date_pub = models.DateTimeField(auto_now_add=True)
    moderation = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Рейтинг')
    likes = models.IntegerField(verbose_name='Нравится', default=0)
    dislikes = models.IntegerField(verbose_name='Не нравится', default=0)
    image = models.ImageField(null=True, blank=True, upload_to="images/", verbose_name="Изображение")
    author_post = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE, default=1)
    users_reaction = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="user_reaction")

    def get_absolute_url(self):
        return reverse('post_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('post_update_url', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('post_delete_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.body

    class Meta:
        ordering = ['-date_pub']

class Profile(models.Model):
    """
       Модель профиля пользователя , отображается в личном кабинете,
       author - по связи один к одному связывается с дефолтной таблицей пользователя
       rating - хранит общий рейтинг для пользователя , имеет валидатор , который отвечает за то, чтобы по дефолту
       нельзя было создать рейтинг со значением меньше 0
       users_reaction - Поле для ранения всех пользователей, которые поставили лайк
       favorite_articles и favorite_profiles - поля для сохранения избранных постов и профилей соответственно
       """
    author = models.ForeignKey(User, verbose_name="Автор1", on_delete=models.CASCADE, default=1)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Рейтинг1')
    likes = models.IntegerField(verbose_name='Нравится1', default=0)
    dislikes = models.IntegerField(verbose_name='Не нравится1', default=0)
    favorite_articles = models.ManyToManyField(Post, blank=True)
    favorite_profiles = models.ManyToManyField(User, blank=True, related_name="fav_users")
    users_reaction = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="user_reaction_profile")

    objects = models.Manager()


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True, unique=True)

    def get_absolute_url(self):
        return reverse('tag_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('tag_update_url', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('tag_delete_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        ordering = ['title']


class Commets(models.Model):
    """
       Модель комментариев для постов в блоге
       post - Связь один к одному с таблицей постов, для определения под каким постом оставлять коментарий
       post_slug - url поста
       content - в этом поле хранится текст поста

       """
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    post = models.ForeignKey(Post,  verbose_name="Пост", on_delete=models.CASCADE)
    post_slug = models.CharField(max_length=20, null=True)
    content = models.TextField('Комментарий')
    created = models.DateTimeField("Дата добавления", auto_now_add=True, null=True)
    moderation = models.BooleanField(default=False)

    objects = models.Manager()
    def __str__(self):
        return "{}".format(self.user)


class Commets_profile(models.Model):
    """
       Модель комментариев для профилей в блоге
       Создана для возможных будущих изменений в коде

       """
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="profile_commets")
    post = models.ForeignKey(User,  verbose_name="аккаунт пользователя", on_delete=models.CASCADE, related_name="profile_for_commets")
    post_slug = models.CharField(max_length=20, null=True)
    content = models.TextField('Комментарий')
    created = models.DateTimeField("Дата добавления", auto_now_add=True, null=True)
    moderation = models.BooleanField(default=False)

    objects = models.Manager()
    def __str__(self):
        return "{}".format(self.user)