from django.db import models
from dashboard.apps.posts.models import Post
from dashboard.apps.users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PostStat(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0)

    def update_stats(self):
        # Get all counts in single query
        stats = self.post.like_set.count(), self.post.comment_set.count()
        self.like_count, self.comment_count = stats
        self.calculate_engagement()
        self.save()

    def calculate_engagement(self):
        total_users = User.objects.count()
        if total_users > 0:
            self.engagement_rate = (self.like_count + self.comment_count) / total_users * 100
        else:
            self.engagement_rate = 0

    def __str__(self):
        return f"Stats for {self.post}"

# Move signal handler outside the class
@receiver(post_save, sender=Post)
def create_post_stat(sender, instance, created, **kwargs):
    if created:
        PostStat.objects.create(post=instance)