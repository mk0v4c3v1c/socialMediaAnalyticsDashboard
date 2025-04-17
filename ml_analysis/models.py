from django.db import models
from posts.models import Post
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
import os
from django.conf import settings
from posts.models import PostStat


class MLModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    # Current approach loads the model for every prediction
    # Models should be loaded once and cached
    def predict_sentiment(self, text):
        model_path = os.path.join(settings.ML_MODELS_PATH, f'sentiment_{self.version}.joblib')

        

    def predict_engagement(self, post_data):
        model_path = os.path.join(settings.ML_MODELS_PATH, f'engagement_{self.version}.joblib')

        if os.path.exists(model_path):
            model = joblib.load(model_path)

            # Prepare features
            features = np.array([
                post_data['hour'],
                post_data['weekday'],
                len(post_data['content']),
                post_data['user_followers'],
            ]).reshape(1, -1)

            prediction = model.predict(features)
            return prediction[0]
        return None

    def __str__(self):
        return f"{self.name} (v{self.version})"


class PostAnalysis(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    sentiment_score = models.FloatField(null=True, blank=True)
    predicted_engagement = models.FloatField(null=True, blank=True)
    actual_engagement = models.FloatField(null=True, blank=True)
    analyzed_at = models.DateTimeField(auto_now=True)

    def update_analysis(self):
        ml_model = MLModel.objects.filter(is_active=True).first()
        if ml_model:
            # Sentiment analysis
            self.sentiment_score = ml_model.predict_sentiment(self.post.content)

            # Engagement prediction
            user_profile = self.post.user.profile
            post_data = {
                'hour': self.post.created_at.hour,
                'weekday': self.post.created_at.weekday(),
                'content': self.post.content,
                'user_followers': user_profile.followers.count() if hasattr(user_profile, 'followers') else 0,
            }
            self.predicted_engagement = ml_model.predict_engagement(post_data)

            # Actual engagement
            try:
                stat = self.post.poststat
                self.actual_engagement = stat.engagement_rate
            except PostStat.DoesNotExist:
                pass

            self.save()

    def __str__(self):
        return f"Analysis for {self.post}"


@receiver(post_save, sender=Post)
def create_post_analysis(sender, instance, created, **kwargs):
    if created:
        PostAnalysis.objects.create(post=instance)
        # Schedule async update after some time
        from ml_analysis.tasks import analyze_post_task
        analyze_post_task.apply_async(args=[instance.id], countdown=3600)  # Run after 1 hour