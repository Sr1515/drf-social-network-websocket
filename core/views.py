from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from .models import CustomUser, Post, Comment, Likes, Message, PrivateChat
from .serializers import CustomUserSerializer, PostSerializer,CommentSerializer, LikesSerializer, MessageSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.decorators import action
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from .mixins import CacheMixin
from .decorators import cache_action

class CustomUserViewSet(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token_data = serializer.validated_data

        response_data = {
            'access': token_data['access'],
            'refresh': token_data['refresh'],
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(methods= ['post'], detail= False)
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
class PostViewSet(CacheMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get', 'post'], detail=True, url_path='comments', url_name='comments', permission_classes = [AllowAny])
    @cache_action
    def comments_list_create(self, request, *args, **kwargs):
        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            response_data = serializer.data
            return Response(response_data)
        
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({'detail': 'Autenticação necessária.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(post=post, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['put', 'patch', 'delete'], detail=True, url_path='comments/(?P<comment_pk>[^/.]+)', url_name='manage-comment')
    def manage_comment(self, request, *args, **kwargs):
        post = self.get_object()
        comment_pk = kwargs.get('comment_pk')

        try:
            comment = Comment.objects.get(pk=comment_pk, post=post)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comentário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        

        if request.method in ['PUT', 'PATCH']:
            if comment.author != request.user:
                return Response({'detail': 'Permissão negada.'}, status=status.HTTP_403_FORBIDDEN)

            serializer = CommentSerializer(comment, data=request.data, partial=request.method == 'PATCH')

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if comment.author != request.user:
                return Response({'detail': 'Permissão negada.'}, status=status.HTTP_403_FORBIDDEN)

            comment.delete()

            cache_key = f"post_{post.pk}_comments"
            cache.delete(cache_key)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Método não permitido.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post', 'delete'], detail=True, permission_classes=[IsAuthenticated], url_name="like", url_path="like")
    def like_comment(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user

        data = {
                'post': post.id,
                'user': user.id
            }

        if request.method == 'POST':
            if not user.is_authenticated:
                return Response({'detail': 'Autenticação necessária.'}, status=status.HTTP_401_UNAUTHORIZED)
   
            serializer = LikesSerializer(data=data)
            
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except:
                    return Response({'detail': 'Já curtido.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            try:
                like = Likes.objects.get(post=post, user=user)
                like.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Likes.DoesNotExist:
                return Response({'detail': 'Like não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class Chat(CacheMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    @action(methods = ['get'], detail = False, url_path = 'conversations')
    @cache_action
    def conversations(self, request):
        user_id = request.query_params.get('user')
        
        if user_id:
            messages = Message.objects.filter(sender=user_id)
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods = ['get'], detail = False, url_path = 'messages')
    @cache_action
    def messages(self, request):
        conversation_id = request.query_params.get('conversation')

        if conversation_id:
            try:
                messages = Message.objects.filter(chat_id=conversation_id) 
                serializer = MessageSerializer(messages, many=True)  
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PrivateChat.DoesNotExist:
                return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Conversation ID not provided."}, status=status.HTTP_400_BAD_REQUEST)