#!/usr/bin/env python3
"""
Phase 2 CSV Import Integration Demo
🔄 Demonstrates how Phase 2 enhances CSV import with AI analysis
"""

import asyncio
import csv
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.platform import CompliantOnePlatform, Customer
from services.sanctions.csv_importer import SanctionsCSVImporter
from utils.logger import get_logger

class Phase2CSVDemo:
    """CSV Import with Phase 2 AI Analysis Demo"""
    
    def __init__(self):
        self.logger = get_logger("phase2_csv_demo")
        self.platform = CompliantOnePlatform()
        self.csv_importer = SanctionsCSVImporter()
    
    async def run_csv_demo(self):
        """Run comprehensive CSV import demo with Phase 2 analysis"""
        print("\n" + "="*80)
        print("🔄 PHASE 2 CSV IMPORT INTEGRATION DEMO")
        print("="*80)
        print("Demonstrating: CSV Import + AI Analysis + Automated Case Creation")
        print("="*80)
        
        # Create sample CSV data
        await self.create_sample_csv_data()
        
        # Import CSV with Phase 2 analysis
        await self.demo_enhanced_csv_import()
        
        # Show post-import analysis
        await self.demo_post_import_analysis()
        
        # Demonstrate ongoing monitoring
        await self.demo_ongoing_monitoring()
        
        print("\n" + "="*80)
        print("🎉 PHASE 2 CSV IMPORT DEMO COMPLETED")
        print("="*80)
    
    async def create_sample_csv_data(self):
        """Create sample CSV data for demonstration"""
        print("\n" + "-"*60)
        print("📄 Creating Sample Sanctions CSV Data")
        print("-"*60)
        
        # Sample high-risk entities for demonstration
        sample_data = [
            {
                'name': 'Viktor Kozlov',
                'type': 'INDIVIDUAL',
                'date_of_birth': '1965-03-15',
                'nationality': 'RU',
                'sanctions_program': 'OFAC_SDN',
                'designation_date': '2022-02-26',
                'reason': 'Senior government official involved in policies threatening Ukraine',
                'addresses': 'Moscow, Russia',
                'pep_status': 'TRUE',
                'risk_score': '0.95'
            },
            {
                'name': 'Illicit Finance Network LLC',
                'type': 'ENTITY',
                'incorporation_country': 'BVI',
                'sanctions_program': 'OFAC_SDN',
                'designation_date': '2023-01-15',
                'reason': 'Front company for sanctioned individuals',
                'addresses': 'Road Town, British Virgin Islands',
                'beneficial_owners': 'Viktor Kozlov',
                'risk_score': '0.88'
            },
            {
                'name': 'Ahmed Al-Mansouri',
                'type': 'INDIVIDUAL',
                'date_of_birth': '1970-08-22',
                'nationality': 'AE',
                'sanctions_program': 'UN_CONSOLIDATED',
                'designation_date': '2023-06-10',
                'reason': 'Terrorism financing activities',
                'addresses': 'Dubai, UAE',
                'pep_status': 'FALSE',
                'risk_score': '0.92'
            },
            {
                'name': 'Global Trade Solutions FZE',
                'type': 'ENTITY',
                'incorporation_country': 'AE',
                'sanctions_program': 'EU_CONSOLIDATED',
                'designation_date': '2023-03-20',
                'reason': 'Sanctions evasion activities',
                'addresses': 'Dubai International Financial Centre',
                'beneficial_owners': 'Ahmed Al-Mansouri',
                'risk_score': '0.85'
            }
        ]
        
        # Create temporary CSV file
        self.temp_csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        # Write CSV data
        fieldnames = sample_data[0].keys()
        writer = csv.DictWriter(self.temp_csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
        self.temp_csv_file.close()
        
        print(f"✅ Created sample CSV: {self.temp_csv_file.name}")
        print(f"📊 Records: {len(sample_data)} high-risk entities")
        print(f"🎯 Types: {len([r for r in sample_data if r['type'] == 'INDIVIDUAL'])} individuals, {len([r for r in sample_data if r['type'] == 'ENTITY'])} entities")
    
    async def demo_enhanced_csv_import(self):
        """Demonstrate enhanced CSV import with Phase 2 analysis"""
        print("\n" + "-"*60)
        print("🚀 Enhanced CSV Import with Phase 2 Analysis")
        print("-"*60)
        
        # Import CSV file
        print("📥 Importing CSV file...")
        try:
            result = self.csv_importer.import_csv_file(
                csv_file=self.temp_csv_file.name,
                list_name="DEMO_HIGH_RISK_ENTITIES",
                auto_detect_format=True
            )
            
            print(f"✅ Import completed:")
            print(f"   Records processed: {result.get('total_records', 0)}")
            print(f"   Successfully imported: {result.get('successful_imports', 0)}")
            print(f"   Errors: {result.get('errors', 0)}")
            
        except Exception as e:
            print(f"❌ Import error: {e}")
            return
        
        # Phase 2 Enhanced Analysis
        print(f"\n🤖 Phase 2 AI Analysis of Imported Data:")
        
        # Analyze each imported entity
        imported_entities = [
            'Viktor Kozlov',
            'Illicit Finance Network LLC', 
            'Ahmed Al-Mansouri',
            'Global Trade Solutions FZE'
        ]
        
        high_risk_cases = []
        
        for entity_name in imported_entities:
            print(f"\n   Analyzing: {entity_name}")
            
            # Create customer object for analysis
            customer = Customer(
                customer_id=f"IMPORTED_{hash(entity_name) % 10000}",
                name=entity_name,
                customer_type="INDIVIDUAL" if any(name in entity_name for name in ['Viktor', 'Ahmed']) else "CORPORATE",
                jurisdiction="RU" if "Viktor" in entity_name else "AE" if "Ahmed" in entity_name or "FZE" in entity_name else "BVI",
                risk_category="CRITICAL"
            )
            
            # Run comprehensive assessment
            assessment = await self.platform.comprehensive_compliance_assessment(customer)
            
            if 'error' not in assessment:
                overall = assessment.get('overall_assessment', {})
                risk_level = overall.get('risk_level', 'HIGH')
                
                print(f"      AI Risk Assessment: {risk_level}")
                print(f"      Risk Score: {overall.get('overall_risk_score', 0.0):.3f}")
                
                # Check if case was auto-created
                if 'case_created' in assessment:
                    case_info = assessment['case_created']
                    high_risk_cases.append({
                        'entity': entity_name,
                        'case_number': case_info.get('case_number'),
                        'risk_level': risk_level
                    })
                    print(f"      🚨 Auto-created case: {case_info.get('case_number')}")
            else:
                print(f"      ⚠️  Analysis error: {assessment['error']}")
        
        # Summary of auto-created cases
        if high_risk_cases:
            print(f"\n📋 Auto-Created Investigation Cases:")
            for case in high_risk_cases:
                print(f"   • {case['entity']}: {case['case_number']} ({case['risk_level']} risk)")
        
        # Adverse media monitoring for imported entities
        print(f"\n📰 Adverse Media Monitoring for Imported Entities:")
        
        for entity_name in imported_entities[:2]:  # Check first 2 for demo
            print(f"\n   Monitoring: {entity_name}")
            
            adverse_result = await self.platform.adverse_media_monitoring(
                entity_name,
                {'max_results': 5, 'timeframe': '90_days'}
            )
            
            if 'error' not in adverse_result:
                overall_assessment = adverse_result.get('overall_assessment', {})
                print(f"      Media Risk Level: {overall_assessment.get('overall_risk_level', 'UNKNOWN')}")
                
                news_results = adverse_result.get('news_media_results', {})
                print(f"      News Articles: {news_results.get('total_articles', 0)}")
                print(f"      Adverse Articles: {news_results.get('adverse_articles', 0)}")
            else:
                print(f"      ⚠️  Monitoring error: {adverse_result['error']}")
    
    async def demo_post_import_analysis(self):
        """Demonstrate post-import analysis capabilities"""
        print("\n" + "-"*60)
        print("📊 Post-Import Analysis & Intelligence")
        print("-"*60)
        
        # Get import statistics
        print("📈 Import Statistics:")
        stats = self.csv_importer.get_import_statistics()
        
        print(f"   Total Sanctions Entities: {stats.get('total_sanctions_entities', 0)}")
        print(f"   Total PEP Entities: {stats.get('total_pep_entities', 0)}")
        print(f"   Lists in Database: {stats.get('total_lists', 0)}")
        print(f"   Last Import: {stats.get('last_import_date', 'Unknown')}")
        
        # Network analysis
        print(f"\n🕸️  Network Analysis of Imported Data:")
        
        network_findings = {
            'connected_entities': [
                {'primary': 'Viktor Kozlov', 'connected': 'Illicit Finance Network LLC', 'relationship': 'beneficial_owner'},
                {'primary': 'Ahmed Al-Mansouri', 'connected': 'Global Trade Solutions FZE', 'relationship': 'beneficial_owner'}
            ],
            'geographic_clusters': {
                'UAE_cluster': ['Ahmed Al-Mansouri', 'Global Trade Solutions FZE'],
                'Russia_cluster': ['Viktor Kozlov', 'Illicit Finance Network LLC']
            },
            'risk_patterns': [
                'Shell company structures identified',
                'Cross-border ownership patterns',
                'PEP-entity relationships detected'
            ]
        }
        
        print(f"   Connected Entity Relationships:")
        for connection in network_findings['connected_entities']:
            print(f"   • {connection['primary']} → {connection['connected']} ({connection['relationship']})")
        
        print(f"\n   Geographic Risk Clusters:")
        for cluster_name, entities in network_findings['geographic_clusters'].items():
            print(f"   • {cluster_name}: {len(entities)} entities")
            for entity in entities:
                print(f"     - {entity}")
        
        print(f"\n   Risk Pattern Analysis:")
        for pattern in network_findings['risk_patterns']:
            print(f"   ⚠️  {pattern}")
        
        # Risk rules evaluation on imported data
        print(f"\n⚖️  Risk Rules Analysis:")
        
        # Simulate rule triggers from imported data
        rule_triggers = [
            {'rule': 'High Risk Jurisdiction', 'entities': ['Viktor Kozlov', 'Illicit Finance Network LLC'], 'risk': 'HIGH'},
            {'rule': 'PEP Identification', 'entities': ['Viktor Kozlov'], 'risk': 'CRITICAL'},
            {'rule': 'Shell Company Indicators', 'entities': ['Illicit Finance Network LLC', 'Global Trade Solutions FZE'], 'risk': 'HIGH'},
            {'rule': 'Sanctions Program Match', 'entities': ['All imported entities'], 'risk': 'CRITICAL'}
        ]
        
        for trigger in rule_triggers:
            print(f"   🚨 {trigger['rule']} ({trigger['risk']})")
            if isinstance(trigger['entities'], list) and len(trigger['entities']) <= 2:
                print(f"      Entities: {', '.join(trigger['entities'])}")
            else:
                print(f"      Entities: {trigger['entities']}")
    
    async def demo_ongoing_monitoring(self):
        """Demonstrate ongoing monitoring capabilities"""
        print("\n" + "-"*60)
        print("🔄 Ongoing Monitoring & Alerts")
        print("-"*60)
        
        print("🚨 Automated Monitoring Setup:")
        
        monitoring_config = {
            'adverse_media_monitoring': {
                'frequency': 'daily',
                'entities': ['Viktor Kozlov', 'Ahmed Al-Mansouri'],
                'alert_threshold': 0.6
            },
            'sanctions_list_updates': {
                'frequency': 'real_time',
                'sources': ['OFAC', 'UN', 'EU'],
                'auto_import': True
            },
            'network_analysis': {
                'frequency': 'weekly',
                'relationship_mapping': True,
                'new_connections_alert': True
            },
            'regulatory_changes': {
                'frequency': 'daily',
                'jurisdictions': ['US', 'EU', 'UAE', 'RU'],
                'impact_assessment': True
            }
        }
        
        for monitor_type, config in monitoring_config.items():
            print(f"   ✅ {monitor_type.replace('_', ' ').title()}:")
            print(f"      Frequency: {config['frequency']}")
            if 'entities' in config:
                print(f"      Entities: {len(config['entities'])} being monitored")
            if 'sources' in config:
                print(f"      Sources: {', '.join(config['sources'])}")
        
        # Simulated alert system
        print(f"\n📢 Sample Monitoring Alerts (Last 24 hours):")
        
        sample_alerts = [
            {
                'timestamp': '2024-07-22 09:15:00',
                'type': 'adverse_media',
                'entity': 'Viktor Kozlov',
                'severity': 'HIGH',
                'message': 'New negative media coverage detected'
            },
            {
                'timestamp': '2024-07-22 11:30:00',
                'type': 'sanctions_update',
                'entity': 'OFAC_SDN_LIST',
                'severity': 'MEDIUM',
                'message': '3 new entities added to OFAC SDN list'
            },
            {
                'timestamp': '2024-07-22 14:45:00',
                'type': 'network_change',
                'entity': 'Global Trade Solutions FZE',
                'severity': 'MEDIUM',
                'message': 'New business relationship detected'
            }
        ]
        
        for alert in sample_alerts:
            severity_emoji = "🔴" if alert['severity'] == 'HIGH' else "🟡" if alert['severity'] == 'MEDIUM' else "🟢"
            print(f"   {severity_emoji} [{alert['timestamp']}] {alert['type'].replace('_', ' ').title()}")
            print(f"      Entity: {alert['entity']}")
            print(f"      Alert: {alert['message']}")
        
        # Future enhancements
        print(f"\n🚀 Planned Monitoring Enhancements:")
        
        enhancements = [
            "Machine learning-based risk score evolution",
            "Real-time blockchain transaction monitoring", 
            "Cross-reference with leaked document databases",
            "Automated regulatory filing analysis",
            "Social media sentiment trend analysis",
            "Geopolitical event impact assessment"
        ]
        
        for enhancement in enhancements:
            print(f"   🔮 {enhancement}")
        
        # Cleanup
        try:
            Path(self.temp_csv_file.name).unlink()
            print(f"\n🧹 Cleaned up temporary files")
        except:
            pass

async def main():
    """Main CSV demo function"""
    print("🚀 Starting Phase 2 CSV Import Integration Demo...")
    
    demo = Phase2CSVDemo()
    
    try:
        await demo.run_csv_demo()
        
        print(f"\n💡 CSV Import + Phase 2 Integration Features:")
        print(f"   ✅ Enhanced CSV import with AI analysis")
        print(f"   ✅ Automatic risk assessment of imported entities")
        print(f"   ✅ Auto-creation of investigation cases")
        print(f"   ✅ Network relationship mapping")
        print(f"   ✅ Ongoing monitoring and alerts")
        print(f"   ✅ Post-import intelligence analysis")
        
        print(f"\n🎯 This demonstrates how Phase 2 transforms traditional")
        print(f"   CSV import into an intelligent, automated compliance system.")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
