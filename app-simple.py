from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(
    title="Compliant-One Platform",
    description="Enterprise RegTech Platform",
    version="3.0.0"
)

@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliant-One Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
            .header { text-align: center; color: white; margin-bottom: 40px; }
            .header h1 { font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.2em; margin: 10px 0; opacity: 0.9; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 40px 0; }
            .feature { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
            .feature:hover { transform: translateY(-5px); }
            .feature h3 { color: #2c3e50; margin-top: 0; font-size: 1.3em; }
            .feature p { color: #666; line-height: 1.6; }
            .links { text-align: center; margin-top: 40px; }
            .api-link { background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 10px; font-weight: bold; transition: background 0.3s; }
            .api-link:hover { background: #2980b9; }
            .status { background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Compliant-One</h1>
                <p>Enterprise RegTech Platform</p>
                <div class="status">✅ System Online & Ready</div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔍 Sanctions Screening</h3>
                    <p>Real-time screening against global sanctions lists including OFAC, EU, UN, and other regulatory databases.</p>
                </div>
                
                <div class="feature">
                    <h3>🔐 KYC Verification</h3>
                    <p>Comprehensive identity verification and compliance checks with document validation and risk assessment.</p>
                </div>
                
                <div class="feature">
                    <h3>🕵️ OSINT Intelligence</h3>
                    <p>Open source intelligence gathering and analysis for enhanced due diligence and risk monitoring.</p>
                </div>
                
                <div class="feature">
                    <h3>⚠️ Threat Intelligence</h3>
                    <p>Real-time threat monitoring, breach detection, and dark web surveillance for proactive security.</p>
                </div>
                
                <div class="feature">
                    <h3>📊 Compliance Reporting</h3>
                    <p>Automated regulatory reporting with customizable templates for various jurisdictions and frameworks.</p>
                </div>
                
                <div class="feature">
                    <h3>🔄 Transaction Monitoring</h3>
                    <p>Advanced AML transaction monitoring with machine learning-based suspicious activity detection.</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs" class="api-link">📚 API Documentation</a>
                <a href="/health" class="api-link">🏥 Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "healthy", "service": "compliant-one", "version": "3.0.0", "features": ["sanctions", "kyc", "osint", "threat-intel"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)