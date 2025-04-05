import logging
from datetime import datetime
import random
import json
from pathlib import Path

class SoilAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.latest_reading = None
        self.data_path = Path("data/soil_readings")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Sensor thresholds
        self.thresholds = {
            "moisture": {"min": 20, "max": 80, "optimal": 50},
            "ph": {"min": 5.5, "max": 7.5, "optimal": 6.5},
            "nitrogen": {"min": 0, "max": 100, "optimal": 60},
            "phosphorus": {"min": 0, "max": 100, "optimal": 45},
            "potassium": {"min": 0, "max": 100, "optimal": 50},
            "temperature": {"min": 10, "max": 35, "optimal": 25}
        }
    
    def analyze_soil(self):
        """Perform soil analysis using sensors"""
        try:
            # In a real implementation, this would read from actual sensors
            # For demonstration, we'll simulate sensor readings
            reading = self._simulate_sensor_reading()
            
            # Analyze the readings
            analysis = self._analyze_reading(reading)
            
            # Save the reading
            self._save_reading(reading)
            
            self.latest_reading = reading
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error during soil analysis: {str(e)}")
            return None
    
    def _simulate_sensor_reading(self):
        """Simulate soil sensor readings"""
        reading = {
            "timestamp": datetime.now().isoformat(),
            "moisture": round(random.uniform(30, 70), 2),
            "ph": round(random.uniform(5.5, 7.5), 2),
            "nitrogen": round(random.uniform(40, 80), 2),
            "phosphorus": round(random.uniform(30, 60), 2),
            "potassium": round(random.uniform(35, 65), 2),
            "temperature": round(random.uniform(15, 30), 2)
        }
        return reading
    
    def _analyze_reading(self, reading):
        """Analyze soil readings and generate recommendations"""
        analysis = {
            "timestamp": reading["timestamp"],
            "conditions": {},
            "recommendations": []
        }
        
        # Analyze each parameter
        for param, value in reading.items():
            if param == "timestamp":
                continue
                
            thresholds = self.thresholds[param]
            condition = self._evaluate_condition(value, thresholds)
            analysis["conditions"][param] = condition
            
            if condition != "optimal":
                recommendation = self._generate_recommendation(param, value, condition)
                analysis["recommendations"].append(recommendation)
        
        return analysis
    
    def _evaluate_condition(self, value, thresholds):
        """Evaluate the condition of a soil parameter"""
        if value < thresholds["min"]:
            return "low"
        elif value > thresholds["max"]:
            return "high"
        elif abs(value - thresholds["optimal"]) <= (thresholds["max"] - thresholds["min"]) * 0.1:
            return "optimal"
        else:
            return "suboptimal"
    
    def _generate_recommendation(self, parameter, value, condition):
        """Generate recommendations based on soil conditions"""
        recommendations = {
            "moisture": {
                "low": "Increase irrigation frequency",
                "high": "Reduce irrigation and improve drainage",
                "suboptimal": "Adjust irrigation schedule"
            },
            "ph": {
                "low": "Apply lime to increase pH",
                "high": "Apply sulfur to decrease pH",
                "suboptimal": "Monitor pH levels"
            },
            "nitrogen": {
                "low": "Apply nitrogen-rich fertilizer",
                "high": "Reduce nitrogen application",
                "suboptimal": "Adjust nitrogen levels gradually"
            },
            "phosphorus": {
                "low": "Apply phosphate fertilizer",
                "high": "Reduce phosphorus application",
                "suboptimal": "Monitor phosphorus levels"
            },
            "potassium": {
                "low": "Apply potassium-rich fertilizer",
                "high": "Reduce potassium application",
                "suboptimal": "Adjust potassium levels"
            },
            "temperature": {
                "low": "Consider soil warming techniques",
                "high": "Apply mulch for temperature regulation",
                "suboptimal": "Monitor soil temperature"
            }
        }
        
        return {
            "parameter": parameter,
            "current_value": value,
            "condition": condition,
            "action": recommendations[parameter][condition]
        }
    
    def _save_reading(self, reading):
        """Save soil reading to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.data_path / f"soil_reading_{timestamp}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(reading, f, indent=4)
            self.logger.info(f"Soil reading saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save soil reading: {str(e)}")
    
    def get_latest_reading(self):
        """Get the most recent soil analysis reading"""
        return self.latest_reading if self.latest_reading else "No readings available"
    
    def get_historical_data(self, days=7):
        """Retrieve historical soil data"""
        try:
            data = []
            for file_path in self.data_path.glob("soil_reading_*.json"):
                with open(file_path, 'r') as f:
                    data.append(json.load(f))
            return data
        except Exception as e:
            self.logger.error(f"Error retrieving historical data: {str(e)}")
            return []

if __name__ == "__main__":
    # Test soil analyzer
    analyzer = SoilAnalyzer()
    analysis = analyzer.analyze_soil()
    
    if analysis:
        print("\nSoil Analysis Results:")
        print("="*50)
        print("\nConditions:")
        for param, condition in analysis["conditions"].items():
            print(f"{param}: {condition}")
        
        print("\nRecommendations:")
        for rec in analysis["recommendations"]:
            print(f"- {rec['parameter']}: {rec['action']}")
