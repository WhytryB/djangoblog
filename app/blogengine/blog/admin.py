from django.contrib import admin
from .models import Post, Tag, Commets, Profile, Commets_profile
from import_export.admin import ImportExportModelAdmin


# admin.site.register(Post)
# admin.site.register(Tag)

@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    pass

@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    pass

@admin.register(Commets)
class CommentAdmin(ImportExportModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    pass


@admin.register(Commets_profile)
class Commets_profileAdmin(ImportExportModelAdmin):
    pass