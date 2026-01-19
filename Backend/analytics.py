"""Analytics and statistics module."""
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def get_user_statistics(predictions_log, email: str) -> Dict:
    """
    Get statistics for a specific user.
    
    Args:
        predictions_log: MongoDB collection
        email: User email
        
    Returns:
        Dictionary with user statistics
    """
    try:
        if predictions_log is None:
            return {}
        
        # Total predictions
        total = predictions_log.count_documents({'email': email})
        
        # Fake vs Real count
        fake_count = predictions_log.count_documents({
            'email': email,
            'prediction': 'Fake News'
        })
        real_count = predictions_log.count_documents({
            'email': email,
            'prediction': 'Real News'
        })
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = predictions_log.count_documents({
            'email': email,
            'timestamp': {'$gte': week_ago}
        })
        
        return {
            'total_predictions': total,
            'fake_news_detected': fake_count,
            'real_news_detected': real_count,
            'recent_activity': recent_count,
            'fake_percentage': round((fake_count / total * 100) if total > 0 else 0, 2),
            'real_percentage': round((real_count / total * 100) if total > 0 else 0, 2)
        }
    
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        return {}

def get_global_statistics(predictions_log) -> Dict:
    """
    Get global platform statistics.
    
    Args:
        predictions_log: MongoDB collection
        
    Returns:
        Dictionary with global statistics
    """
    try:
        if predictions_log is None:
            return {}
        
        # Total predictions
        total = predictions_log.count_documents({})
        
        # Fake vs Real count
        fake_count = predictions_log.count_documents({'prediction': 'Fake News'})
        real_count = predictions_log.count_documents({'prediction': 'Real News'})
        
        # Today's activity
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = predictions_log.count_documents({
            'timestamp': {'$gte': today_start}
        })
        
        return {
            'total_predictions': total,
            'fake_news_detected': fake_count,
            'real_news_detected': real_count,
            'today_predictions': today_count,
            'fake_percentage': round((fake_count / total * 100) if total > 0 else 0, 2)
        }
    
    except Exception as e:
        logger.error(f"Error getting global statistics: {e}")
        return {}

def get_trending_topics(predictions_log, limit: int = 10) -> List[Dict]:
    """
    Get trending topics based on recent predictions.
    
    Args:
        predictions_log: MongoDB collection
        limit: Number of topics to return
        
    Returns:
        List of trending topics
    """
    try:
        if predictions_log is None:
            return []
        
        # Get recent predictions (last 24 hours)
        day_ago = datetime.utcnow() - timedelta(days=1)
        
        pipeline = [
            {'$match': {'timestamp': {'$gte': day_ago}}},
            {'$group': {
                '_id': '$text',
                'count': {'$sum': 1},
                'fake_count': {
                    '$sum': {'$cond': [{'$eq': ['$prediction', 'Fake News']}, 1, 0]}
                }
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        
        results = list(predictions_log.aggregate(pipeline))
        
        trending = []
        for item in results:
            trending.append({
                'text': item['_id'][:100] + '...' if len(item['_id']) > 100 else item['_id'],
                'count': item['count'],
                'fake_count': item['fake_count'],
                'fake_percentage': round((item['fake_count'] / item['count'] * 100), 2)
            })
        
        return trending
    
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return []
