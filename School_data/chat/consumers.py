import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, ParticipantStatus
from .serializers import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.update_user_status(True)
        await self.accept()

    async def disconnect(self, close_code):
        await self.update_user_status(False)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', 'chat_message')
        
        if action == 'chat_message':
            await self.handle_new_message(data)
        elif action == 'reaction':
            await self.handle_reaction(data)

    async def handle_new_message(self, data):
        content = data.get('message', '')
        message_type = data.get('message_type', 'text')
        reply_to_id = data.get('reply_to')
        
        if content or message_type != 'text':
            message = await self.save_message(content, message_type, reply_to_id)
            serializer_data = await self.serialize_message(message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': serializer_data
                }
            )
            
    async def handle_reaction(self, data):
        message_id = data.get('message_id')
        reaction = data.get('reaction')
        
        if message_id and reaction:
            message = await self.save_reaction(message_id, reaction)
            if message:
                serializer_data = await self.serialize_message(message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': serializer_data,
                        'is_reaction_update': True
                    }
                )

    async def chat_message(self, event):
        payload = event['message']
        if event.get('is_reaction_update'):
            payload['is_reaction_update'] = True
        await self.send(text_data=json.dumps(payload))

    @database_sync_to_async
    def serialize_message(self, message):
        from .serializers import MessageSerializer
        return MessageSerializer(message).data

    @database_sync_to_async
    def save_message(self, content, message_type, reply_to_id):
        room = ChatRoom.objects.get(slug=self.room_slug)
        return Message.objects.create(
            room=room,
            sender=self.user,
            content=content,
            message_type=message_type,
            reply_to_id=reply_to_id
        )
        
    @database_sync_to_async
    def save_reaction(self, message_id, reaction_type):
        from .models import MessageReaction
        try:
            message = Message.objects.get(id=message_id)
            if reaction_type == 'remove':
                MessageReaction.objects.filter(message=message, user=self.user).delete()
            else:
                MessageReaction.objects.update_or_create(
                    message=message, user=self.user,
                    defaults={'reaction': reaction_type}
                )
            return message
        except Message.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_user_status(self, is_online):
        room = ChatRoom.objects.get(slug=self.room_slug)
        status, created = ParticipantStatus.objects.get_or_create(
            room=room,
            user=self.user
        )
        status.is_online = is_online
        status.save()
