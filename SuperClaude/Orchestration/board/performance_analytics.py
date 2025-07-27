"""
Performance Analytics for Phase 3: Advanced Orchestration
Collects metrics, identifies patterns, and provides optimization insights
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import statistics
import logging

from .card_model import Card, CardStatus, CardType, CardPriority
from .board_manager import BoardManager

logger = logging.getLogger(__name__)


@dataclass
class TaskMetrics:
    """Metrics for a completed task"""
    card_id: str
    agent_id: str
    task_type: CardType
    priority: CardPriority
    duration_seconds: float
    tokens_used: int
    success: bool
    error_count: int
    quality_score: float = 0.8  # Default quality score
    

@dataclass
class AgentPerformance:
    """Performance profile for an agent"""
    agent_id: str
    total_tasks: int = 0
    successful_tasks: int = 0
    total_duration: float = 0.0
    total_tokens: int = 0
    specialties: Dict[str, float] = field(default_factory=dict)  # domain -> proficiency score
    avg_quality: float = 0.8
    last_active: Optional[datetime] = None
    

@dataclass
class WorkflowPattern:
    """Detected workflow pattern"""
    pattern_id: str
    description: str
    frequency: int
    success_rate: float
    avg_duration: float
    avg_tokens: int
    typical_agents: List[str]
    conditions: Dict[str, Any]
    

class PerformanceAnalytics:
    """
    Collects performance metrics, identifies patterns, and provides optimization insights.
    Enables continuous learning and improvement of the orchestration system.
    """
    
    def __init__(self, board_manager: BoardManager, storage_path: Optional[str] = None):
        self.board = board_manager
        self.storage_path = Path(storage_path or "SuperClaude/Orchestration/storage")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Metrics storage
        self.task_metrics: List[TaskMetrics] = []
        self.agent_profiles: Dict[str, AgentPerformance] = {}
        self.workflow_patterns: Dict[str, WorkflowPattern] = {}
        
        # Real-time tracking
        self.active_task_start_times: Dict[str, datetime] = {}
        self.pattern_detection_window = 50  # Analyze last 50 tasks
        
        # Load existing data
        self._load_metrics()
        
    def record_task_start(self, card: Card, agent_id: str):
        """Record when a task starts"""
        self.active_task_start_times[card.id] = datetime.now()
        
        # Update agent last active
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = AgentPerformance(agent_id=agent_id)
        self.agent_profiles[agent_id].last_active = datetime.now()
        
    def record_task_completion(self, card: Card, agent_id: str, success: bool = True):
        """Record task completion with metrics"""
        start_time = self.active_task_start_times.pop(card.id, datetime.now())
        duration = (datetime.now() - start_time).total_seconds()
        
        # Calculate quality score based on errors and warnings
        quality_score = self._calculate_quality_score(card)
        
        # Create task metrics
        metrics = TaskMetrics(
            card_id=card.id,
            agent_id=agent_id,
            task_type=card.card_type,
            priority=card.priority,
            duration_seconds=duration,
            tokens_used=card.metrics.token_usage,
            success=success,
            error_count=card.metrics.error_count,
            quality_score=quality_score
        )
        
        self.task_metrics.append(metrics)
        
        # Update agent profile
        self._update_agent_profile(agent_id, metrics)
        
        # Detect patterns periodically
        if len(self.task_metrics) % 10 == 0:  # Every 10 tasks
            self._detect_patterns()
            
        # Save metrics
        self._save_metrics()
        
    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific agent"""
        if agent_id not in self.agent_profiles:
            return {"error": f"Agent {agent_id} not found"}
            
        profile = self.agent_profiles[agent_id]
        
        # Calculate derived metrics
        success_rate = profile.successful_tasks / profile.total_tasks if profile.total_tasks > 0 else 0
        avg_duration = profile.total_duration / profile.total_tasks if profile.total_tasks > 0 else 0
        avg_tokens = profile.total_tokens / profile.total_tasks if profile.total_tasks > 0 else 0
        
        return {
            "agent_id": agent_id,
            "total_tasks": profile.total_tasks,
            "success_rate": success_rate,
            "avg_duration_minutes": avg_duration / 60,
            "avg_tokens": avg_tokens,
            "avg_quality": profile.avg_quality,
            "specialties": dict(profile.specialties),
            "last_active": profile.last_active.isoformat() if profile.last_active else None
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        if not self.task_metrics:
            return {"message": "No metrics available"}
            
        # Overall statistics
        total_tasks = len(self.task_metrics)
        successful_tasks = sum(1 for m in self.task_metrics if m.success)
        total_duration = sum(m.duration_seconds for m in self.task_metrics)
        total_tokens = sum(m.tokens_used for m in self.task_metrics)
        
        # Recent performance (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_metrics = [m for m in self.task_metrics[-100:]]  # Approximate recent
        
        # Calculate trends
        avg_duration = total_duration / total_tasks if total_tasks > 0 else 0
        avg_tokens = total_tokens / total_tasks if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "avg_duration_minutes": avg_duration / 60,
            "avg_tokens_per_task": avg_tokens,
            "total_agents": len(self.agent_profiles),
            "active_patterns": len(self.workflow_patterns),
            "recent_tasks": len(recent_metrics)
        }
        
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for system optimization"""
        recommendations = []
        
        # Analyze agent performance
        if self.agent_profiles:
            # Find best performing agents per task type
            task_type_performance = defaultdict(list)
            
            for metrics in self.task_metrics[-50:]:  # Last 50 tasks
                if metrics.success:
                    task_type_performance[metrics.task_type].append({
                        "agent": metrics.agent_id,
                        "quality": metrics.quality_score,
                        "efficiency": metrics.tokens_used / max(1, metrics.duration_seconds)
                    })
                    
            # Recommend optimal agent assignments
            for task_type, performances in task_type_performance.items():
                if len(performances) >= 3:  # Need sufficient data
                    best_agents = sorted(performances, 
                                       key=lambda x: x["quality"] * (1 / max(1, x["efficiency"])), 
                                       reverse=True)[:2]
                    
                    recommendations.append({
                        "type": "agent_assignment",
                        "description": f"For {task_type.value} tasks, prefer agents: {[a['agent'] for a in best_agents]}",
                        "confidence": 0.8,
                        "impact": "medium"
                    })
                    
        # Analyze resource usage patterns
        if self.task_metrics:
            token_usage = [m.tokens_used for m in self.task_metrics[-20:]]
            if token_usage:
                avg_tokens = statistics.mean(token_usage)
                if avg_tokens > 8000:  # High token usage
                    recommendations.append({
                        "type": "resource_optimization",
                        "description": "Consider enabling --uc mode for token efficiency",
                        "confidence": 0.9,
                        "impact": "high"
                    })
                    
        # Pattern-based recommendations
        for pattern in self.workflow_patterns.values():
            if pattern.success_rate < 0.7:  # Low success rate pattern
                recommendations.append({
                    "type": "workflow_improvement",
                    "description": f"Pattern '{pattern.description}' has low success rate ({pattern.success_rate:.1%})",
                    "confidence": 0.7,
                    "impact": "medium"
                })
                
        return recommendations
        
    def predict_resource_needs(self, card: Card) -> Dict[str, Any]:
        """Predict resource needs for a new task"""
        # Find similar historical tasks
        similar_tasks = []
        
        for metrics in self.task_metrics:
            similarity_score = 0
            
            # Task type match
            if metrics.task_type == card.card_type:
                similarity_score += 0.4
                
            # Priority match
            if metrics.priority == card.priority:
                similarity_score += 0.2
                
            # Description similarity (simplified)
            if any(word in card.description.lower() 
                  for word in ["api", "ui", "component", "security", "test"]):
                similarity_score += 0.2
                
            if similarity_score >= 0.4:  # Threshold for similarity
                similar_tasks.append(metrics)
                
        if not similar_tasks:
            # Use default estimates
            return {
                "estimated_duration_minutes": 5.0,
                "estimated_tokens": 3000,
                "confidence": 0.3,
                "recommendation": "No similar tasks found, using defaults"
            }
            
        # Calculate predictions based on similar tasks
        durations = [t.duration_seconds / 60 for t in similar_tasks]
        tokens = [t.tokens_used for t in similar_tasks]
        
        return {
            "estimated_duration_minutes": statistics.mean(durations),
            "estimated_tokens": int(statistics.mean(tokens)),
            "confidence": min(0.9, len(similar_tasks) * 0.1),
            "similar_tasks_count": len(similar_tasks),
            "recommendation": f"Based on {len(similar_tasks)} similar tasks"
        }
        
    def _calculate_quality_score(self, card: Card) -> float:
        """Calculate quality score based on card results"""
        base_score = 1.0
        
        # Reduce score for errors
        if card.result.errors:
            base_score -= len(card.result.errors) * 0.1
            
        # Reduce score for warnings
        if card.result.warnings:
            base_score -= len(card.result.warnings) * 0.05
            
        # Bonus for artifacts created
        if card.result.artifacts:
            base_score += len(card.result.artifacts) * 0.05
            
        # Bonus for recommendations provided
        if card.result.recommendations:
            base_score += len(card.result.recommendations) * 0.02
            
        return max(0.0, min(1.0, base_score))
        
    def _update_agent_profile(self, agent_id: str, metrics: TaskMetrics):
        """Update agent performance profile"""
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = AgentPerformance(agent_id=agent_id)
            
        profile = self.agent_profiles[agent_id]
        
        # Update basic stats
        profile.total_tasks += 1
        if metrics.success:
            profile.successful_tasks += 1
        profile.total_duration += metrics.duration_seconds
        profile.total_tokens += metrics.tokens_used
        
        # Update average quality
        profile.avg_quality = (
            (profile.avg_quality * (profile.total_tasks - 1) + metrics.quality_score) / 
            profile.total_tasks
        )
        
        # Update specialties based on task type
        task_type_str = metrics.task_type.value
        if task_type_str not in profile.specialties:
            profile.specialties[task_type_str] = 0.5  # Starting proficiency
            
        # Adjust proficiency based on success and quality
        adjustment = 0.1 if metrics.success else -0.05
        adjustment *= metrics.quality_score
        
        profile.specialties[task_type_str] = max(0.0, min(1.0, 
            profile.specialties[task_type_str] + adjustment))
            
    def _detect_patterns(self):
        """Detect workflow patterns from recent task metrics"""
        if len(self.task_metrics) < 10:
            return
            
        recent_metrics = self.task_metrics[-self.pattern_detection_window:]
        
        # Group by task combinations
        pattern_groups = defaultdict(list)
        
        # Look for patterns in task sequences
        for i in range(len(recent_metrics) - 1):
            current = recent_metrics[i]
            next_task = recent_metrics[i + 1]
            
            # Create pattern key
            pattern_key = f"{current.task_type.value}+{next_task.task_type.value}"
            pattern_groups[pattern_key].append((current, next_task))
            
        # Analyze patterns
        for pattern_key, task_pairs in pattern_groups.items():
            if len(task_pairs) >= 3:  # Need at least 3 occurrences
                # Calculate pattern metrics
                total_success = sum(1 for curr, next_t in task_pairs 
                                  if curr.success and next_t.success)
                success_rate = total_success / len(task_pairs)
                
                avg_duration = statistics.mean(
                    curr.duration_seconds + next_t.duration_seconds 
                    for curr, next_t in task_pairs
                )
                
                avg_tokens = statistics.mean(
                    curr.tokens_used + next_t.tokens_used 
                    for curr, next_t in task_pairs
                )
                
                agents_used = set()
                for curr, next_t in task_pairs:
                    agents_used.add(curr.agent_id)
                    agents_used.add(next_t.agent_id)
                    
                # Create or update pattern
                pattern = WorkflowPattern(
                    pattern_id=pattern_key,
                    description=f"Sequential {pattern_key.replace('+', ' → ')} workflow",
                    frequency=len(task_pairs),
                    success_rate=success_rate,
                    avg_duration=avg_duration,
                    avg_tokens=int(avg_tokens),
                    typical_agents=list(agents_used),
                    conditions={"min_frequency": 3}
                )
                
                self.workflow_patterns[pattern_key] = pattern
                
    def _save_metrics(self):
        """Save metrics to storage"""
        try:
            # Save task metrics
            metrics_file = self.storage_path / "performance_metrics.json"
            metrics_data = {
                "task_metrics": [
                    {
                        "card_id": m.card_id,
                        "agent_id": m.agent_id,
                        "task_type": m.task_type.value,
                        "priority": m.priority.value,
                        "duration_seconds": m.duration_seconds,
                        "tokens_used": m.tokens_used,
                        "success": m.success,
                        "error_count": m.error_count,
                        "quality_score": m.quality_score
                    }
                    for m in self.task_metrics[-1000:]  # Keep last 1000
                ],
                "agent_profiles": {
                    agent_id: {
                        "total_tasks": profile.total_tasks,
                        "successful_tasks": profile.successful_tasks,
                        "total_duration": profile.total_duration,
                        "total_tokens": profile.total_tokens,
                        "specialties": dict(profile.specialties),
                        "avg_quality": profile.avg_quality,
                        "last_active": profile.last_active.isoformat() if profile.last_active else None
                    }
                    for agent_id, profile in self.agent_profiles.items()
                },
                "workflow_patterns": {
                    pattern_id: {
                        "description": pattern.description,
                        "frequency": pattern.frequency,
                        "success_rate": pattern.success_rate,
                        "avg_duration": pattern.avg_duration,
                        "avg_tokens": pattern.avg_tokens,
                        "typical_agents": pattern.typical_agents,
                        "conditions": pattern.conditions
                    }
                    for pattern_id, pattern in self.workflow_patterns.items()
                }
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            
    def _load_metrics(self):
        """Load metrics from storage"""
        try:
            metrics_file = self.storage_path / "performance_metrics.json"
            if not metrics_file.exists():
                return
                
            with open(metrics_file, 'r') as f:
                data = json.load(f)
                
            # Load task metrics
            for item in data.get("task_metrics", []):
                metrics = TaskMetrics(
                    card_id=item["card_id"],
                    agent_id=item["agent_id"],
                    task_type=CardType(item["task_type"]),
                    priority=CardPriority(item["priority"]),
                    duration_seconds=item["duration_seconds"],
                    tokens_used=item["tokens_used"],
                    success=item["success"],
                    error_count=item["error_count"],
                    quality_score=item.get("quality_score", 0.8)
                )
                self.task_metrics.append(metrics)
                
            # Load agent profiles
            for agent_id, profile_data in data.get("agent_profiles", {}).items():
                profile = AgentPerformance(
                    agent_id=agent_id,
                    total_tasks=profile_data["total_tasks"],
                    successful_tasks=profile_data["successful_tasks"],
                    total_duration=profile_data["total_duration"],
                    total_tokens=profile_data["total_tokens"],
                    specialties=profile_data["specialties"],
                    avg_quality=profile_data["avg_quality"]
                )
                if profile_data.get("last_active"):
                    profile.last_active = datetime.fromisoformat(profile_data["last_active"])
                self.agent_profiles[agent_id] = profile
                
            # Load workflow patterns
            for pattern_id, pattern_data in data.get("workflow_patterns", {}).items():
                pattern = WorkflowPattern(
                    pattern_id=pattern_id,
                    description=pattern_data["description"],
                    frequency=pattern_data["frequency"],
                    success_rate=pattern_data["success_rate"],
                    avg_duration=pattern_data["avg_duration"],
                    avg_tokens=pattern_data["avg_tokens"],
                    typical_agents=pattern_data["typical_agents"],
                    conditions=pattern_data["conditions"]
                )
                self.workflow_patterns[pattern_id] = pattern
                
        except Exception as e:
            logger.error(f"Error loading metrics: {e}")