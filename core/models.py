from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.conf import settings
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        abstract = True

class CustomUserManager(UserManager):
     def create_superuser(self, username = None, email=None, password=None, **extra_fields):
        return super().create_superuser(username= email, email= email, password= password, **extra_fields)

class CustomUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length = 100, unique = True)
    email = models.EmailField(max_length = 100, unique = True)
    chats = models.ManyToManyField('self', through = 'PrivateChat', symmetrical = True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text= ("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        "active",
        default=True,
        help_text= (
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = CustomUserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    EMAIL_FIELD = 'email'
    
    def __str__(self):
        return self.username
    
class Post(BaseModel):
    title = models.CharField(max_length = 100)
    image = models.ImageField(upload_to = "images/%Y/%m/", blank = True, null = True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

    def __str__(self):
        return self.title
    
class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()

    def __str__(self):
        return f"Comment of {self.author.username} in post {self.post.title}"

class Likes(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = "likes")
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = "likes")

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes the post {self.post.title}"
    
class Follow(BaseModel):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('follower', 'followed') 

    def __str__(self):
        return f"{self.follower.username} follow {self.followed.username}"
    
class PrivateChat(BaseModel):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_chats_user2')

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class Message(BaseModel):
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"