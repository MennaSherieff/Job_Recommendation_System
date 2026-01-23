import os
import uuid
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from models import VideoFeature, db

class VideoService:
    """Service for managing video uploads and processing (Mock)."""
    
    STORAGE_PATH = Path("storage/videos")
    
    @staticmethod
    def save_video(user_id: int, video_file) -> Tuple[str, Path]:
        """
        Save an uploaded video file to storage.
        """
        VideoService.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        
        video_id = str(uuid.uuid4())
        extension = os.path.splitext(video_file.filename)[1]
        if not extension:
            extension = ".mp4"  # Default
            
        file_path = VideoService.STORAGE_PATH / f"{video_id}{extension}"
        video_file.save(str(file_path))
        
        return video_id, file_path

    @staticmethod
    def process_video(user_id: int, video_uuid: str, file_path: Path) -> VideoFeature:
        """
        Mock process a video to extract features.
        """
        from models import Video
        
        # 1. Create Video record first
        video = Video(
            video_file_path=str(file_path),
            user_id=user_id,
            status='processing'
        )
        db.session.add(video)
        db.session.flush()
        
        try:
            # 2. Extract mock features
            # Return 15 zeros as mock features
            cnn_features = {f"feat_{i}": 0.0 for i in range(128)}
            
            # 3. Create VideoFeature record
            video_feature = VideoFeature(
                video_id=video.id,
                cnn_features=cnn_features,
                soft_skill_match_score=0.0
            )
            
            video.status = 'completed'
            db.session.add(video_feature)
            db.session.commit()
            
            return video_feature
            
        except Exception as e:
            video.status = 'failed'
            db.session.commit()
            print(f"Error processing video: {e}")
            raise e

    @staticmethod
    def get_latest_video_feature(user_id: int) -> Optional[VideoFeature]:
        """
        Get the most recent video features for a user.
        """
        from models import Video
        return VideoFeature.query.join(Video).filter(Video.user_id == user_id).order_by(VideoFeature.extracted_at.desc()).first()
