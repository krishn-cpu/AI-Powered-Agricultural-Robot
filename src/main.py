import cv2
import numpy as np
from datetime import datetime
import logging
from pathlib import Path

# Local imports
from drone_controller import DroneController
from plant_disease_classifier import PlantDiseaseClassifier
from soil_analyzer import SoilAnalyzer

class AgriculturalRobot:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Agricultural Robot System...")
        
        # Initialize components
        self.drone = DroneController()
        self.disease_classifier = PlantDiseaseClassifier()
        self.soil_analyzer = SoilAnalyzer()
        
        # Status flags
        self.is_monitoring = False
        self.emergency_stop = False
        
    def start_monitoring(self):
        """Start the monitoring process"""
        self.logger.info("Starting monitoring sequence...")
        self.is_monitoring = True
        
        try:
            # Start drone surveillance
            self.drone.start_mission()
            
            # Analyze soil conditions
            soil_data = self.soil_analyzer.analyze_soil()
            self.logger.info(f"Soil Analysis Results: {soil_data}")
            
            # Check for plant diseases
            image_path = "data/latest_capture.jpg"
            if Path(image_path).exists():
                disease_result = self.disease_classifier.detect_disease(image_path)
                self.logger.info(f"Disease Detection Results: {disease_result}")
            
        except Exception as e:
            self.logger.error(f"Error during monitoring: {str(e)}")
            self.emergency_stop = True
        
        finally:
            self.is_monitoring = False
            if self.emergency_stop:
                self.emergency_shutdown()
    
    def emergency_shutdown(self):
        """Handle emergency shutdown procedure"""
        self.logger.warning("Emergency shutdown initiated!")
        self.drone.return_to_home()
        self.is_monitoring = False
        self.emergency_stop = True
    
    def generate_report(self):
        """Generate monitoring report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "timestamp": timestamp,
            "soil_health": self.soil_analyzer.get_latest_reading(),
            "detected_diseases": self.disease_classifier.get_latest_results(),
            "drone_status": self.drone.get_status()
        }
        return report

def main():
    robot = AgriculturalRobot()
    
    try:
        # Start monitoring sequence
        robot.start_monitoring()
        
        # Generate and display report
        report = robot.generate_report()
        print("
Monitoring Report:")
        print("="*50)
        for key, value in report.items():
            print(f"{key}: {value}")
            
    except KeyboardInterrupt:
        print("
Program terminated by user")
        robot.emergency_shutdown()
    
    except Exception as e:
        print(f"
An error occurred: {str(e)}")
        robot.emergency_shutdown()

if __name__ == "__main__":
    main()

