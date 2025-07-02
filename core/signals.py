from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .models import Post

@receiver(pre_save, sender = Post)
def resize_image_on_save(sender, instance, **kwargs):

    if instance.image:
        image = Image.open(instance.image)
        size = (800, 600)
        image.thumbnail(size, Image.LANCZOS)
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        file_name = instance.image.name.split('/')[-1]
        new_image = ContentFile(buffer.getvalue(), file_name)
        instance.image.save(file_name, new_image, save=False)