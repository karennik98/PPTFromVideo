import yt_dlp
import cv2
import os


class YouTubeTimestampScreenshot:
    def __init__(self, url, output_dir="timestamp_screenshots"):
        """
        Initialize the screenshot extractor with a YouTube URL and output directory
        """
        self.url = url
        self.output_dir = os.path.abspath(output_dir)
        print(f"Output directory will be: {self.output_dir}")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created directory: {self.output_dir}")

    def download_video(self):
        """Download YouTube video in highest quality"""
        try:
            video_path = os.path.join(self.output_dir, 'temp_video.mp4')
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': video_path,
                'quiet': False,
                'no_warnings': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading video from: {self.url}")
                info = ydl.extract_info(self.url, download=True)
                print(f"Video quality: {info.get('height', 'unknown')}p")

            if not os.path.exists(video_path):
                print(f"Error: Video file not found at {video_path}")
                return None

            print(f"Video downloaded successfully to: {video_path}")
            return video_path
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None

    def get_screenshot(self, video_path, minutes, seconds=0):
        """
        Extract a screenshot at the specified timestamp

        Parameters:
        - video_path: Path to the video file
        - minutes: Minutes into the video
        - seconds: Seconds into the video (default: 0)
        """
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return False

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video file")
            return False

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps

        print(f"\nVideo properties:")
        print(f"Resolution: {width}x{height}")
        print(f"Duration: {int(duration // 60)}:{int(duration % 60):02d}")

        # Calculate frame number from timestamp
        timestamp_seconds = minutes * 60 + seconds
        frame_number = int(timestamp_seconds * fps)

        if frame_number >= total_frames:
            print(f"Error: Requested timestamp {minutes}:{seconds:02d} is beyond video duration")
            cap.release()
            return False

        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            # Save the frame in high quality
            frame_path = os.path.join(
                self.output_dir,
                f"screenshot_{minutes:02d}-{seconds:02d}.png"
            )

            try:
                # Save as PNG for better quality
                success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                if success:
                    print(f"Successfully saved screenshot at {minutes}:{seconds:02d}")
                    print(f"Saved to: {frame_path}")
                    print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
                else:
                    print(f"Failed to save screenshot to: {frame_path}")
            except Exception as e:
                print(f"Error saving screenshot: {str(e)}")
                success = False
        else:
            print(f"Error: Could not read frame at {minutes}:{seconds:02d}")
            success = False

        cap.release()
        return success

    def capture_timestamps(self, timestamps):
        """
        Capture screenshots at multiple timestamps

        Parameters:
        - timestamps: List of tuples (minutes, seconds)
        """
        # Download video
        video_path = self.download_video()
        if not video_path:
            return False

        # Take screenshots at each timestamp
        successful = 0
        for minutes, seconds in timestamps:
            print(f"\nCapturing screenshot at {minutes}:{seconds:02d}")
            if self.get_screenshot(video_path, minutes, seconds):
                successful += 1

        # Cleanup video file
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"\nCleaned up temporary video file")

        print(f"\nProcess completed.")
        print(f"Successfully captured {successful}/{len(timestamps)} screenshots")
        print(f"Screenshots saved in: {self.output_dir}")

        return successful > 0


# Example usage
if __name__ == "__main__":
    youtube_url = "https://youtube.com/watch?v=WbtQzAvhnRI"

    # List of timestamps to capture (minutes, seconds)
    timestamps = [
        (11, 18),  # Screenshot at 0:30
        (15, 4),  # Screenshot at 1:15
        (27, 36),  # Screenshot at 2:45
    ]

    extractor = YouTubeTimestampScreenshot(youtube_url, output_dir="timestamp_shots")
    extractor.capture_timestamps(timestamps)