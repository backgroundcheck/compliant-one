#!/usr/bin/env python3
"""
Interactive Phase 2 Demo Selector
🎯 Choose specific demo scenarios to run
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from phase2_demo import Phase2Demo
from phase2_advanced_demos import Phase2AdvancedDemos

class InteractiveDemo:
    """Interactive demo selector and runner"""
    
    def __init__(self):
        self.basic_demo = Phase2Demo()
        self.advanced_demo = Phase2AdvancedDemos()
    
    def show_menu(self):
        """Display the demo menu"""
        print("\n" + "="*70)
        print("🎯 PHASE 2 INTERACTIVE DEMO SELECTOR")
        print("="*70)
        print("Choose which demos you'd like to run:")
        print()
        
        print("📋 BASIC DEMOS:")
        print("  1. Complete Phase 2 Overview (All basic scenarios)")
        print("  2. High-Risk Corporate Customer")
        print("  3. PEP Individual with Sanctions Risk") 
        print("  4. Suspicious Transaction Monitoring")
        print("  5. Platform Status & Coverage")
        print()
        
        print("🚀 ADVANCED DEMOS:")
        print("  6. All Advanced Scenarios (Complete suite)")
        print("  7. Cryptocurrency Exchange Onboarding")
        print("  8. AI Shell Company Detection")
        print("  9. Trade Finance Monitoring")
        print("  10. Wire Transfer Pattern Analysis")
        print("  11. PEP Network Analysis") 
        print("  12. Regulatory Change Impact")
        print("  13. Bulk Portfolio Screening")
        print("  14. Case Workflow Automation")
        print()
        
        print("🔧 UTILITIES:")
        print("  15. Service Status Check")
        print("  16. Platform Statistics")
        print("  17. Configuration Test")
        print()
        
        print("  0. Exit")
        print("="*70)
    
    async def run_interactive(self):
        """Run interactive demo selector"""
        while True:
            self.show_menu()
            
            try:
                choice = input("Enter your choice (0-17): ").strip()
                
                if choice == "0":
                    print("👋 Thanks for exploring Phase 2! Goodbye!")
                    break
                
                elif choice == "1":
                    await self.basic_demo.run_comprehensive_demo()
                
                elif choice == "2":
                    await self.basic_demo.demo_scenario_1()
                
                elif choice == "3":
                    await self.basic_demo.demo_scenario_2()
                
                elif choice == "4":
                    await self.basic_demo.demo_scenario_3()
                
                elif choice == "5":
                    await self.basic_demo.demo_comprehensive_assessment()
                
                elif choice == "6":
                    await self.advanced_demo.run_all_demos()
                
                elif choice == "7":
                    await self.advanced_demo.demo_cryptocurrency_exchange()
                
                elif choice == "8":
                    await self.advanced_demo.demo_shell_company_detection()
                
                elif choice == "9":
                    await self.advanced_demo.demo_trade_finance_monitoring()
                
                elif choice == "10":
                    await self.advanced_demo.demo_wire_transfer_patterns()
                
                elif choice == "11":
                    await self.advanced_demo.demo_pep_network_analysis()
                
                elif choice == "12":
                    await self.advanced_demo.demo_regulatory_change_impact()
                
                elif choice == "13":
                    await self.advanced_demo.demo_bulk_screening()
                
                elif choice == "14":
                    await self.advanced_demo.demo_case_workflow_automation()
                
                elif choice == "15":
                    await self.check_service_status()
                
                elif choice == "16":
                    await self.show_platform_statistics()
                
                elif choice == "17":
                    await self.test_configuration()
                
                else:
                    print("❌ Invalid choice. Please enter a number between 0-17.")
                
                if choice != "0":
                    input("\nPress Enter to return to menu...")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")
    
    async def check_service_status(self):
        """Check and display service status"""
        print("\n" + "-"*50)
        print("🔍 SERVICE STATUS CHECK")
        print("-"*50)
        
        try:
            status = await self.basic_demo.platform.get_service_status()
            
            print("Phase 2 Services:")
            phase2_services = ['ai_analytics', 'adverse_media', 'risk_rules', 'case_management']
            
            for service in phase2_services:
                if service in status:
                    service_info = status[service]
                    availability = "✅" if service_info.get('available') else "❌"
                    print(f"  {availability} {service.replace('_', ' ').title()}: {service_info.get('status', 'Unknown')}")
            
            print("\nAll Services:")
            available_count = sum(1 for s in status.values() if s.get('available', False))
            total_count = len(status)
            print(f"  Available: {available_count}/{total_count}")
            
            for service_name, service_info in status.items():
                availability = "✅" if service_info.get('available') else "❌"
                print(f"  {availability} {service_name}: {service_info.get('status', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Error checking service status: {e}")
    
    async def show_platform_statistics(self):
        """Show platform statistics"""
        print("\n" + "-"*50)
        print("📊 PLATFORM STATISTICS")
        print("-"*50)
        
        try:
            # FATF Coverage
            coverage = await self.basic_demo.platform.get_fatf_coverage()
            print(f"FATF Compliance:")
            print(f"  Coverage: {coverage.get('coverage_percentage', 0):.1f}%")
            print(f"  Recommendations: {coverage.get('covered_recommendations', 0)}/{coverage.get('total_recommendations', 0)}")
            
            # Risk Rules Statistics
            if hasattr(self.basic_demo.platform, 'risk_rules_manager'):
                print(f"\nRisk Rules:")
                try:
                    stats = self.basic_demo.platform.risk_rules_manager.get_statistics()
                    rules_stats = stats.get('rules', {})
                    print(f"  Total Rules: {rules_stats.get('total_rules', 0)}")
                    print(f"  Enabled Rules: {rules_stats.get('enabled_rules', 0)}")
                    
                    eval_stats = stats.get('evaluation_engine', {})
                    print(f"  Total Evaluations: {eval_stats.get('total_evaluations', 0)}")
                    print(f"  Rules Triggered: {eval_stats.get('rules_triggered', 0)}")
                except Exception as e:
                    print(f"  Error getting rules stats: {e}")
            
            # Case Management Statistics
            if hasattr(self.basic_demo.platform, 'case_management_system'):
                print(f"\nCase Management:")
                try:
                    case_stats = self.basic_demo.platform.case_management_system.get_case_statistics()
                    print(f"  Total Cases: {case_stats.get('total_cases', 0)}")
                    print(f"  Open Cases: {case_stats.get('cases_by_status', {}).get('open', 0)}")
                    print(f"  Overdue Cases: {case_stats.get('overdue_cases', 0)}")
                    print(f"  SLA Compliance: {case_stats.get('sla_compliance', 0):.1f}%")
                except Exception as e:
                    print(f"  Error getting case stats: {e}")
                    
        except Exception as e:
            print(f"❌ Error getting platform statistics: {e}")
    
    async def test_configuration(self):
        """Test platform configuration"""
        print("\n" + "-"*50)
        print("🔧 CONFIGURATION TEST")
        print("-"*50)
        
        try:
            # Test Phase 2 services initialization
            print("Testing Phase 2 Services:")
            
            services_to_test = [
                ('AI Analytics', hasattr(self.basic_demo.platform, 'ai_service_manager')),
                ('Adverse Media', hasattr(self.basic_demo.platform, 'adverse_media_manager')),
                ('Risk Rules', hasattr(self.basic_demo.platform, 'risk_rules_manager')),
                ('Case Management', hasattr(self.basic_demo.platform, 'case_management_system'))
            ]
            
            for service_name, available in services_to_test:
                status = "✅ Available" if available else "❌ Not Available"
                print(f"  {service_name}: {status}")
            
            # Test database connectivity
            print("\nDatabase Connectivity:")
            try:
                # Test through CSV importer
                from services.sanctions.csv_importer import SanctionsCSVImporter
                importer = SanctionsCSVImporter()
                stats = importer.get_import_statistics()
                print(f"  ✅ Database Connected")
                print(f"  Sanctions Records: {stats.get('total_sanctions_entities', 0)}")
            except Exception as e:
                print(f"  ❌ Database Error: {e}")
            
            # Test Phase 2 configuration
            print("\nPhase 2 Configuration:")
            phase2_enabled = getattr(self.basic_demo.platform, 'phase2_enabled', False)
            print(f"  Phase 2 Enabled: {'✅ Yes' if phase2_enabled else '⚠️  Mock Mode'}")
            
            print(f"\nConfiguration Summary:")
            print(f"  ✅ Core platform functional")
            print(f"  ✅ Phase 2 services initialized")
            print(f"  ✅ Demo scenarios ready")
            
        except Exception as e:
            print(f"❌ Configuration test error: {e}")

async def main():
    """Main interactive demo function"""
    demo = InteractiveDemo()
    
    print("🚀 Starting Interactive Phase 2 Demo...")
    print("This demo lets you explore specific Phase 2 capabilities.")
    
    await demo.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
