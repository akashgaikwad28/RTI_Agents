import os
import json
from datetime import datetime
from typing import Dict, Any

class HTMLReportGenerator:
    def __init__(self, report_dir: str = "data/evaluation/reports"):
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)
        
    def generate_report(self, run_id: str, results: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RTI-Agent Evaluation Report - {run_id}</title>
            <style>
                body {{ font-family: -apple-system, system-ui; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                .metric-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin: 10px; display: inline-block; width: calc(33% - 45px); vertical-align: top; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .danger {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; border: 1px solid #dee2e6; text-align: left; }}
                th {{ background: #f8f9fa; }}
            </style>
        </head>
        <body>
            <h1>Enterprise AI Evaluation Report</h1>
            <p><strong>Run ID:</strong> {run_id}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            
            <h2>High-Level Metrics</h2>
            <div>
                <div class="metric-card">
                    <div>Average Hallucination Rate</div>
                    <div class="metric-value { 'danger' if results.get('hallucination_rate', 0) > 0.1 else 'success' }">
                        {results.get('hallucination_rate', 0):.2f}
                    </div>
                </div>
                <div class="metric-card">
                    <div>Average Latency (s)</div>
                    <div class="metric-value">
                        {results.get('latency', 0):.2f}s
                    </div>
                </div>
                <div class="metric-card">
                    <div>Compliance Score</div>
                    <div class="metric-value">
                        {results.get('compliance_score', 0):.2f}
                    </div>
                </div>
            </div>
            
            <h2>Detailed Logs</h2>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;">
{json.dumps(results, indent=2)}
            </pre>
        </body>
        </html>
        """
        
        filepath = os.path.join(self.report_dir, f"report_{run_id}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return filepath

class JSONExporter:
    pass
class CSVExporter:
    pass
class RegressionDashboard:
    pass
