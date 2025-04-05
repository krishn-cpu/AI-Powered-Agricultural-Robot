import cv2
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

class ImageProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path("data/processed_images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def preprocess_image(self, image_path, target_size=(224, 224)):
        """
        Preprocess image for ML model input
        Args:
            image_path: Path to the image file
            target_size: Desired output size (height, width)
        Returns:
            Preprocessed image array or None if processing fails
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Resize image
            image = cv2.resize(image, target_size)
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {str(e)}")
            return None
    
    def enhance_image(self, image_array):
        """
        Enhance image quality
        Args:
            image_array: Input image as numpy array
        Returns:
            Enhanced image array
        """
        try:
            # Convert to uint8 if normalized
            if image_array.dtype == np.float32 and image_array.max() <= 1.0:
                image_array = (image_array * 255).astype(np.uint8)
            
            # Apply enhancements
            # 1. Contrast Limited Adaptive Histogram Equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # 2. Slight sharpening
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]]) / 9.0
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Error enhancing image: {str(e)}")
            return image_array
    
    def detect_vegetation(self, image_array):
        """
        Detect vegetation in image using color thresholding
        Args:
            image_array: Input image as numpy array
        Returns:
            Mask of detected vegetation
        """
        try:
            # Convert to HSV color space
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            
            # Define green color range
            lower_green = np.array([35, 30, 30])
            upper_green = np.array([85, 255, 255])
            
            # Create mask for green vegetation
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            return mask
            
        except Exception as e:
            self.logger.error(f"Error detecting vegetation: {str(e)}")
            return None
    
    def analyze_plant_health(self, image_array):
        """
        Analyze plant health using color analysis
        Args:
            image_array: Input image as numpy array
        Returns:
            Dictionary containing health metrics
        """
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            
            # Get vegetation mask
            veg_mask = self.detect_vegetation(image_array)
            if veg_mask is None:
                raise ValueError("Failed to create vegetation mask")
            
            # Calculate metrics only for vegetation areas
            metrics = {
                "vegetation_coverage": (np.sum(veg_mask > 0) / veg_mask.size) * 100,
                "average_saturation": np.mean(hsv[:,:,1][veg_mask > 0]),
                "health_score": 0.0
            }
            
            # Calculate health score (simplified version)
            # Combines coverage and color saturation
            metrics["health_score"] = (
                0.6 * (metrics["vegetation_coverage"] / 100) +
                0.4 * (metrics["average_saturation"] / 255)
            ) * 100
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing plant health: {str(e)}")
            return None
    
    def save_processed_image(self, image_array, prefix="processed"):
        """
        Save processed image to cache directory
        Args:
            image_array: Image to save
            prefix: Prefix for the filename
        Returns:
            Path to saved image or None if saving fails
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.jpg"
            filepath = self.cache_dir / filename
            
            # Convert to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Save image
            cv2.imwrite(str(filepath), image_array)
            self.logger.info(f"Saved processed image to {filepath}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving processed image: {str(e)}")
            return None

if __name__ == "__main__":
    # Test image processing functions
    processor = ImageProcessor()
    
    # Test with a sample image if available
    test_image_path = Path("data/test_image.jpg")
    if test_image_path.exists():
        # Process image
        processed = processor.preprocess_image(test_image_path)
        if processed is not None:
            # Enhance image
            enhanced = processor.enhance_image(processed)
            
            # Analyze health
            health_metrics = processor.analyze_plant_health(enhanced)
            if health_metrics:
                print("\nPlant Health Analysis:")
                print("="*50)
                for metric, value in health_metrics.items():
                    print(f"{metric}: {value:.2f}")
                
                # Save processed image
                saved_path = processor.save_processed_image(enhanced)
                if saved_path:
                    print(f"\nProcessed image saved to: {saved_path}")
    else:
        print(f"Test image not found: {test_image_path}")
