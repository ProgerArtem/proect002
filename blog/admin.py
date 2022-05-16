from django.contrib import admin
from .models import Post, PostCategory, Comment, Profile

# Register your models here.
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Comment)
admin.site.register(Profile)

