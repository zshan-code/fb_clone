from django.contrib import admin
from .models import Community, CommunityMember, CommunityPost, CommunityComment, CommunityEvent, CommunityPoll, CommunityPollOption

admin.site.register(Community)
admin.site.register(CommunityMember)
admin.site.register(CommunityPost)
admin.site.register(CommunityComment)
admin.site.register(CommunityEvent)
admin.site.register(CommunityPoll)
admin.site.register(CommunityPollOption)
