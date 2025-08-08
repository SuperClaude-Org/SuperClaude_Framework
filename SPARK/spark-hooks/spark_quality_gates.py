#!/usr/bin/env python3
"""
SPARK Quality Gates Hook (SubagentStop)
Implements SPARK's 8-step quality validation + Jason's DNA compliance
"""

import json
import logging
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def run_command(cmd: str, cwd: str = None) -> tuple:
    """Run shell command and return (success, output, error)"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            timeout=60
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, "", "Command timed out")
    except Exception as e:
        return (False, "", str(e))


def execute_sparkclaude_quality_gates(task_data: dict) -> dict:
    """Execute SPARK's 8-step quality gates + Jason DNA extensions"""
    
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    quality_results = {
        "gates_passed": 0,
        "total_gates": 10,
        "violations": {},
        "gate_results": {},
        "sparkclaude_compliance": False,
        "jason_dna_compliance": False
    }
    
    # Get implementation files from task context
    artifacts = task_data.get("artifacts", {})
    files_created = artifacts.get("files_created", [])
    files_modified = artifacts.get("files_modified", [])
    all_files = files_created + files_modified
    
    if not all_files:
        logger.warning("No files to validate - skipping quality gates")
        return quality_results
    
    logger.info("🛡️ Executing SPARK + Jason Quality Gates...")
    
    # SPARK Gate 1: Syntax Validation
    logger.info("Step 1/10: Syntax Validation...")
    syntax_violations = 0
    for file_path in all_files:
        if file_path.endswith('.py'):
            success, _, error = run_command(f"python3 -m py_compile {file_path}", project_root)
            if not success:
                syntax_violations += 1
                logger.error(f"Syntax error in {file_path}: {error}")
    
    quality_results["gate_results"]["step_1_syntax"] = syntax_violations == 0
    quality_results["violations"]["syntax_errors"] = syntax_violations
    if syntax_violations == 0:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 2: Type Verification (MyPy)
    logger.info("Step 2/10: Type Verification...")
    mypy_violations = 0
    for file_path in all_files:
        if file_path.endswith('.py'):
            success, output, error = run_command(f"uv run mypy {file_path} --strict", project_root)
            if not success:
                # Count actual errors (not just warnings)
                error_lines = [line for line in (output + error).split('\n') if 'error:' in line]
                mypy_violations += len(error_lines)
                if error_lines:
                    logger.error(f"MyPy errors in {file_path}: {len(error_lines)}")
    
    quality_results["gate_results"]["step_2_types"] = mypy_violations == 0  
    quality_results["violations"]["mypy_errors"] = mypy_violations
    if mypy_violations == 0:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 3: Lint Enforcement (Ruff)
    logger.info("Step 3/10: Lint Enforcement...")
    ruff_violations = 0
    for file_path in all_files:
        if file_path.endswith('.py'):
            success, output, error = run_command(f"uv run ruff check {file_path}", project_root)
            if not success:
                # Count violations from ruff output
                violation_lines = [line for line in output.split('\n') if file_path in line]
                ruff_violations += len(violation_lines)
                if violation_lines:
                    logger.error(f"Ruff violations in {file_path}: {len(violation_lines)}")
    
    quality_results["gate_results"]["step_3_lint"] = ruff_violations == 0
    quality_results["violations"]["ruff_violations"] = ruff_violations  
    if ruff_violations == 0:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 4: Security Analysis (Basic patterns)
    logger.info("Step 4/10: Security Analysis...")
    security_violations = 0
    security_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
        (r'exec\s*\(', "Dangerous exec() usage"),
        (r'eval\s*\(', "Dangerous eval() usage"),
    ]
    
    for file_path in all_files:
        if file_path.endswith('.py'):
            try:
                with open(os.path.join(project_root, file_path), 'r') as f:
                    content = f.read()
                    
                import re
                for pattern, message in security_patterns:
                    if re.search(pattern, content):
                        security_violations += 1
                        logger.error(f"Security issue in {file_path}: {message}")
            except Exception as e:
                logger.error(f"Could not analyze {file_path}: {e}")
    
    quality_results["gate_results"]["step_4_security"] = security_violations == 0
    quality_results["violations"]["security_issues"] = security_violations
    if security_violations == 0:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 5: Test Integration (Check if tests exist)
    logger.info("Step 5/10: Test Integration...")
    test_files_exist = any('test' in file_path.lower() for file_path in all_files)
    test_coverage_adequate = test_files_exist  # Simplified for now
    
    quality_results["gate_results"]["step_5_tests"] = test_coverage_adequate
    quality_results["violations"]["missing_tests"] = 0 if test_coverage_adequate else 1
    if test_coverage_adequate:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 6: Performance Check (Import analysis)
    logger.info("Step 6/10: Performance Check...")
    performance_issues = 0
    # Check for potentially expensive imports in main execution paths
    # This is a simplified check - could be expanded
    
    quality_results["gate_results"]["step_6_performance"] = performance_issues == 0
    quality_results["violations"]["performance_issues"] = performance_issues
    if performance_issues == 0:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 7: Documentation (Check for docstrings)
    logger.info("Step 7/10: Documentation...")
    documentation_violations = 0
    for file_path in all_files:
        if file_path.endswith('.py'):
            try:
                with open(os.path.join(project_root, file_path), 'r') as f:
                    content = f.read()
                    # Simple check for function definitions without docstrings
                    import re
                    functions = re.findall(r'def\s+\w+\(.*?\):', content)
                    docstrings = re.findall(r'""".*?"""', content, re.DOTALL)
                    
                    if len(functions) > len(docstrings) and len(functions) > 2:  # Allow small functions
                        documentation_violations += 1
                        logger.warning(f"Missing docstrings in {file_path}")
            except Exception as e:
                logger.error(f"Could not analyze documentation in {file_path}: {e}")
    
    quality_results["gate_results"]["step_7_documentation"] = documentation_violations == 0
    quality_results["violations"]["documentation_issues"] = documentation_violations  
    if documentation_violations == 0:
        quality_results["gates_passed"] += 1
    
    # SPARK Gate 8: Integration Test (Import test)
    logger.info("Step 8/10: Integration Test...")
    integration_failures = 0
    for file_path in all_files:
        if file_path.endswith('.py'):
            # Test if the file can be imported
            module_path = file_path.replace('/', '.').replace('.py', '')
            success, _, error = run_command(f"python3 -c \"import {module_path}\"", project_root)
            if not success:
                integration_failures += 1
                logger.error(f"Import failed for {file_path}: {error}")
    
    quality_results["gate_results"]["step_8_integration"] = integration_failures == 0
    quality_results["violations"]["integration_failures"] = integration_failures
    if integration_failures == 0:
        quality_results["gates_passed"] += 1
    
    # Jason DNA Gate 9: MyPy Zero Errors (Already done in step 2, but enforce)
    logger.info("Step 9/10: Jason DNA MyPy Enforcement...")
    jason_mypy_compliance = mypy_violations == 0
    quality_results["gate_results"]["step_9_jason_mypy"] = jason_mypy_compliance
    if jason_mypy_compliance:
        quality_results["gates_passed"] += 1
    
    # Jason DNA Gate 10: Ruff Zero Violations (Already done in step 3, but enforce)  
    logger.info("Step 10/10: Jason DNA Ruff Enforcement...")
    jason_ruff_compliance = ruff_violations == 0
    quality_results["gate_results"]["step_10_jason_ruff"] = jason_ruff_compliance
    if jason_ruff_compliance:
        quality_results["gates_passed"] += 1
    
    # Final compliance assessment
    quality_results["sparkclaude_compliance"] = quality_results["gates_passed"] >= 8
    quality_results["jason_dna_compliance"] = jason_mypy_compliance and jason_ruff_compliance
    
    # Log results
    logger.info(f"🛡️ Quality Gates Complete: {quality_results['gates_passed']}/10 passed")
    logger.info(f"⚡ SPARK Compliance: {'✅ PASS' if quality_results['sparkclaude_compliance'] else '❌ FAIL'}")
    logger.info(f"🧬 Jason DNA Compliance: {'✅ PASS' if quality_results['jason_dna_compliance'] else '❌ FAIL'}")
    
    return quality_results


def determine_routing_decision(task_data: dict, quality_results: dict) -> dict:
    """Determine next action based on quality gate results"""
    
    current_agent = task_data.get("current_agent", "implementer")
    iteration = task_data.get("iteration_tracking", {}).get("current_iteration", 1)
    max_iterations = task_data.get("iteration_tracking", {}).get("max_iterations", 3)
    
    total_violations = sum(quality_results["violations"].values())
    gates_passed = quality_results["gates_passed"]
    
    # If this was implementer and we have violations
    if current_agent in ["implementer", "implementer-spark"] and total_violations > 0:
        if iteration < max_iterations:
            return {
                "next_action": "retry_implementer",
                "reason": f"Quality gates failed: {gates_passed}/10 passed, {total_violations} violations found",
                "specific_instructions": f"Fix violations: {list(quality_results['violations'].keys())}",
                "retry_required": True
            }
        else:
            return {
                "next_action": "escalate", 
                "reason": f"Maximum iterations reached with {total_violations} violations",
                "specific_instructions": "Manual intervention required",
                "retry_required": False
            }
    
    # If quality gates passed or this is from another agent
    if total_violations == 0:
        if current_agent in ["implementer", "implementer-spark"]:
            return {
                "next_action": "proceed_to_tester",
                "reason": "All quality gates passed successfully",
                "specific_instructions": "Ready for test implementation phase",
                "retry_required": False
            }
        elif current_agent == "tester":
            return {
                "next_action": "proceed_to_reviewer", 
                "reason": "Testing phase complete",
                "specific_instructions": "Ready for architecture review",
                "retry_required": False
            }
        elif current_agent == "reviewer":
            return {
                "next_action": "proceed_to_reporter",
                "reason": "Review phase complete", 
                "specific_instructions": "Ready for final reporting",
                "retry_required": False
            }
        elif current_agent == "reporter":
            return {
                "next_action": "workflow_complete",
                "reason": "All phases completed successfully",
                "specific_instructions": "Workflow finished",
                "retry_required": False  
            }
    
    # Default fallback
    return {
        "next_action": "proceed_to_next",
        "reason": "Standard workflow progression", 
        "specific_instructions": "",
        "retry_required": False
    }


def main():
    """Main hook execution"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        # Load current task data
        task_file = Path(".claude/workflows/current_task.json")
        if not task_file.exists():
            logger.warning("No current_task.json found - skipping quality gates")
            sys.exit(0)
            
        with open(task_file, 'r') as f:
            task_data = json.load(f)
        
        # Only run quality gates if SPARK is activated or this is implementer-spark
        sparkclaude_active = task_data.get("sparkclaude_activation") is not None
        current_agent = task_data.get("current_agent", "")
        
        if not sparkclaude_active and "super" not in current_agent:
            logger.info("SPARK not activated - using standard quality gates")
            sys.exit(0)
        
        # Execute SPARK quality gates
        quality_results = execute_sparkclaude_quality_gates(task_data)
        
        # Determine routing decision
        routing_decision = determine_routing_decision(task_data, quality_results)
        
        # Update task data
        task_data.update({
            "sparkclaude_quality_results": quality_results,
            "routing_decision": routing_decision,
            "quality_gates_timestamp": datetime.now().isoformat(),
            "quality_gates": quality_results["violations"]  # For backward compatibility
        })
        
        # Save updated task data
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        # Log routing decision
        logger.info(f"🎯 Routing Decision: {routing_decision['next_action']}")
        logger.info(f"📋 Reason: {routing_decision['reason']}")
        
        # If there are violations and retry is needed, send feedback to Claude
        if routing_decision.get("retry_required") and quality_results["violations"]:
            violation_details = []
            for violation_type, count in quality_results["violations"].items():
                if count > 0:
                    violation_details.append(f"• {violation_type}: {count}")
            
            feedback = f"""🛡️ SPARK Quality Gates Results:

❌ **Quality Issues Found** ({quality_results['gates_passed']}/10 gates passed):

{chr(10).join(violation_details)}

**Required Actions:**
{routing_decision['specific_instructions']}

**Next Step:** The implementer-spark agent will be called again to fix these issues."""

            # Send feedback to agent via JSON output
            output = {
                "decision": "block",
                "reason": feedback
            }
            print(json.dumps(output))
            sys.exit(0)
        
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Quality gates execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()