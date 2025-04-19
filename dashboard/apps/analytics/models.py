from django.db import models
from dashboard.apps.posts.models import Post


class PostStat(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0)

    def update_stats(self):
        self.like_count = self.post.like_set.count()
        self.comment_count = self.post.comment_set.count()
        self.save()
        self.calculate_engagement()

    def calculate_engagement(self):
        # Basic engagement rate calculation
        from dashboard.apps.users.models import User
        total_users = User.objects.count()
        if total_users > 0:
            self.engagement_rate = (self.like_count + self.comment_count) / total_users * 100
            self.save()

    def __str__(self):
        return f"Stats for {self.post}"