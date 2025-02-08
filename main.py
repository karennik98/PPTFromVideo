import yt_dlp
import cv2
import os
import numpy as np


class YouTubeScreenshots:
    def __init__(self, url, output_dir="screenshots"):
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
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Get highest quality
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

    def extract_frames(self, video_path, interval_seconds=30, scene_threshold=30):
        """
        Extract high-quality frames from video
        """
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return 0

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video file")
            return 0

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"Video properties:")
        print(f"Resolution: {width}x{height}")
        print(f"FPS: {fps}")
        print(f"Total frames: {total_frames}")
        print(f"Duration: {total_frames / fps:.2f} seconds")

        # Initialize variables for scene detection
        prev_frame = None
        frame_count = 0
        last_captured = -interval_seconds * fps
        screenshots_taken = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to grayscale for scene detection only
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            except Exception as e:
                print(f"Error converting frame to grayscale: {str(e)}")
                continue

            should_capture = False

            if prev_frame is not None:
                # Calculate difference between current and previous frame
                diff = cv2.absdiff(gray, prev_frame)
                mean_diff = np.mean(diff)

                # Detect scene change
                if mean_diff > scene_threshold and (frame_count - last_captured) > fps * 5:
                    should_capture = True

                # Also capture frames at regular intervals
                elif frame_count % (interval_seconds * fps) == 0:
                    should_capture = True

            if should_capture:
                # Format timestamp in a Windows-friendly way
                seconds = int(frame_count / fps)
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                timestamp = f"{hours:02d}-{minutes:02d}-{secs:02d}"

                # Save the frame in high quality
                frame_path = os.path.join(self.output_dir, f"screenshot_{screenshots_taken:03d}_{timestamp}.png")

                try:
                    # Save as PNG for better quality
                    success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                    if success:
                        screenshots_taken += 1
                        print(f"Saved screenshot {screenshots_taken} to: {frame_path}")
                        print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
                    else:
                        print(f"Failed to save screenshot to: {frame_path}")
                except Exception as e:
                    print(f"Error saving screenshot: {str(e)}")

                last_captured = frame_count

            prev_frame = gray
            frame_count += 1

            # Print progress every 1000 frames
            if frame_count % 1000 == 0:
                print(f"Processed {frame_count}/{total_frames} frames")

        cap.release()

        # Verify final results
        actual_files = [f for f in os.listdir(self.output_dir) if f.endswith('.png')]
        print(f"\nFinal verification:")
        print(f"Screenshots taken: {screenshots_taken}")
        print(f"Files in directory: {len(actual_files)}")

        return screenshots_taken

    def process(self):
        """Main processing function"""
        # Download video
        video_path = self.download_video()
        if not video_path:
            return False

        # Extract frames
        print("\nExtracting screenshots...")
        num_screenshots = self.extract_frames(video_path)

        # Cleanup video file
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Cleaned up temporary video file: {video_path}")

        if num_screenshots > 0:
            print(f"\nProcess completed successfully.")
            print(f"Screenshots saved in: {self.output_dir}")
            print(f"Total screenshots: {num_screenshots}")
        else:
            print("\nProcess completed but no screenshots were saved.")
            print("Please check the error messages above.")

        return num_screenshots > 0


if __name__ == "__main__":
    youtube_url = "https://youtube.com/watch?v=WbtQzAvhnRI"
    extractor = YouTubeScreenshots(youtube_url, output_dir="my_screenshots")
    extractor.process()