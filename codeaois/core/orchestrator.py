from agents.coder_agent import CoderAgent
from agents.tester_agent import TesterAgent
from agents.git_agent import GitAgent

class AgentOrchestrator:
    def __init__(self):
        # Registering the full AI team
        self.agents = {
            "coder": CoderAgent(),
            "tester": TesterAgent(),
            "git": GitAgent()
        }

    def run(self, tasks):
        results = []
        for task in tasks:
            agent_name = task.get("agent")
            agent = self.agents.get(agent_name)
            
            # If the agent exists, execute its task
            if agent:
                results.append(agent.execute(task.get("task")))
        return results