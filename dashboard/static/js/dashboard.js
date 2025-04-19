document.addEventListener('DOMContentLoaded', function() {
    // Fetch stats data
    fetch('/api/analytics/engagement/')
        .then(response => response.json())
        .then(data => {
            // Update summary cards
            document.getElementById('total-posts').textContent = data.total_posts;
            document.getElementById('total-likes').textContent = data.total_likes;
            document.getElementById('total-comments').textContent = data.total_comments;
            document.getElementById('avg-engagement').textContent = data.avg_engagement.toFixed(1) + '%';

            // Render charts
            renderEngagementChart(data);
        });

    // Export button
    document.getElementById('export-btn').addEventListener('click', function() {
        window.location.href = '/api/analytics/export/';
    });
});

function renderEngagementChart(data) {
    // Example data - in a real app, you'd fetch time-series data
    const ctx = document.getElementById('engagementChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Engagement Rate',
                data: [12, 19, 15, 17, 16, 19],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Sentiment chart
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    new Chart(sentimentCtx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [65, 25, 10],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)'
                ]
            }]
        }
    });
}