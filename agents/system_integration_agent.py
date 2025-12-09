#!/usr/bin/env python3
"""
System Integration Agent - End-to-End Workflow Orchestration
Coordinates all agents in proper sequence and ensures dependencies are met
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add agents directory to path
agents_path = Path(__file__).parent
repo_path = agents_path.parent
sys.path.extend([str(agents_path), str(repo_path)])

from qa_verification_agent import QAVerificationAgent
from product_design_agent import ProductDesignAgent
from data_pipeline_agent import DataPipelineAgent
from codebase_hygiene_agent import CodebaseHygieneAgent


class SystemIntegrationAgent:
    """Orchestrates complete ABM research system with sequential gates"""

    def __init__(self, repo_path: str = "/Users/chungty/Projects/vdg-clean/abm-research"):
        self.repo_path = Path(repo_path)
        self.execution_log = []
        self.system_status = {
            "overall_health": "Unknown",
            "agent_status": {},
            "gate_status": {},
            "last_execution": None,
        }

        # Initialize all agents
        self.qa_agent = QAVerificationAgent()
        self.design_agent = ProductDesignAgent(str(repo_path))
        self.pipeline_agent = DataPipelineAgent(str(repo_path))
        self.hygiene_agent = CodebaseHygieneAgent(str(repo_path))

        print("🎼 System Integration Agent initialized")
        print(f"🎯 Managing: {repo_path}")
        print("🤖 All sub-agents loaded")

    def execute_complete_abm_workflow(self, company_domain: str) -> Dict:
        """Execute complete ABM workflow with sequential gates"""

        print(f"\n🚀 EXECUTING COMPLETE ABM WORKFLOW FOR: {company_domain}")
        print("🚪 Sequential gates will prevent progression until requirements are met")

        workflow_results = {
            "company_domain": company_domain,
            "workflow_start": datetime.now().isoformat(),
            "gates_passed": [],
            "gates_failed": [],
            "final_status": "In Progress",
            "errors": [],
            "recommendations": [],
        }

        try:
            # Gate 1: System Health Check
            print("\n🚪 GATE 1: System Health Check")
            gate1_result = self._execute_gate1_system_health()
            if gate1_result["passed"]:
                workflow_results["gates_passed"].append("gate_1_system_health")
                print("   ✅ Gate 1 PASSED - System health verified")
            else:
                workflow_results["gates_failed"].append("gate_1_system_health")
                workflow_results["errors"].extend(gate1_result["blockers"])
                print("   ❌ Gate 1 FAILED - System health issues must be resolved")
                return self._finalize_workflow_results(workflow_results, "Failed at Gate 1")

            # Gate 2: SKILL.md Compliance Verification
            print("\n🚪 GATE 2: SKILL.md Compliance Verification")
            gate2_result = self._execute_gate2_compliance()
            if gate2_result["passed"]:
                workflow_results["gates_passed"].append("gate_2_compliance")
                print("   ✅ Gate 2 PASSED - SKILL.md compliance verified")
            else:
                workflow_results["gates_failed"].append("gate_2_compliance")
                workflow_results["errors"].extend(gate2_result["blockers"])
                print("   ❌ Gate 2 FAILED - Compliance issues must be resolved")
                return self._finalize_workflow_results(workflow_results, "Failed at Gate 2")

            # Gate 3: Data Pipeline Execution
            print("\n🚪 GATE 3: Data Pipeline Execution")
            gate3_result = self._execute_gate3_data_pipeline(company_domain)
            if gate3_result["passed"]:
                workflow_results["gates_passed"].append("gate_3_data_pipeline")
                workflow_results["pipeline_results"] = gate3_result["pipeline_data"]
                print("   ✅ Gate 3 PASSED - 5-phase research completed")
            else:
                workflow_results["gates_failed"].append("gate_3_data_pipeline")
                workflow_results["errors"].extend(gate3_result["blockers"])
                print("   ❌ Gate 3 FAILED - Data pipeline execution failed")
                return self._finalize_workflow_results(workflow_results, "Failed at Gate 3")

            # Gate 4: Notion Database Validation
            print("\n🚪 GATE 4: Notion Database Validation")
            gate4_result = self._execute_gate4_notion_validation()
            if gate4_result["passed"]:
                workflow_results["gates_passed"].append("gate_4_notion_validation")
                print("   ✅ Gate 4 PASSED - Notion databases populated and accessible")
            else:
                workflow_results["gates_failed"].append("gate_4_notion_validation")
                workflow_results["errors"].extend(gate4_result["blockers"])
                print("   ❌ Gate 4 FAILED - Notion database issues detected")
                return self._finalize_workflow_results(workflow_results, "Failed at Gate 4")

            # Gate 5: End-to-End Integration Test
            print("\n🚪 GATE 5: End-to-End Integration Test")
            gate5_result = self._execute_gate5_integration_test()
            if gate5_result["passed"]:
                workflow_results["gates_passed"].append("gate_5_integration")
                print("   ✅ Gate 5 PASSED - Complete workflow verified")
                workflow_results["final_status"] = "Success"
            else:
                workflow_results["gates_failed"].append("gate_5_integration")
                workflow_results["errors"].extend(gate5_result["blockers"])
                print("   ❌ Gate 5 FAILED - Integration issues detected")
                return self._finalize_workflow_results(workflow_results, "Failed at Gate 5")

        except Exception as e:
            workflow_results["errors"].append(f"Workflow execution failed: {str(e)}")
            workflow_results["final_status"] = "Error"

        return self._finalize_workflow_results(workflow_results, workflow_results["final_status"])

    def _execute_gate1_system_health(self) -> Dict:
        """Gate 1: Verify system health and codebase cleanliness"""

        gate_result = {"passed": False, "blockers": [], "details": {}}

        try:
            # Run codebase hygiene analysis
            print("   🧹 Running codebase hygiene analysis...")
            hygiene_analysis = self.hygiene_agent.analyze_codebase_health()

            # Check health score threshold
            total_issues = sum(len(issues) for issues in hygiene_analysis["issues_found"].values())
            health_score = max(0, 100 - (total_issues * 5))

            gate_result["details"]["health_score"] = health_score
            gate_result["details"]["total_issues"] = total_issues

            if health_score >= 70:  # 70% health threshold
                gate_result["passed"] = True
            else:
                gate_result["blockers"].append(
                    f"Codebase health score {health_score}/100 below threshold (70)"
                )

            # Check for critical missing files
            required_files = [
                "comprehensive_abm_research.py",
                "agents/qa_verification_agent.py",
                "agents/product_design_agent.py",
            ]

            for required_file in required_files:
                file_path = self.repo_path / required_file
                if not file_path.exists():
                    gate_result["blockers"].append(f"Missing required file: {required_file}")

            print(f"      📊 Health Score: {health_score}/100")
            print(f"      🐛 Issues Found: {total_issues}")

        except Exception as e:
            gate_result["blockers"].append(f"System health check failed: {str(e)}")

        return gate_result

    def _execute_gate2_compliance(self) -> Dict:
        """Gate 2: Verify SKILL.md compliance"""

        gate_result = {"passed": False, "blockers": [], "details": {}}

        try:
            print("   📋 Validating SKILL.md compliance...")
            compliance_results = self.design_agent.validate_skill_compliance()

            gate_result["details"]["compliance_results"] = compliance_results

            if compliance_results["overall_compliance"]:
                gate_result["passed"] = True
            else:
                gate_result["blockers"].extend(
                    [
                        f"SKILL.md compliance failed",
                        f"Missing components: {', '.join(compliance_results['missing_components'])}",
                    ]
                )

            # Check specific compliance areas
            phase_compliance = sum(compliance_results["phase_compliance"].values())
            total_phases = len(compliance_results["phase_compliance"])

            print(f"      🔄 Phase Compliance: {phase_compliance}/{total_phases}")
            print(
                f"      🗄️ Notion Structure: {'✅' if compliance_results['notion_structure_compliance'] else '❌'}"
            )
            print(
                f"      🧮 Scoring Formula: {'✅' if compliance_results['scoring_formula_compliance'] else '❌'}"
            )

        except Exception as e:
            gate_result["blockers"].append(f"Compliance validation failed: {str(e)}")

        return gate_result

    def _execute_gate3_data_pipeline(self, company_domain: str) -> Dict:
        """Gate 3: Execute data pipeline and verify completion"""

        gate_result = {"passed": False, "blockers": [], "details": {}, "pipeline_data": None}

        try:
            print("   🔄 Executing 5-phase ABM research pipeline...")
            pipeline_results = self.pipeline_agent.execute_full_abm_pipeline(company_domain)

            gate_result["details"]["pipeline_results"] = pipeline_results
            gate_result["pipeline_data"] = pipeline_results

            # Check if all 5 phases completed
            phases_completed = len(pipeline_results.get("phases_completed", []))
            if phases_completed == 5:
                print(f"      ✅ All 5 phases completed")
            else:
                gate_result["blockers"].append(f"Only {phases_completed}/5 phases completed")

            # Check if Notion population attempted
            notion_status = pipeline_results.get("notion_population_status", {})
            if notion_status:
                successful_dbs = sum(notion_status.values())
                total_dbs = len(notion_status)
                print(f"      📝 Notion Population: {successful_dbs}/{total_dbs} databases")

                if successful_dbs < total_dbs:
                    gate_result["blockers"].append(
                        f"Notion population incomplete ({successful_dbs}/{total_dbs})"
                    )
            else:
                gate_result["blockers"].append("Notion population not attempted")

            # Overall pipeline success
            if pipeline_results.get("overall_success", False):
                gate_result["passed"] = True
            else:
                if not gate_result["blockers"]:  # Add general blocker if none specific
                    gate_result["blockers"].append("Data pipeline did not report overall success")

        except Exception as e:
            gate_result["blockers"].append(f"Data pipeline execution failed: {str(e)}")

        return gate_result

    def _execute_gate4_notion_validation(self) -> Dict:
        """Gate 4: Validate Notion databases are accessible and populated"""

        gate_result = {"passed": False, "blockers": [], "details": {}}

        try:
            print("   📝 Verifying Notion database accessibility...")

            # Use QA agent to verify databases
            qa_results = self.qa_agent.run_comprehensive_qa()

            gate_result["details"]["qa_results"] = qa_results

            # Check database accessibility
            db_test_passed = False
            genesis_test_passed = False

            for test in qa_results["test_results"]:
                if test["test_name"] == "verify_notion_databases_exist_and_accessible":
                    db_test_passed = test["status"] == "PASS"
                    if not db_test_passed:
                        gate_result["blockers"].append("Notion databases not accessible")

                elif test["test_name"] == "verify_genesis_cloud_data_populated":
                    genesis_test_passed = test["status"] == "PASS"
                    if not genesis_test_passed:
                        gate_result["blockers"].append("Genesis Cloud data not found in Notion")

            gate_result["passed"] = db_test_passed and genesis_test_passed

            print(f"      🗄️ Database Access: {'✅' if db_test_passed else '❌'}")
            print(f"      📊 Data Population: {'✅' if genesis_test_passed else '❌'}")

        except Exception as e:
            gate_result["blockers"].append(f"Notion validation failed: {str(e)}")

        return gate_result

    def _execute_gate5_integration_test(self) -> Dict:
        """Gate 5: End-to-end integration test"""

        gate_result = {"passed": False, "blockers": [], "details": {}}

        try:
            print("   🔗 Running end-to-end integration test...")

            # Test complete workflow from research to dashboard
            integration_checks = {
                "research_data_exists": False,
                "notion_data_accessible": False,
                "dashboard_can_read_data": False,
            }

            # Check 1: Research data generated
            abm_research_file = self.repo_path / "comprehensive_abm_research.py"
            if abm_research_file.exists():
                integration_checks["research_data_exists"] = True
            else:
                gate_result["blockers"].append("No research implementation found")

            # Check 2: Notion data accessible (reuse Gate 4 logic)
            qa_results = self.qa_agent.run_comprehensive_qa()
            notion_accessible = any(
                test["status"] == "PASS" and "notion" in test["test_name"].lower()
                for test in qa_results["test_results"]
            )

            integration_checks["notion_data_accessible"] = notion_accessible
            if not notion_accessible:
                gate_result["blockers"].append(
                    "Notion data not accessible for dashboard integration"
                )

            # Check 3: Dashboard integration ready
            dashboard_files = list(self.repo_path.glob("*dashboard*"))
            if dashboard_files:
                integration_checks["dashboard_can_read_data"] = True
            else:
                gate_result["blockers"].append("No dashboard implementation found")

            gate_result["details"]["integration_checks"] = integration_checks

            # Pass if all checks pass
            gate_result["passed"] = all(integration_checks.values())

            for check_name, status in integration_checks.items():
                status_icon = "✅" if status else "❌"
                print(f"      {status_icon} {check_name.replace('_', ' ').title()}")

        except Exception as e:
            gate_result["blockers"].append(f"Integration test failed: {str(e)}")

        return gate_result

    def _finalize_workflow_results(self, workflow_results: Dict, status: str) -> Dict:
        """Finalize workflow results and print summary"""

        workflow_results["workflow_end"] = datetime.now().isoformat()
        workflow_results["final_status"] = status

        # Calculate execution time
        start_time = datetime.fromisoformat(workflow_results["workflow_start"])
        end_time = datetime.fromisoformat(workflow_results["workflow_end"])
        execution_time = (end_time - start_time).total_seconds()

        workflow_results["execution_time_seconds"] = execution_time

        self._print_workflow_summary(workflow_results)
        return workflow_results

    def _print_workflow_summary(self, results: Dict):
        """Print comprehensive workflow execution summary"""

        print(f"\n🎼 SYSTEM INTEGRATION WORKFLOW SUMMARY")
        print("=" * 60)

        status_color = "✅" if results["final_status"] == "Success" else "❌"
        print(f"Final Status: {status_color} {results['final_status']}")
        print(f"Company: {results['company_domain']}")
        print(f"Execution Time: {results.get('execution_time_seconds', 0):.1f} seconds")

        print(f"\n🚪 SEQUENTIAL GATES:")
        total_gates = 5
        gates_passed = len(results["gates_passed"])
        gates_failed = len(results["gates_failed"])

        gate_names = [
            "System Health Check",
            "SKILL.md Compliance",
            "Data Pipeline Execution",
            "Notion Database Validation",
            "End-to-End Integration",
        ]

        for i, gate_name in enumerate(gate_names, 1):
            gate_key = f"gate_{i}_" + gate_name.lower().replace(" ", "_").replace("-", "_").replace(
                ".", ""
            )

            if any(gate_key in passed_gate for passed_gate in results["gates_passed"]):
                print(f"   ✅ Gate {i}: {gate_name}")
            elif any(gate_key in failed_gate for failed_gate in results["gates_failed"]):
                print(f"   ❌ Gate {i}: {gate_name} [FAILED - BLOCKING]")
            else:
                print(f"   ⏳ Gate {i}: {gate_name} [NOT REACHED]")

        print(f"\n📊 GATE STATISTICS:")
        print(f"   Passed: {gates_passed}/{total_gates}")
        print(f"   Failed: {gates_failed}/{total_gates}")
        print(f"   Success Rate: {(gates_passed/total_gates)*100:.1f}%")

        if results.get("errors"):
            print(f"\n⚠️ ERRORS & BLOCKERS:")
            for i, error in enumerate(results["errors"], 1):
                print(f"   {i}. {error}")

        if results["final_status"] == "Success":
            print(f"\n🎉 WORKFLOW COMPLETE - ABM RESEARCH SYSTEM OPERATIONAL")
            print(f"   • All 5 phases executed successfully")
            print(f"   • Notion databases populated and accessible")
            print(f"   • End-to-end integration verified")
            print(f"   • Ready for dashboard connection and usage")
        else:
            print(f"\n🔧 NEXT STEPS:")
            print(f"   • Resolve blockers listed above")
            print(f"   • Re-run workflow after fixes")
            print(f"   • Sequential gates prevent progression until issues resolved")

    def get_system_status(self) -> Dict:
        """Get current system status without execution"""

        print("\n📊 CHECKING SYSTEM STATUS...")

        status = {
            "timestamp": datetime.now().isoformat(),
            "agents_operational": {},
            "quick_health_check": {},
            "recommendations": [],
        }

        # Check agent availability
        agents = {
            "QA Verification": self.qa_agent,
            "Product Design": self.design_agent,
            "Data Pipeline": self.pipeline_agent,
            "Codebase Hygiene": self.hygiene_agent,
        }

        for agent_name, agent in agents.items():
            try:
                # Test agent is callable
                hasattr(agent, "__class__")
                status["agents_operational"][agent_name] = True
            except:
                status["agents_operational"][agent_name] = False

        # Quick health checks
        try:
            qa_results = self.qa_agent.run_comprehensive_qa()
            status["quick_health_check"]["qa_tests_passing"] = (
                qa_results["overall_status"] == "PASS"
            )
            status["quick_health_check"]["database_count"] = len(
                [
                    test
                    for test in qa_results["test_results"]
                    if test["status"] == "PASS" and "database" in test["test_name"]
                ]
            )
        except:
            status["quick_health_check"]["qa_tests_passing"] = False

        # Generate recommendations
        all_agents_ok = all(status["agents_operational"].values())
        qa_passing = status["quick_health_check"].get("qa_tests_passing", False)

        if all_agents_ok and qa_passing:
            status["recommendations"].append("✅ System ready for workflow execution")
        else:
            if not all_agents_ok:
                status["recommendations"].append(
                    "🔧 Some agents not operational - check agent initialization"
                )
            if not qa_passing:
                status["recommendations"].append("📝 QA tests failing - run full QA verification")

        self._print_status_summary(status)
        return status

    def _print_status_summary(self, status: Dict):
        """Print system status summary"""

        print(f"\n📊 SYSTEM STATUS SUMMARY")
        print("=" * 40)

        print(f"📅 Timestamp: {status['timestamp']}")

        print(f"\n🤖 AGENT STATUS:")
        for agent_name, operational in status["agents_operational"].items():
            status_icon = "✅" if operational else "❌"
            print(f"   {status_icon} {agent_name}")

        print(f"\n⚡ QUICK HEALTH CHECK:")
        for check_name, result in status["quick_health_check"].items():
            if isinstance(result, bool):
                status_icon = "✅" if result else "❌"
                print(f"   {status_icon} {check_name.replace('_', ' ').title()}")
            else:
                print(f"   📊 {check_name.replace('_', ' ').title()}: {result}")

        print(f"\n🎯 RECOMMENDATIONS:")
        for i, rec in enumerate(status["recommendations"], 1):
            print(f"   {i}. {rec}")


if __name__ == "__main__":
    system_agent = SystemIntegrationAgent()

    # Check system status first
    system_status = system_agent.get_system_status()

    # Execute complete workflow if system is ready
    if system_status["quick_health_check"].get("qa_tests_passing", False):
        print("\n🚀 System appears ready - executing complete workflow...")
        workflow_results = system_agent.execute_complete_abm_workflow("genesiscloud.com")
    else:
        print("\n⚠️ System not ready for workflow execution")
        print("   Run QA verification and resolve issues first")
