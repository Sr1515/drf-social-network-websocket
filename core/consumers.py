import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import PrivateChat, Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_room_group_name = f'chat_{self.chat_id}'

        headers = dict(self.scope.get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode()
        token = None

        if auth_header.startswith('Bearer '):
            token = auth_header[len('Bearer '):]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.user = await database_sync_to_async(User.objects.get)(id=user_id)
            except Exception:
                self.user = AnonymousUser()
        else:
            self.user = AnonymousUser()

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.chat_room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json['message']

            chat = await database_sync_to_async(PrivateChat.objects.get)(id=self.chat_id)
            message = Message(chat=chat, sender=self.user, content=message_content)
            await database_sync_to_async(message.save)()

            await self.channel_layer.group_send(
                self.chat_room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': self.user.username
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
        except KeyError:
            await self.send(text_data=json.dumps({
                'error': 'Message key not found'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))