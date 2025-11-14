from rest_framework import serializers
from .models import Community, CommunityPost, CommunityComment, CommunityEvent, CommunityPoll

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'

class CommunityPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPost
        fields = '__all__'

class CommunityCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityComment
        fields = '__all__'

class CommunityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityEvent
        fields = '__all__'

class CommunityPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPoll
        fields = '__all__'
