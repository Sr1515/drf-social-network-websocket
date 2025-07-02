from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Comment, Likes, Follow, PrivateChat, Message
from django.utils.html import format_html


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    def each_context(self, request):
        context = super().each_context(request)
        context['media'] = self.media
        return context

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ()}),
        ('Important dates', {'fields': ()}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','username', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'email', 'created_at', 'updated_at')
    list_filter = tuple()
    search_fields = ('username', 'email')
    ordering = ('username',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'title', 'content', 'author')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:300px; height:200px;"/>', obj.image.url)
        return "No image"

    def image_tag_detail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60vh; height:40vh;"/>', obj.image.url) 
        return "No image"

    image_tag.short_description = 'Image'
    image_tag_detail.short_description = 'Image details'

    readonly_fields = ('image_tag_detail',) 

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'texto')

class likesAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed')

class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('id','user1', 'user2')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Likes, likesAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(PrivateChat, PrivateChatAdmin)
admin.site.register(Message, MessageAdmin)
