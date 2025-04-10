import requests
import json
from typing import Dict, Any, List
import logging
from urllib.parse import urljoin

class BurpSuiteIntegration:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8080"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='burp_integration.log'
        )
        
    def start_scan(self, target_url: str, scan_config: Dict[str, Any] = None) -> str:
        """Start a new Burp Suite scan"""
        endpoint = urljoin(self.base_url, "/api/v1/scan")
        
        default_config = {
            "urls": [target_url],
            "scan_configuration": {
                "scan_type": "full",
                "reporting": {
                    "format": "json",
                    "include_evidence": True
                }
            }
        }
        
        config = scan_config or default_config
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=config
            )
            response.raise_for_status()
            scan_id = response.json().get('scan_id')
            logging.info(f"Started Burp Suite scan with ID: {scan_id}")
            return scan_id
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to start Burp Suite scan: {str(e)}")
            raise
            
    def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get the status of a running scan"""
        endpoint = urljoin(self.base_url, f"/api/v1/scan/{scan_id}")
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get scan status: {str(e)}")
            raise
            
    def get_scan_results(self, scan_id: str) -> Dict[str, Any]:
        """Get the results of a completed scan"""
        endpoint = urljoin(self.base_url, f"/api/v1/scan/{scan_id}/results")
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get scan results: {str(e)}")
            raise
            
    def stop_scan(self, scan_id: str) -> bool:
        """Stop a running scan"""
        endpoint = urljoin(self.base_url, f"/api/v1/scan/{scan_id}")
        
        try:
            response = requests.delete(
                endpoint,
                headers=self.headers
            )
            response.raise_for_status()
            logging.info(f"Successfully stopped scan: {scan_id}")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to stop scan: {str(e)}")
            return False
            
    def get_vulnerabilities(self, scan_id: str) -> List[Dict[str, Any]]:
        """Get a list of vulnerabilities found during the scan"""
        results = self.get_scan_results(scan_id)
        return results.get('vulnerabilities', [])
        
    def analyze_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and categorize vulnerabilities by severity and type"""
        analysis = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info').lower()
            if severity in analysis:
                analysis[severity].append(vuln)
                
        return analysis 