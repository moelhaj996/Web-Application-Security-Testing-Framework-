import argparse
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv
from core.scanner import SecurityScanner
from core.reporter import SecurityReporter
from integrations.burp_suite import BurpSuiteIntegration
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='security_framework.log'
    )

def load_configuration():
    load_dotenv()
    return {
        'burp_api_key': os.getenv('BURP_API_KEY'),
        'burp_base_url': os.getenv('BURP_BASE_URL', 'http://localhost:8080')
    }

def run_security_scan(target_url: str, config: Dict[str, Any]):
    # Initialize components
    scanner = SecurityScanner(target_url)
    reporter = SecurityReporter()
    burp = BurpSuiteIntegration(
        api_key=config['burp_api_key'],
        base_url=config['burp_base_url']
    )
    
    try:
        # Run automated scans
        logging.info("Starting automated security scans...")
        scan_results = scanner.run_comprehensive_scan()
        
        # Run Burp Suite scan
        logging.info("Starting Burp Suite scan...")
        scan_id = burp.start_scan(target_url)
        
        # Wait for Burp Suite scan to complete
        while True:
            status = burp.get_scan_status(scan_id)
            if status.get('status') == 'completed':
                break
            elif status.get('status') == 'failed':
                raise Exception("Burp Suite scan failed")
                
        # Get Burp Suite results
        burp_results = burp.get_scan_results(scan_id)
        vulnerabilities = burp.get_vulnerabilities(scan_id)
        analysis = burp.analyze_vulnerabilities(vulnerabilities)
        
        # Merge results
        scan_results['burp_suite'] = analysis
        
        # Generate reports
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_report = f'reports/security_report_{timestamp}.pdf'
        excel_report = f'reports/security_report_{timestamp}.xlsx'
        
        os.makedirs('reports', exist_ok=True)
        reporter.create_pdf_report(scan_results, pdf_report)
        reporter.generate_excel_report(scan_results, excel_report)
        
        logging.info(f"Security scan completed. Reports generated: {pdf_report}, {excel_report}")
        
    except Exception as e:
        logging.error(f"Error during security scan: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Web Application Security Testing Framework')
    parser.add_argument('target_url', help='Target URL to scan')
    args = parser.parse_args()
    
    setup_logging()
    config = load_configuration()
    
    try:
        run_security_scan(args.target_url, config)
    except Exception as e:
        logging.error(f"Framework execution failed: {str(e)}")
        raise

if __name__ == '__main__':
    main() 