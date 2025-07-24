#!/usr/bin/env python3
"""
Phase 2 Demonstration Script
🚀 Advanced AI & Compliance Automation Demo
Shows all Phase 2 capabilities: AI Analytics, Adverse Media, Risk Rules, Case Management
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.platform import CompliantOnePlatform, Customer
from utils.logger import get_logger

class Phase2Demo:
    """Phase 2 comprehensive demonstration"""
    
    def __init__(self):
        self.logger = get_logger("phase2_demo")
        self.platform = CompliantOnePlatform()
        
    async def run_comprehensive_demo(self):
        """Run comprehensive Phase 2 demonstration"""
        print("\n" + "="*80)
        print("🚀 PHASE 2: ADVANCED AI & COMPLIANCE AUTOMATION DEMO")
        print("="*80)
        print("Demonstrating: AI Analytics, Adverse Media, Risk Rules, Case Management")
        print("="*80)
        
        # Check if Phase 2 is enabled
        if not hasattr(self.platform, 'phase2_enabled') or not self.platform.phase2_enabled:
            print("\n❌ Phase 2 services not available")
            print("Phase 2 services are running in mock mode for demonstration")
            print("In production, these would connect to real AI/ML services")
        else:
            print("\n✅ Phase 2 services initialized and ready")
        
        # Demo scenarios
        await self.demo_scenario_1()
        await self.demo_scenario_2()
        await self.demo_scenario_3()
        await self.demo_comprehensive_assessment()
        
        print("\n" + "="*80)
        print("🎉 PHASE 2 DEMONSTRATION COMPLETED")
        print("="*80)
    
    async def demo_scenario_1(self):
        """Demo Scenario 1: High-Risk Corporate Customer"""
        print("\n" + "-"*60)
        print("📋 SCENARIO 1: High-Risk Corporate Customer Analysis")
        print("-"*60)
        
        # Create high-risk customer
        customer = Customer(
            customer_id="CORP_001",
            name="Global Trade Solutions Ltd",
            customer_type="CORPORATE",
            jurisdiction="PK",  # High-risk jurisdiction
            risk_category="HIGH",
            metadata={
                'pep_status': True,
                'sanctions_score': 0.85,
                'adverse_media_score': 0.72,
                'annual_revenue': 50000000,
                'business_type': 'import_export'
            }
        )
        
        print(f"Customer: {customer.name}")
        print(f"Type: {customer.customer_type}")
        print(f"Jurisdiction: {customer.jurisdiction}")
        print(f"Risk Category: {customer.risk_category}")
        
        # 1. AI Risk Analysis
        print(f"\n🤖 AI Risk Analysis:")
        ai_analysis = await self.platform.ai_risk_analysis(customer, "comprehensive")
        if 'error' not in ai_analysis:
            print(f"   Overall AI Risk Score: {ai_analysis.get('overall_risk_score', 0):.3f}")
            print(f"   Analysis Type: {ai_analysis.get('analysis_type')}")
            
            # Show AI recommendations
            recommendations = ai_analysis.get('recommendations', [])
            if recommendations:
                print(f"   AI Recommendations:")
                for rec in recommendations:
                    print(f"   - {rec}")
        else:
            print(f"   ⚠️  AI Analysis: {ai_analysis['error']}")
        
        # 2. Adverse Media Monitoring
        print(f"\n📰 Adverse Media Monitoring:")
        adverse_media = await self.platform.adverse_media_monitoring(
            customer.name, 
            {'entity_type': 'corporate', 'max_results': 10}
        )
        if 'error' not in adverse_media:
            overall_assessment = adverse_media.get('overall_assessment', {})
            print(f"   Risk Level: {overall_assessment.get('overall_risk_level', 'UNKNOWN')}")
            print(f"   Risk Score: {overall_assessment.get('overall_risk_score', 0):.3f}")
            print(f"   Sentiment: {overall_assessment.get('overall_sentiment', 0):.3f}")
            
            news_results = adverse_media.get('news_media_results', {})
            print(f"   News Articles: {news_results.get('total_articles', 0)}")
            print(f"   Adverse Articles: {news_results.get('adverse_articles', 0)}")
            
            social_results = adverse_media.get('social_media_results', {})
            print(f"   Social Media Mentions: {social_results.get('total_mentions', 0)}")
            print(f"   Adverse Mentions: {social_results.get('adverse_mentions', 0)}")
        else:
            print(f"   ⚠️  Adverse Media: {adverse_media['error']}")
        
        # 3. Risk Rules Evaluation
        print(f"\n⚖️  Risk Rules Evaluation:")
        rules_evaluation = await self.platform.evaluate_risk_rules(customer)
        if 'error' not in rules_evaluation:
            print(f"   Rules Evaluated: {rules_evaluation.get('rules_evaluated', 0)}")
            print(f"   Rules Triggered: {rules_evaluation.get('rules_triggered', 0)}")
            print(f"   Overall Risk Level: {rules_evaluation.get('overall_risk_level', 'UNKNOWN')}")
            
            triggered_rules = rules_evaluation.get('triggered_rules', [])
            if triggered_rules:
                print(f"   Triggered Rules:")
                for rule in triggered_rules[:3]:  # Show first 3
                    print(f"   - {rule['rule_name']} (Risk: {rule['risk_level']})")
        else:
            print(f"   ⚠️  Rules Evaluation: {rules_evaluation['error']}")
        
        # 4. Case Creation (if high risk)
        print(f"\n📝 Case Management:")
        case_result = await self.platform.create_compliance_case(
            title=f"High Risk Corporate Review - {customer.name}",
            description=f"Comprehensive review of high-risk corporate customer {customer.customer_id}",
            case_type="customer_due_diligence",
            created_by="compliance_analyst",
            entity_id=customer.customer_id,
            entity_name=customer.name
        )
        
        if 'error' not in case_result:
            print(f"   Case Created: {case_result.get('case_number')}")
            print(f"   Priority: {case_result.get('priority')}")
            print(f"   Status: {case_result.get('status')}")
            print(f"   Due Date: {case_result.get('due_date', 'Not set')}")
        else:
            print(f"   ⚠️  Case Creation: {case_result['error']}")
    
    async def demo_scenario_2(self):
        """Demo Scenario 2: PEP Individual with Sanctions Risk"""
        print("\n" + "-"*60)
        print("👤 SCENARIO 2: PEP Individual with Sanctions Risk")
        print("-"*60)
        
        customer = Customer(
            customer_id="IND_002",
            name="Alexander Petrov",
            customer_type="INDIVIDUAL",
            jurisdiction="RU",
            risk_category="CRITICAL",
            metadata={
                'pep_status': True,
                'sanctions_score': 0.92,
                'adverse_media_score': 0.88,
                'occupation': 'government_official',
                'source_of_wealth': 'government_salary'
            }
        )
        
        print(f"Customer: {customer.name}")
        print(f"Type: {customer.customer_type}")
        print(f"PEP Status: {customer.metadata.get('pep_status')}")
        print(f"Sanctions Score: {customer.metadata.get('sanctions_score')}")
        
        # Comprehensive assessment
        print(f"\n🔍 Comprehensive Assessment:")
        assessment = await self.platform.comprehensive_compliance_assessment(customer)
        
        if 'error' not in assessment:
            overall = assessment.get('overall_assessment', {})
            print(f"   Final Risk Level: {overall.get('risk_level', 'UNKNOWN')}")
            print(f"   Overall Score: {overall.get('overall_risk_score', 0):.3f}")
            
            risk_indicators = overall.get('risk_indicators', [])
            print(f"   Risk Indicators: {len(risk_indicators)}")
            for indicator in risk_indicators:
                print(f"   - {indicator}")
            
            print(f"   Recommendation: {overall.get('recommendation', 'None')}")
            
            # Check if case was auto-created
            if 'case_created' in assessment:
                case_info = assessment['case_created']
                print(f"   🚨 AUTO-CREATED CASE: {case_info.get('case_number')}")
        else:
            print(f"   ⚠️  Assessment Error: {assessment['error']}")
    
    async def demo_scenario_3(self):
        """Demo Scenario 3: Suspicious Transaction Monitoring"""
        print("\n" + "-"*60)
        print("💰 SCENARIO 3: Suspicious Transaction Monitoring")
        print("-"*60)
        
        customer = Customer(
            customer_id="CORP_003",
            name="Tech Innovations Inc",
            customer_type="CORPORATE",
            jurisdiction="US",
            risk_category="MEDIUM"
        )
        
        # Simulate high-value transaction
        transaction_data = {
            'transaction_id': 'TXN_789012',
            'amount': 250000,  # High value
            'currency': 'USD',
            'destination_country': 'PK',  # High-risk country
            'transaction_type': 'wire_transfer',
            'purpose': 'business_payment'
        }
        
        print(f"Customer: {customer.name}")
        print(f"Transaction Amount: ${transaction_data['amount']:,}")
        print(f"Destination: {transaction_data['destination_country']}")
        
        # Evaluate transaction against risk rules
        print(f"\n⚖️  Transaction Risk Rules:")
        rules_evaluation = await self.platform.evaluate_risk_rules(customer, transaction_data)
        
        if 'error' not in rules_evaluation:
            print(f"   Rules Triggered: {rules_evaluation.get('rules_triggered', 0)}")
            
            triggered_rules = rules_evaluation.get('triggered_rules', [])
            for rule in triggered_rules:
                print(f"   - {rule['rule_name']}")
                print(f"     Risk Level: {rule['risk_level']}")
                print(f"     Confidence: {rule['confidence_score']:.3f}")
                
                # Show executed actions
                actions = rule.get('actions_executed', [])
                if actions:
                    print(f"     Actions: {', '.join(actions)}")
        else:
            print(f"   ⚠️  Rules Error: {rules_evaluation['error']}")
        
        # AI analysis for transaction pattern
        print(f"\n🤖 AI Transaction Analysis:")
        # Add transaction context to customer metadata
        customer.metadata.update({
            'recent_transaction': transaction_data,
            'transaction_pattern': 'high_value_international'
        })
        
        ai_analysis = await self.platform.ai_risk_analysis(customer, "anomaly")
        if 'error' not in ai_analysis:
            print(f"   Anomaly Score: {ai_analysis.get('overall_risk_score', 0):.3f}")
            
            ai_results = ai_analysis.get('ai_analysis_results', {})
            if 'anomaly_detection' in ai_results:
                anomalies = ai_results['anomaly_detection'].get('detected_anomalies', [])
                print(f"   Detected Anomalies: {len(anomalies)}")
                for anomaly in anomalies[:2]:  # Show first 2
                    print(f"   - {anomaly}")
        else:
            print(f"   ⚠️  AI Analysis: {ai_analysis['error']}")
    
    async def demo_comprehensive_assessment(self):
        """Demo comprehensive assessment capabilities"""
        print("\n" + "-"*60)
        print("🎯 COMPREHENSIVE PLATFORM ASSESSMENT")
        print("-"*60)
        
        # Get platform status
        print(f"\n📊 Platform Status:")
        status = await self.platform.get_service_status()
        
        available_services = sum(1 for service_status in status.values() if service_status.get('available', False))
        total_services = len(status)
        
        print(f"   Services Available: {available_services}/{total_services}")
        
        # Show Phase 2 specific services
        phase2_services = ['ai_analytics', 'adverse_media', 'risk_rules', 'case_management']
        for service in phase2_services:
            if service in status:
                service_status = status[service]
                availability = "✅" if service_status.get('available') else "❌"
                print(f"   {availability} {service.replace('_', ' ').title()}")
        
        # FATF Coverage
        print(f"\n📋 FATF Compliance Coverage:")
        coverage = await self.platform.get_fatf_coverage()
        print(f"   Coverage: {coverage.get('coverage_percentage', 0):.1f}%")
        print(f"   Covered Recommendations: {coverage.get('covered_recommendations', 0)}")
        print(f"   Total Recommendations: {coverage.get('total_recommendations', 0)}")
        
        # Service-specific coverage
        coverage_by_service = coverage.get('coverage_by_service', {})
        if coverage_by_service:
            print(f"   Coverage by Service:")
            for service, recommendations in coverage_by_service.items():
                print(f"   - {service}: {len(recommendations)} recommendations")
        
        # Show statistics if available
        if hasattr(self.platform, 'risk_rules_manager'):
            print(f"\n📈 Risk Rules Statistics:")
            try:
                stats = self.platform.risk_rules_manager.get_statistics()
                rules_stats = stats.get('rules', {})
                print(f"   Total Rules: {rules_stats.get('total_rules', 0)}")
                print(f"   Enabled Rules: {rules_stats.get('enabled_rules', 0)}")
                
                eval_stats = stats.get('evaluation_engine', {})
                print(f"   Total Evaluations: {eval_stats.get('total_evaluations', 0)}")
                print(f"   Rules Triggered: {eval_stats.get('rules_triggered', 0)}")
            except Exception as e:
                print(f"   ⚠️  Stats Error: {e}")
        
        if hasattr(self.platform, 'case_management_system'):
            print(f"\n📁 Case Management Statistics:")
            try:
                case_stats = self.platform.case_management_system.get_case_statistics()
                print(f"   Total Cases: {case_stats.get('total_cases', 0)}")
                print(f"   Overdue Cases: {case_stats.get('overdue_cases', 0)}")
                print(f"   SLA Compliance: {case_stats.get('sla_compliance', 0):.1f}%")
                
                # Show case distribution
                cases_by_status = case_stats.get('cases_by_status', {})
                if cases_by_status:
                    print(f"   Cases by Status:")
                    for status, count in cases_by_status.items():
                        print(f"   - {status}: {count}")
            except Exception as e:
                print(f"   ⚠️  Case Stats Error: {e}")

async def main():
    """Main demo function"""
    print("Starting Phase 2 Demo...")
    
    demo = Phase2Demo()
    
    try:
        await demo.run_comprehensive_demo()
        
        print(f"\n💡 Phase 2 Key Features Demonstrated:")
        print(f"   ✅ AI-Powered Risk Analytics (Anomaly Detection, Predictive Analytics)")
        print(f"   ✅ Advanced OSINT & Adverse Media Monitoring")
        print(f"   ✅ Customizable Risk Rules Engine") 
        print(f"   ✅ Intelligent Case Management System")
        print(f"   ✅ Comprehensive Compliance Assessment")
        
        print(f"\n🚀 Phase 2 provides advanced AI and automation capabilities")
        print(f"   that significantly enhance compliance effectiveness and efficiency.")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
