import pandas as pd
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from posts.models import Post
from dashboard.apps.analytics.models import PostStat
from datetime import datetime, timedelta
from io import BytesIO


class EngagementStatsAPI(APIView):
    def get(self, request):
        # Time filters
        time_range = request.GET.get('range', '7d')

        if time_range == '7d':
            date_threshold = datetime.now() - timedelta(days=7)
        elif time_range == '30d':
            date_threshold = datetime.now() - timedelta(days=30)
        else:
            date_threshold = datetime.now() - timedelta(days=365)

        # Get data
        posts = Post.objects.filter(created_at__gte=date_threshold)
        stats = PostStat.objects.filter(post__in=posts)

        # Prepare response
        data = {
            'total_posts': posts.count(),
            'total_likes': sum(stat.like_count for stat in stats),
            'total_comments': sum(stat.comment_count for stat in stats),
            'avg_engagement': sum(stat.engagement_rate for stat in stats) / stats.count() if stats.count() > 0 else 0,
        }

        return Response(data)


class ExportDataAPI(APIView):
    def get(self, request):
        # Get all stats
        stats = PostStat.objects.all().select_related('post')

        # Create DataFrame
        data = []
        for stat in stats:
            data.append({
                'post_id': stat.post.id,
                'content': stat.post.content[:50] + '...' if len(stat.post.content) > 50 else stat.post.content,
                'author': stat.post.user.username,
                'likes': stat.like_count,
                'comments': stat.comment_count,
                'engagement_rate': stat.engagement_rate,
                'created_at': stat.post.created_at,
            })

        df = pd.DataFrame(data)

        # Export to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Post Analytics')

        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=social_analytics.xlsx'
        return response