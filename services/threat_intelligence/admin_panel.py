"""
Threat Intelligence Admin Panel
Web-based administration interface for threat intelligence configuration
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.threat_intelligence.threat_intel_service import ThreatIntelligenceService
from utils.logger import get_logger

class ThreatIntelAdminPanel:
    """
    Administrative interface for threat intelligence service management
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.threat_service = ThreatIntelligenceService()
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            stats = self.threat_service.get_statistics()
            health = self.threat_service.health_check()
            alerts = self.threat_service.get_alerts(limit=10)
            
            # Get recent activity
            import sqlite3
            conn = sqlite3.connect(self.threat_service.db_path)
            cursor = conn.cursor()
            
            # Recent indicators
            cursor.execute('''
                SELECT indicator_type, COUNT(*) as count
                FROM threat_indicators 
                WHERE last_updated >= datetime('now', '-7 days')
                GROUP BY indicator_type
                ORDER BY count DESC
            ''')
            recent_indicators = dict(cursor.fetchall())
            
            # Active sources
            cursor.execute('''
                SELECT source, COUNT(*) as count
                FROM threat_indicators 
                WHERE is_active = 1
                GROUP BY source
                ORDER BY count DESC
                LIMIT 10
            ''')
            active_sources = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'statistics': stats,
                'health': health,
                'recent_alerts': alerts,
                'recent_indicators': recent_indicators,
                'active_sources': active_sources,
                'dashboard_generated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard data: {e}")
            return {'error': str(e)}
    
    def manage_sources(self, action: str, source_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage threat intelligence sources"""
        try:
            if action == 'list':
                return {
                    'success': True,
                    'sources': self.threat_service.sources,
                    'enabled_sources': self.threat_service.config['enabled_sources']
                }
            
            elif action == 'enable' and source_config:
                source_name = source_config.get('source_name')
                if source_name in self.threat_service.config['enabled_sources']:
                    self.threat_service.config['enabled_sources'][source_name] = True
                    
                    # Update in database
                    result = self.threat_service.update_configuration({
                        'enabled_sources': self.threat_service.config['enabled_sources']
                    })
                    
                    return {
                        'success': True,
                        'message': f'Enabled source: {source_name}',
                        'update_result': result
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Unknown source: {source_name}'
                    }
            
            elif action == 'disable' and source_config:
                source_name = source_config.get('source_name')
                if source_name in self.threat_service.config['enabled_sources']:
                    self.threat_service.config['enabled_sources'][source_name] = False
                    
                    # Update in database
                    result = self.threat_service.update_configuration({
                        'enabled_sources': self.threat_service.config['enabled_sources']
                    })
                    
                    return {
                        'success': True,
                        'message': f'Disabled source: {source_name}',
                        'update_result': result
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Unknown source: {source_name}'
                    }
            
            elif action == 'test' and source_config:
                source_name = source_config.get('source_name')
                # Implement source connectivity test
                return self._test_source_connectivity(source_name)
            
            else:
                return {
                    'success': False,
                    'error': 'Invalid action or missing configuration'
                }
                
        except Exception as e:
            self.logger.error(f"Error managing sources: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _test_source_connectivity(self, source_name: str) -> Dict[str, Any]:
        """Test connectivity to a threat intelligence source"""
        try:
            import aiohttp
            import asyncio
            
            # Get source URLs
            test_urls = []
            if source_name == 'abuse_ch':
                test_urls = ['https://feodotracker.abuse.ch/downloads/ipblocklist.csv']
            elif source_name == 'cybercrime_tracker':
                test_urls = ['https://cybercrime-tracker.net/ccamlist.php']
            elif source_name == 'haveibeenpwned':
                test_urls = ['https://haveibeenpwned.com/api/v3/breaches']
            
            if not test_urls:
                return {
                    'success': False,
                    'error': f'No test URLs configured for {source_name}'
                }
            
            async def test_url(url):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            return {
                                'url': url,
                                'status': response.status,
                                'accessible': response.status < 400,
                                'response_time': 'quick'  # Simplified for demo
                            }
                except Exception as e:
                    return {
                        'url': url,
                        'status': 0,
                        'accessible': False,
                        'error': str(e)
                    }
            
            # Run tests
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            test_results = []
            for url in test_urls:
                result = loop.run_until_complete(test_url(url))
                test_results.append(result)
            
            loop.close()
            
            # Summary
            accessible_count = sum(1 for r in test_results if r.get('accessible', False))
            
            return {
                'success': True,
                'source_name': source_name,
                'test_results': test_results,
                'summary': {
                    'total_tested': len(test_results),
                    'accessible': accessible_count,
                    'success_rate': (accessible_count / len(test_results)) * 100 if test_results else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Source connectivity test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def manage_monitoring_targets(self, action: str, target_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage monitoring targets"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.threat_service.db_path)
            cursor = conn.cursor()
            
            if action == 'list':
                cursor.execute('''
                    SELECT id, target_type, target_value, description, priority, 
                           is_active, created_at, last_checked
                    FROM monitoring_targets 
                    ORDER BY priority DESC, created_at DESC
                ''')
                
                columns = [description[0] for description in cursor.description]
                targets = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                conn.close()
                
                return {
                    'success': True,
                    'targets': targets,
                    'total_count': len(targets)
                }
            
            elif action == 'add' and target_data:
                result = self.threat_service.add_monitoring_target(
                    target_type=target_data['target_type'],
                    target_value=target_data['target_value'],
                    description=target_data.get('description'),
                    priority=target_data.get('priority', 5)
                )
                
                conn.close()
                return result
            
            elif action == 'remove' and target_data:
                target_id = target_data.get('target_id')
                cursor.execute('DELETE FROM monitoring_targets WHERE id = ?', (target_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return {
                        'success': True,
                        'message': f'Removed monitoring target {target_id}'
                    }
                else:
                    conn.close()
                    return {
                        'success': False,
                        'error': 'Target not found'
                    }
            
            elif action == 'toggle' and target_data:
                target_id = target_data.get('target_id')
                cursor.execute('''
                    UPDATE monitoring_targets 
                    SET is_active = NOT is_active 
                    WHERE id = ?
                ''', (target_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return {
                        'success': True,
                        'message': f'Toggled monitoring target {target_id}'
                    }
                else:
                    conn.close()
                    return {
                        'success': False,
                        'error': 'Target not found'
                    }
            
            else:
                conn.close()
                return {
                    'success': False,
                    'error': 'Invalid action or missing data'
                }
                
        except Exception as e:
            self.logger.error(f"Error managing monitoring targets: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def manage_alerts(self, action: str, alert_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage threat alerts"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.threat_service.db_path)
            cursor = conn.cursor()
            
            if action == 'list':
                status_filter = alert_data.get('status') if alert_data else None
                severity_filter = alert_data.get('severity') if alert_data else None
                limit = alert_data.get('limit', 50) if alert_data else 50
                
                query = "SELECT * FROM threat_alerts WHERE 1=1"
                params = []
                
                if status_filter:
                    query += " AND status = ?"
                    params.append(status_filter)
                
                if severity_filter:
                    query += " AND severity = ?"
                    params.append(severity_filter)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                conn.close()
                
                return {
                    'success': True,
                    'alerts': alerts,
                    'total_count': len(alerts),
                    'filters': {
                        'status': status_filter,
                        'severity': severity_filter,
                        'limit': limit
                    }
                }
            
            elif action == 'resolve' and alert_data:
                alert_id = alert_data.get('alert_id')
                resolution_note = alert_data.get('resolution_note', '')
                
                cursor.execute('''
                    UPDATE threat_alerts 
                    SET status = 'resolved', resolved_at = ?
                    WHERE id = ?
                ''', (datetime.now(), alert_id))
                
                if resolution_note:
                    cursor.execute('''
                        UPDATE threat_alerts 
                        SET description = description || ? || ?
                        WHERE id = ?
                    ''', ('\n\nResolution: ', resolution_note, alert_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    conn.close()
                    return {
                        'success': True,
                        'message': f'Resolved alert {alert_id}'
                    }
                else:
                    conn.close()
                    return {
                        'success': False,
                        'error': 'Alert not found'
                    }
            
            elif action == 'bulk_resolve' and alert_data:
                alert_ids = alert_data.get('alert_ids', [])
                resolution_note = alert_data.get('resolution_note', 'Bulk resolved')
                
                if not alert_ids:
                    conn.close()
                    return {
                        'success': False,
                        'error': 'No alert IDs provided'
                    }
                
                placeholders = ','.join('?' * len(alert_ids))
                cursor.execute(f'''
                    UPDATE threat_alerts 
                    SET status = 'resolved', resolved_at = ?
                    WHERE id IN ({placeholders})
                ''', [datetime.now()] + alert_ids)
                
                resolved_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                return {
                    'success': True,
                    'message': f'Resolved {resolved_count} alerts',
                    'resolved_count': resolved_count
                }
            
            else:
                conn.close()
                return {
                    'success': False,
                    'error': 'Invalid action or missing data'
                }
                
        except Exception as e:
            self.logger.error(f"Error managing alerts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def run_collection_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run threat intelligence collection task"""
        try:
            task_type = task_config.get('task_type', 'full')
            
            results = {
                'task_type': task_type,
                'started_at': datetime.now().isoformat(),
                'results': {}
            }
            
            if task_type in ['full', 'breaches']:
                self.logger.info("Starting breach data collection...")
                breach_result = await self.threat_service.collect_breach_data()
                results['results']['breach_collection'] = breach_result
            
            if task_type in ['full', 'feeds']:
                self.logger.info("Starting threat feed collection...")
                feed_result = await self.threat_service.collect_threat_feeds()
                results['results']['feed_collection'] = feed_result
            
            if task_type in ['full', 'monitoring']:
                self.logger.info("Running monitoring checks...")
                # Get active targets
                import sqlite3
                conn = sqlite3.connect(self.threat_service.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT target_type, target_value FROM monitoring_targets WHERE is_active = 1")
                targets = [{'type': row[0], 'value': row[1]} for row in cursor.fetchall()]
                conn.close()
                
                if targets:
                    monitoring_result = await self.threat_service.monitor_targets(targets)
                    results['results']['monitoring'] = monitoring_result
                else:
                    results['results']['monitoring'] = {
                        'success': True,
                        'message': 'No monitoring targets configured'
                    }
            
            results['completed_at'] = datetime.now().isoformat()
            results['success'] = True
            
            return results
            
        except Exception as e:
            self.logger.error(f"Collection task failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            }
    
    def export_data(self, export_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export threat intelligence data"""
        try:
            import sqlite3
            import csv
            import json
            from io import StringIO
            
            conn = sqlite3.connect(self.threat_service.db_path)
            cursor = conn.cursor()
            
            export_data = []
            
            if export_type == 'indicators':
                query = "SELECT * FROM threat_indicators WHERE is_active = 1"
                if filters:
                    if filters.get('threat_type'):
                        query += f" AND threat_type = '{filters['threat_type']}'"
                    if filters.get('min_confidence'):
                        query += f" AND confidence >= {filters['min_confidence']}"
                
                cursor.execute(query)
                columns = [description[0] for description in cursor.description]
                export_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            elif export_type == 'alerts':
                query = "SELECT * FROM threat_alerts"
                if filters and filters.get('status'):
                    query += f" WHERE status = '{filters['status']}'"
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query)
                columns = [description[0] for description in cursor.description]
                export_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            elif export_type == 'targets':
                cursor.execute("SELECT * FROM monitoring_targets ORDER BY priority DESC")
                columns = [description[0] for description in cursor.description]
                export_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"threat_intel_{export_type}_{timestamp}"
            
            # Export as JSON by default
            export_content = json.dumps(export_data, indent=2, default=str)
            
            return {
                'success': True,
                'export_type': export_type,
                'filename': f"{filename}.json",
                'content': export_content,
                'record_count': len(export_data),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Data export failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and configuration"""
        try:
            health = self.threat_service.health_check()
            stats = self.threat_service.get_statistics()
            
            # Get database info
            import sqlite3
            conn = sqlite3.connect(self.threat_service.db_path)
            cursor = conn.cursor()
            
            # Database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            
            # Table counts
            tables = ['threat_indicators', 'breach_data', 'monitoring_targets', 'threat_alerts']
            table_counts = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_counts[table] = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'health': health,
                'statistics': stats,
                'database': {
                    'path': str(self.threat_service.db_path),
                    'size_bytes': db_size,
                    'size_mb': round(db_size / 1024 / 1024, 2),
                    'table_counts': table_counts
                },
                'configuration': {
                    'enabled_sources': self.threat_service.config['enabled_sources'],
                    'rate_limit_delay': self.threat_service.config['rate_limit_delay'],
                    'max_concurrent_requests': self.threat_service.config['max_concurrent_requests']
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {
                'error': str(e)
            }

def main():
    """Main function for command line admin interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Threat Intelligence Admin Panel")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard")
    parser.add_argument("--sources", choices=['list', 'test'], help="Manage sources")
    parser.add_argument("--targets", choices=['list', 'add'], help="Manage targets")
    parser.add_argument("--alerts", choices=['list', 'resolve'], help="Manage alerts")
    parser.add_argument("--collect", choices=['full', 'breaches', 'feeds', 'monitoring'], help="Run collection")
    parser.add_argument("--export", choices=['indicators', 'alerts', 'targets'], help="Export data")
    parser.add_argument("--system-info", action="store_true", help="Show system information")
    
    args = parser.parse_args()
    
    admin = ThreatIntelAdminPanel()
    
    if args.dashboard:
        dashboard = admin.get_dashboard_data()
        print("📊 Threat Intelligence Dashboard")
        print("=" * 50)
        
        if 'error' in dashboard:
            print(f"❌ Error: {dashboard['error']}")
            return
        
        stats = dashboard['statistics']
        print(f"🎯 Active Indicators: {stats['indicators']['total_active']}")
        print(f"💥 Total Breaches: {stats['breaches']['total']}")
        print(f"🚨 New Alerts: {stats['alerts']['new']}")
        print(f"👁️  Active Targets: {stats['monitoring']['active_targets']}")
        
        print("\n📈 Recent Activity:")
        for indicator_type, count in dashboard['recent_indicators'].items():
            print(f"  {indicator_type}: {count}")
    
    elif args.sources:
        if args.sources == 'list':
            result = admin.manage_sources('list')
            print("📡 Threat Intelligence Sources:")
            print("-" * 40)
            
            enabled = result['enabled_sources']
            for category, urls in result['sources'].items():
                print(f"\n{category.upper()}:")
                for url in urls:
                    status = "✅" if enabled.get(category, False) else "❌"
                    print(f"  {status} {url}")
        
        elif args.sources == 'test':
            print("🧪 Testing source connectivity...")
            # Test a few key sources
            for source in ['abuse_ch', 'cybercrime_tracker']:
                result = admin.manage_sources('test', {'source_name': source})
                if result['success']:
                    summary = result['summary']
                    print(f"  {source}: {summary['accessible']}/{summary['total_tested']} accessible ({summary['success_rate']:.1f}%)")
                else:
                    print(f"  {source}: ❌ {result['error']}")
    
    elif args.targets:
        if args.targets == 'list':
            result = admin.manage_monitoring_targets('list')
            print(f"👁️  Monitoring Targets ({result['total_count']}):")
            print("-" * 50)
            
            for target in result['targets'][:10]:  # Show first 10
                status = "🟢" if target['is_active'] else "🔴"
                print(f"  {status} {target['target_type']}: {target['target_value']} (Priority: {target['priority']})")
    
    elif args.alerts:
        if args.alerts == 'list':
            result = admin.manage_alerts('list', {'limit': 15})
            print(f"🚨 Recent Alerts ({len(result['alerts'])}):")
            print("-" * 60)
            
            for alert in result['alerts']:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert['severity'], "⚪")
                status_icon = {"new": "🆕", "resolved": "✅"}.get(alert['status'], "❓")
                print(f"  {severity_icon}{status_icon} {alert['title']}")
                print(f"    Created: {alert['created_at']}")
    
    elif args.collect:
        print(f"🔄 Starting {args.collect} collection...")
        
        async def run_collection():
            result = await admin.run_collection_task({'task_type': args.collect})
            
            if result['success']:
                print("✅ Collection completed successfully!")
                for task_name, task_result in result['results'].items():
                    if task_result.get('success'):
                        print(f"  {task_name}: ✅")
                    else:
                        print(f"  {task_name}: ❌ {task_result.get('error', 'Unknown error')}")
            else:
                print(f"❌ Collection failed: {result['error']}")
        
        import asyncio
        asyncio.run(run_collection())
    
    elif args.export:
        print(f"📤 Exporting {args.export} data...")
        result = admin.export_data(args.export)
        
        if result['success']:
            # Save to file
            with open(result['filename'], 'w') as f:
                f.write(result['content'])
            
            print(f"✅ Exported {result['record_count']} records to {result['filename']}")
        else:
            print(f"❌ Export failed: {result['error']}")
    
    elif args.system_info:
        info = admin.get_system_info()
        
        if 'error' in info:
            print(f"❌ Error: {info['error']}")
            return
        
        print("🖥️  System Information")
        print("=" * 40)
        
        print(f"📊 Database Size: {info['database']['size_mb']} MB")
        print(f"📍 Database Path: {info['database']['path']}")
        
        print("\n📋 Table Counts:")
        for table, count in info['database']['table_counts'].items():
            print(f"  {table}: {count:,}")
        
        print("\n⚙️  Configuration:")
        for source, enabled in info['configuration']['enabled_sources'].items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {source}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
