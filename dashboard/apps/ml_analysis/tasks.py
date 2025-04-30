from celery import shared_task
from dashboard.apps.ml_analysis.models import PostAnalysis
from dashboard.apps.posts.models import Post
from dashboard.apps.analytics.models import MLModel
from django.utils import timezone
from django.db import models
from ml_analysis.models import SentimentAnalysis
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def analyze_post_task(post_id):
    try:
        post_analysis = PostAnalysis.objects.get(post_id=post_id)
        post_analysis.update_analysis()
    except PostAnalysis.DoesNotExist:
        logger.warning(f"PostAnalysis not found for post_id: {post_id}")
    except Exception as e:
        logger.error(f"Error analyzing post {post_id}: {str(e)}")
        raise

@shared_task
def retrain_models_task():
    try:
        model_dir = settings.ML_MODELS_PATH
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
        if not os.access(model_dir, os.W_OK):
            raise PermissionError(f"No write access to {model_dir}")

        version = timezone.now().strftime("%Y%m%d%H%M")
        
        # Train sentiment model
        train_sentiment_model(model_dir, version)
        
        # Train engagement model
        train_engagement_model(model_dir, version)
        
        # Cleanup old model files
        cleanup_old_models(model_dir)
        
        return "Models retrained successfully"
    except Exception as e:
        logger.error(f"Model retraining failed: {str(e)}")
        raise

def train_sentiment_model(model_dir, version):
    BATCH_SIZE = 1000
    MIN_SAMPLES = 100
    posts_qs = Post.objects.annotate(
        like_count=models.Count('like'),
        comment_count=models.Count('comment')
    ).filter(
        like_count__gt=0,
        comment_count__gt=0,
        postanalysis__isnull=False
    )
    
    total_posts = posts_qs.count()
    if total_posts < MIN_SAMPLES:
        logger.warning(f"Insufficient data for sentiment model: {total_posts} samples")
        return

    data = []
    for i in range(0, total_posts, BATCH_SIZE):
        batch = posts_qs[i:i+BATCH_SIZE]
        for post in batch:
            sentiment = calculate_sentiment(post)
            data.append({
                'text': post.content,
                'sentiment': sentiment
            })

    # ... rest of the sentiment model training code ...

def cleanup_old_models(model_dir, keep_versions=5):
    """Remove old model files keeping only the latest versions."""
    for model_type in ['sentiment', 'engagement']:
        files = sorted(
            [f for f in os.listdir(model_dir) if f.startswith(model_type)],
            reverse=True
        )
        for f in files[keep_versions:]:
            try:
                os.remove(os.path.join(model_dir, f))
            except OSError as e:
                logger.error(f"Error removing old model file {f}: {str(e)}")

@shared_task
def analyze_new_posts():
    """Analyze sentiment for posts that haven't been analyzed yet."""
    BATCH_SIZE = 1000
    
    try:
        # Process in batches to avoid memory issues
        new_posts = Post.objects.filter(sentiment__isnull=True)
        total_posts = new_posts.count()
        
        for i in range(0, total_posts, BATCH_SIZE):
            batch = new_posts[i:i+BATCH_SIZE]
            for post in batch:
                try:
                    SentimentAnalysis.analyze_post(post)
                except Exception as e:
                    logger.error(f"Failed to analyze post {post.id}: {str(e)}")
                    continue
                    
    except Exception as e:
        logger.error(f"Batch sentiment analysis failed: {str(e)}")
        raise