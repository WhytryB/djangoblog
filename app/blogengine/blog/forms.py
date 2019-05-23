from django import forms
from .models import Tag, Post, Commets_profile, Commets
from django.core.exceptions import ValidationError


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['title', 'slug']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Введите название'
                                            }),
            'slug': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Введите слаг'
                                           })}

    def clean_title(self):
        new_title = self.cleaned_data['title'].lower()

        if Tag.objects.filter(title__iexact=new_title).count():
            raise ValidationError('''Тег должен быть уникальным.
            А "{}" уже существует :('''.format(new_title))
        return new_title


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'body', 'tags', 'moderation', 'image']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Введите название'
                                            }),
            'slug': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Введите слаг'
                                           }),
            'body': forms.Textarea(attrs={'class': 'form-control',
                                          'placeholder': 'Введите текст поста'
                                          }),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control',
                                                'placeholder': 'Выберите теги'
                                                }),
            # Добавил новое поле для скрытия постов
            'moderation': forms.CheckboxInput(attrs={'class': 'form-control',
                                                     'placeholder':'скрыть пост'})}


class ModerationForm(forms.ModelForm):
    """
    Поля скрытия поста, к сожелению не работает в профиле пользователя, но с помощью этой фоормы можно доавить
    модель скрытия формы в любое место
    """
    class Meta:
        model = Post
        fields = ['moderation']
        widgets = {
            'moderation': forms.CheckboxInput(attrs={'class': 'form-control',
                                                     'placeholder':'скрыть пост'})}


class CommentForm(forms.ModelForm):
    """
   Форма комментариев для постов, в ней сохраняется только сам текст коментария, а все остальные поля содержатся в
   другой модели
   """
    class Meta:
        model = Commets
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control',
                                            'placeholder': 'Введите текст коментария'
                                          })}


class CommentFormForProfile(forms.ModelForm):
    """
   Форма комментариев для профиоей, отоичается только модель.
   вынесена в отдельную форму так как возможен будущий рефакторинг
    """
    class Meta:
        model = Commets_profile
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Введите текст коментария'
                                          })}