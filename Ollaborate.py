import ollama
import sys
import time
import linecache

# Initialize agent configurations
agent_a_config = {"model": "llama2", "system": "You are Agent A, and you are a curious and speculative questioner "}
agent_b_config = {"model": "llama2", "system": "You are Agent B, and you are an analytical thinker"}

# Initial conversation setup
conversation = [
    {"speaker": "Agent A", "message": "Hello, Agent B! Why is it hard to compute the environmental impact of AI?"},
]
"""
    This function will be called whenever a new line of code is about to be executed.
    It captures the current timestamp, the filename, line number, and the actual code line.
"""

def trace_lines(frame, event, arg):
    """
    This function will be called whenever a new line of code is about to be executed.
    It captures the current timestamp, the filename, line number, and the actual code line.
    """
    if event == 'line':
        # Get human-readable timestamp
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Get line info
        lineno = frame.f_lineno
        filename = frame.f_code.co_filename
        
        # Grab the actual line of code
        code_line = linecache.getline(filename, lineno).rstrip()

        # Print or log the information
        print(f"{current_time} - {filename}:{lineno} => {code_line}")

    return trace_lines


# Function to generate a response using the Ollama library
def generate_response(agent_config, prompt):
    try:
        response = ollama.generate(model=agent_config["model"], system=agent_config["system"], prompt=prompt)

        # Access the 'response' attribute for the generated text
        if hasattr(response, "response"):
            return response.response.strip()
        else:
            print("Debug: Unexpected response structure:", response)
            return "I'm unable to respond at the moment."
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm unable to respond at the moment."


def main():
    # Multi-agent conversation logic
    for _ in range(5):  # Limit to 5 conversation turns for demonstration
        last_message = conversation[-1]
        current_agent_config = agent_b_config if last_message["speaker"] == "Agent A" else agent_a_config
        current_agent_name = "Agent B" if last_message["speaker"] == "Agent A" else "Agent A"

        # Generate the response
        response_text = generate_response(current_agent_config, last_message["message"])

        # Append the response to the conversation
        conversation.append({"speaker": current_agent_name, "message": response_text})
        print(f"{current_agent_name}: {response_text}")

    # Output the entire conversation
    print("\nComplete Conversation:")
    for turn in conversation:
        print(f"{turn['speaker']}: {turn['message']}")


if __name__ == "__main__":
    # Enable tracing
    sys.settrace(trace_lines)
    #sys.settrace(None)
    main()

    # Disable tracing if desired (to avoid tracing cleanup/shutdown code)
    sys.settrace(None)
