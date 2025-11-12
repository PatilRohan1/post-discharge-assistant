import json
from typing import Optional, Dict, List
from pathlib import Path
from src.utils.logger import Logger
from src.constants.environment_constants import EnvironmentConstants


class PatientDatabase:
    def __init__(self):
        self.patients_path = Path(EnvironmentConstants.PATIENTS_JSON_PATH.value)
        self.patients = self._load_patients()
        Logger.log_info_message(f"Loaded {len(self.patients)} patients from database")
    
    def _load_patients(self) -> List[Dict]:
        """Load patients from JSON file"""
        try:
            if self.patients_path.exists():
                with open(self.patients_path, 'r') as f:
                    return json.load(f)
            else:
                Logger.log_error_message(
                    Exception("Patients file not found"), 
                    f"File not found: {self.patients_path}"
                )
                return []
        except Exception as e:
            Logger.log_error_message(e, "Error loading patients database")
            return []
    
    def find_patient_by_name(self, name: str) -> Optional[Dict]:
      
        name_lower = name.lower().strip()
        
        # Exact match first
        for patient in self.patients:
            if patient["patient_name"].lower() == name_lower:
                Logger.log_info_message(f"Found patient (exact match): {patient['patient_name']}")
                return patient
        
        # Partial match
        for patient in self.patients:
            patient_name_lower = patient["patient_name"].lower()
            if name_lower in patient_name_lower or patient_name_lower in name_lower:
                Logger.log_info_message(f"Found patient (partial match): {patient['patient_name']}")
                return patient
        
        Logger.log_info_message(f"No patient found for name: {name}")
        return None
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients"""
        return self.patients
    
    def format_patient_info(self, patient):
        """Format patient information for display"""
        return f"""
    Patient Name: {patient['patient_name']}
    Discharge Date: {patient['discharge_date']}
    Primary Diagnosis: {patient['primary_diagnosis']}
    Medications: {', '.join(patient['medications'])}
    Dietary Restrictions: {patient.get('dietary_restrictions', 'None specified')}
    Follow-up: {patient['follow_up']}
    Warning Signs: {patient.get('warning_signs', 'None specified')}
    """