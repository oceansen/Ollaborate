import asyncio
import ray
from typing import Optional
from ollama import Ollama  # Hypothetical Python client for Ollama

########################################
# Ollama LLM Call Utility
########################################
class OllamaClient:
    def __init__(self):
        self.client = Ollama()

    async def generate_response(self, model: str, prompt: str) -> str:
        # Hypothetical async usage. If only sync is available, wrap with asyncio.to_thread.
        # If Ollama supports streaming, you may need to accumulate outputs.
        response = await self.client.generate(model=model, prompt=prompt)
        return response.strip()


########################################
# DEVS Atomic Model (LLMAgent)
########################################
@ray.remote
class LLMAgent:
    def __init__(self, name: str, model: str, initial_context: str, ollama_client: OllamaClient):
        self.name = name
        self.model = model
        self.context = initial_context  # State: conversation so far
        self.last_input = None
        self.goal_reached = False
        self.ollama_client = ollama_client

    async def external_transition(self, message: str):
        """
        Process an external event: a message from the other agent.
        Update internal state accordingly.
        """
        self.last_input = message
        # Append message to the context
        self.context += f"\n{message}"

    async def internal_transition(self) -> str:
        """
        Internal transition: generate a response (the output event).
        """
        if self.goal_reached:
            return ""

        prompt = f"{self.context}\n{self.name}:"
        response = await self.ollama_client.generate_response(self.model, prompt)
        self.context += f"\n{self.name}: {response}"

        # Check if the goal is reached. For demonstration: if response contains "AGREED_PLAN:"
        if "AGREED_PLAN:" in response.upper():
            self.goal_reached = True

        return response

    async def is_goal_reached(self) -> bool:
        return self.goal_reached


########################################
# DEVS Coupled Model / Simulator (Coordinator)
########################################
class ConversationSimulator:
    def __init__(self, agent_a, agent_b, max_steps=10):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.current_turn = 'A'
        self.max_steps = max_steps
        self.step_count = 0

    async def run(self):
        """
        Run a simplified discrete-event simulation of the conversation.
        """
        # Start the conversation
        starting_message = "System: You are two experts who need to come up with an agreed-upon plan. Please cooperate."
        await self.agent_a.external_transition.remote(starting_message)

        while self.step_count < self.max_steps:
            self.step_count += 1

            if self.current_turn == 'A':
                # Agent A responds
                response = await self.agent_a.internal_transition.remote()
                if response:
                    await self.agent_b.external_transition.remote(f"AgentA: {response}")

                # Check goals
                goal_a = await self.agent_a.is_goal_reached.remote()
                goal_b = await self.agent_b.is_goal_reached.remote()
                if ray.get(goal_a) or ray.get(goal_b):
                    print("Goal reached after Agent A's turn.")
                    break

                self.current_turn = 'B'

            else:
                # Agent B responds
                response = await self.agent_b.internal_transition.remote()
                if response:
                    await self.agent_a.external_transition.remote(f"AgentB: {response}")

                # Check goals
                goal_a = await self.agent_a.is_goal_reached.remote()
                goal_b = await self.agent_b.is_goal_reached.remote()
                if ray.get(goal_a) or ray.get(goal_b):
                    print("Goal reached after Agent B's turn.")
                    break

                self.current_turn = 'A'

        print("Simulation ended.")


########################################
# Main Execution
########################################
if __name__ == "__main__":
    ray.init(ignore_reinit_error=True)

    ollama_client = OllamaClient()

    # Replace 'my-model-name' with a real Ollama model name, e.g. "llama2"
    agent_a = LLMAgent.remote(name="AgentA", model="my-model-name", initial_context="Role:AgentA", ollama_client=ollama_client)
    agent_b = LLMAgent.remote(name="AgentB", model="my-model-name", initial_context="Role:AgentB", ollama_client=ollama_client)

    simulator = ConversationSimulator(agent_a, agent_b, max_steps=10)

    # Run the simulation
    asyncio.run(simulator.run())

    ray.shutdown()

