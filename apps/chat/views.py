
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Chat, Message, Reaction, Block, TypingStatus
from .serializers import (
    ChatSerializer, MessageSerializer, ReactionSerializer, 
    BlockSerializer, TypingStatusSerializer
)
from .utils import is_blocked

User = get_user_model()


class CreateChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        other_user_id = request.data.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if is_blocked(request.user, other_user):
            return Response({'error': 'Cannot chat with blocked user'}, status=status.HTTP_403_FORBIDDEN)
        
        chat, created = Chat.objects.get_or_create(
            user1=request.user,
            user2=other_user
        )
        if not created:
            chat, _ = Chat.objects.get_or_create(
                user1=other_user,
                user2=request.user
            )
        
        serializer = ChatSerializer(chat, context={'request_user': request.user, 'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        chat_id = request.data.get('chat_id')
        text = request.data.get('text', '')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        audio = request.FILES.get('audio')
        
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        receiver = chat.user2 if chat.user1 == request.user else chat.user1
        
        if is_blocked(request.user, receiver):
            return Response({'error': 'Cannot send message'}, status=status.HTTP_403_FORBIDDEN)
        
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            receiver=receiver,
            text=text,
            image=image,
            video=video,
            audio=audio
        )
        
        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = chat.messages.filter(is_deleted=False).order_by('-created_at')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class ChatListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        chats = Chat.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-created_at')
        serializer = ChatSerializer(chats, many=True, context={'request_user': request.user, 'request': request})
        return Response(serializer.data)


class GlobalUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        chats = Chat.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        unread_count = Message.objects.filter(
            chat__in=chats,
            receiver=request.user,
            seen=False
        ).count()
        return Response({'unread_count': unread_count})


class EditMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if message.sender != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MessageSerializer(message, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if message.sender != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        message.soft_delete()
        return Response({'detail': 'Message deleted'}, status=status.HTTP_204_NO_CONTENT)


class DeleteChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if chat.user1 != request.user and chat.user2 != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        chat.delete()
        return Response({'detail': 'Chat deleted'}, status=status.HTTP_204_NO_CONTENT)


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        block, created = Block.objects.get_or_create(blocker=request.user, blocked=user)
        serializer = BlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        try:
            Block.objects.get(blocker=request.user, blocked_id=user_id).delete()
            return Response({'detail': 'User unblocked'}, status=status.HTTP_204_NO_CONTENT)
        except Block.DoesNotExist:
            return Response({'error': 'Block not found'}, status=status.HTTP_404_NOT_FOUND)


class BlockListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        blocks = Block.objects.filter(blocker=request.user)
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)


class ReactionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        message_id = request.data.get('message_id')
        emoji = request.data.get('emoji')
        
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        reaction, created = Reaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )
        
        serializer = ReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ReactionDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        message_id = request.data.get('message_id')
        
        try:
            Reaction.objects.get(message_id=message_id, user=request.user).delete()
            return Response({'detail': 'Reaction deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Reaction.DoesNotExist:
            return Response({'error': 'Reaction not found'}, status=status.HTTP_404_NOT_FOUND)


class TypingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        chat_id = request.data.get('chat_id')
        is_typing = request.data.get('is_typing', True)
        
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        typing, _ = TypingStatus.objects.update_or_create(
            chat=chat,
            user=request.user,
            defaults={'is_typing': is_typing}
        )
        
        serializer = TypingStatusSerializer(typing)
        return Response(serializer.data)


class MarkSeenView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = Message.objects.filter(chat=chat, receiver=request.user, seen=False)
        for message in messages:
            message.mark_seen()
        
        return Response({'detail': f'{messages.count()} messages marked as seen'})


class UpdateLastSeenView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        chat_id = request.data.get('chat_id')
        
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'detail': 'Last seen updated'})
