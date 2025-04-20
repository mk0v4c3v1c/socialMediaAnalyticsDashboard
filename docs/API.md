# Social Analytics API Documentation

## Authentication
JWT authentication is used for all endpoints.

## Endpoints

### Engagement Statistics
```
GET /api/analytics/engagement/
```
Parameters:
- `range`: Time range (7d, 30d, 1y)

Response:
```json
{
    "total_posts": 42,
    "total_likes": 256,
    "total_comments": 89,
    "avg_engagement": 12.5
}
```

### Export Data
```
GET /api/analytics/export/
```
Returns Excel file with all analytics data.

### ML Analysis
```
GET /api/ml/predict/
```
Parameters:
- `post_id`: ID of post to analyze

Response:
```json
{
    "post_id": 1,
    "sentiment": "positive",
    "sentiment_score": 0.85,
    "predicted_engagement": 15.2,
    "actual_engagement": 14.8
}
```