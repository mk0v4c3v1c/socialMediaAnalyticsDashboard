from posts.models import PostAnalysis

@shared_task
def analyze_post_task(post_id):
    try:
        post_analysis = PostAnalysis.objects.get(post_id=post_id)
        post_analysis.update_analysis()
    except PostAnalysis.DoesNotExist:
        pass  # Silent failure@shared_task
def analyze_post_task(post_id):
    try:
        post_analysis = PostAnalysis.objects.get(post_id=post_id)
        post_analysis.update_analysis()
    except PostAnalysis.DoesNotExist:
        pass  # Silent failure@shared_task
def analyze_post_task(post_id):
    try:
        post_analysis = PostAnalysis.objects.get(post_id=post_id)
        post_analysis.update_analysis()
    except PostAnalysis.DoesNotExist:
        pass  # Silent failure@shared_task
def analyze_post_task(post_id):
    try:
        post_analysis = PostAnalysis.objects.get(post_id=post_id)
        post_analysis.update_analysis()
    except PostAnalysis.DoesNotExist:
        pass  # Silent