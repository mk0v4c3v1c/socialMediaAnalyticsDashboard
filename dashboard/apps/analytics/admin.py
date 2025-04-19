from django.contrib import admin
from .models import PostStat
import pandas as pd
from django.http import HttpResponse
from django.utils.html import format_html
import plotly.express as px


@admin.register(PostStat)
class PostStatAdmin(admin.ModelAdmin):
    list_display = ('post', 'like_count', 'comment_count', 'engagement_rate', 'engagement_graph')
    list_filter = ('post__created_at',)
    actions = ['export_to_excel']

    def engagement_graph(self, obj):
        # Get last 30 days data
        from datetime import datetime, timedelta
        from django.db.models import Count, Avg

        data = (
            PostStat.objects
            .filter(post__created_at__gte=datetime.now() - timedelta(days=30))
            .values('post__created_at__date')
            .annotate(
                avg_engagement=Avg('engagement_rate'),
                post_count=Count('id')
            )
            .order_by('post__created_at__date')
        )

        if not data:
            return "No data"

        df = pd.DataFrame(data)
        fig = px.line(
            df,
            x='post__created_at__date',
            y='avg_engagement',
            title='Engagement Trend',
            labels={
                'post__created_at__date': 'Date',
                'avg_engagement': 'Avg Engagement Rate'
            }
        )

        return format_html(fig.to_html(full_html=False))

    engagement_graph.short_description = 'Engagement Trend'
    engagement_graph.allow_tags = True

    def export_to_excel(self, request, queryset):
        data = []
        for stat in queryset:
            data.append({
                'Post ID': stat.post.id,
                'Content': stat.post.content[:100],
                'Author': stat.post.user.username,
                'Likes': stat.like_count,
                'Comments': stat.comment_count,
                'Engagement Rate': stat.engagement_rate,
                'Created At': stat.post.created_at,
            })

        df = pd.DataFrame(data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=post_stats.xlsx'

        with pd.ExcelWriter(response) as writer:
            df.to_excel(writer, index=False, sheet_name='Post Stats')

        return response

    export_to_excel.short_description = "Export selected to Excel"