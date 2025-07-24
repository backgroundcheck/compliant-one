# Phase 2 Quick Start Guide

## 🚀 Getting Started with Advanced AI & Compliance Automation

This guide will help you quickly get up and running with Phase 2 capabilities.

## Prerequisites

- Python 3.8+
- CompliantOne base platform installed
- Required dependencies (see requirements.txt)

## Step 1: Verify Phase 2 Installation

```bash
# Run the Phase 2 demo to verify everything is working
cd /root/compliant-one
python phase2_demo.py
```

Expected output should show:
- ✅ Phase 2 services initialized
- AI Analytics capabilities
- Adverse Media Monitoring
- Risk Rules Engine
- Case Management System

## Step 2: Access the Enhanced Dashboard

```bash
# Start the enhanced dashboard with Phase 2 features
python -m streamlit run dashboard/main.py --server.port 8501
```

Navigate to: `http://localhost:8501`

**New Phase 2 Features in Dashboard:**
- AI Risk Analysis section
- Adverse Media Monitoring
- Risk Rules Management
- Case Management interface

## Step 3: Basic Usage Examples

### AI Risk Analysis

```python
from core.platform import CompliantOnePlatform, Customer

platform = CompliantOnePlatform()

# Create a customer for analysis
customer = Customer(
    customer_id="TEST_001",
    name="Test Corporation",
    customer_type="CORPORATE",
    jurisdiction="US",
    risk_category="MEDIUM"
)

# Run AI risk analysis
result = await platform.ai_risk_analysis(customer, "comprehensive")
print(f"Risk Score: {result['overall_risk_score']}")
```

### Adverse Media Monitoring

```python
# Monitor for adverse media
result = await platform.adverse_media_monitoring(
    "Test Corporation",
    {'max_results': 10}
)

print(f"Risk Level: {result['overall_assessment']['overall_risk_level']}")
print(f"News Articles: {result['news_media_results']['total_articles']}")
```

### Risk Rules Evaluation

```python
# Evaluate against risk rules
evaluation = await platform.evaluate_risk_rules(customer)
print(f"Rules Triggered: {evaluation['rules_triggered']}")
print(f"Risk Level: {evaluation['overall_risk_level']}")
```

### Case Management

```python
# Create a compliance case
case = await platform.create_compliance_case(
    title="High Risk Customer Review",
    description="Requires comprehensive review",
    case_type="customer_due_diligence",
    entity_id=customer.customer_id
)

print(f"Case Created: {case['case_number']}")
```

## Step 4: Configuration

### Environment Setup

Create a `.env` file in your project root:

```bash
# Phase 2 Configuration
AI_ANALYTICS_ENABLED=true
OSINT_ENABLED=true
RISK_RULES_ENABLED=true
CASE_MANAGEMENT_ENABLED=true

# Optional: Production API Keys
NEWS_API_KEY=your_news_api_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

### Risk Rules Configuration

Create custom rules in `config/risk_rules.json`:

```json
{
  "rules": [
    {
      "rule_id": "CUSTOM_001",
      "name": "High Value Transaction Alert",
      "conditions": [
        {"field": "amount", "operator": "greater_than", "value": 10000}
      ],
      "risk_level": "HIGH",
      "actions": ["send_alert", "require_review"]
    }
  ]
}
```

## Step 5: Testing with Sample Data

### Import Test Data

```bash
# Import sample sanctions data
python import_sanctions_csv.py --file data/sample_sanctions.csv

# Or use the web interface
python -m streamlit run dashboard/main.py
# Navigate to "Import Sanctions Data" section
```

### Run Comprehensive Assessment

```python
# Test comprehensive assessment
result = await platform.comprehensive_compliance_assessment(customer)
print(f"Final Risk Level: {result['overall_assessment']['risk_level']}")
```

## Step 6: Monitor Services

### Check Service Status

```python
status = await platform.get_service_status()
for service, info in status.items():
    availability = "✅" if info['available'] else "❌"
    print(f"{availability} {service}: {info['status']}")
```

### View Statistics

```python
# Get FATF coverage
coverage = await platform.get_fatf_coverage()
print(f"FATF Coverage: {coverage['coverage_percentage']:.1f}%")

# Risk rules statistics
if hasattr(platform, 'risk_rules_manager'):
    stats = platform.risk_rules_manager.get_statistics()
    print(f"Active Rules: {stats['rules']['enabled_rules']}")

# Case management statistics  
if hasattr(platform, 'case_management_system'):
    case_stats = platform.case_management_system.get_case_statistics()
    print(f"Open Cases: {case_stats['cases_by_status'].get('open', 0)}")
```

## Common Issues & Solutions

### Issue: AI Services Not Available

**Solution:** AI services run in mock mode by default. To enable full AI:

```bash
pip install scikit-learn torch numpy pandas
export AI_ANALYTICS_ENABLED=true
```

### Issue: OSINT Data Limited

**Solution:** Configure API keys for real data sources:

```bash
export NEWS_API_KEY=your_reuters_api_key
export TWITTER_BEARER_TOKEN=your_twitter_token
```

### Issue: Rules Not Triggering

**Solution:** Check rule configuration and customer data:

```python
# Debug rule evaluation
evaluation = await platform.evaluate_risk_rules(customer)
print(f"Rules evaluated: {evaluation['rules_evaluated']}")
print(f"Triggered rules: {evaluation.get('triggered_rules', [])}")
```

## Next Steps

1. **Explore Advanced Features:**
   - Configure custom risk rules
   - Set up real-time monitoring
   - Integrate with external systems

2. **Production Deployment:**
   - Configure production databases
   - Set up monitoring and alerting
   - Enable security features

3. **Training & Documentation:**
   - Review full Phase 2 documentation
   - Train compliance team on new features
   - Customize workflows for your organization

## Support

- **Demo Issues:** Run `python phase2_demo.py` for troubleshooting
- **Documentation:** See `docs/PHASE2.md` for comprehensive guide
- **Configuration:** Check `config/settings.py` for all options

---

**Phase 2 transforms your compliance operations with AI-powered automation and intelligence gathering capabilities.**
