import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load the conversation flow tree from JSON
with open('conversation_flow.json', 'r') as file:
    conversation_tree = json.load(file)

def get_root_node():
    for node in conversation_tree:
        if node.get('rootNode', False):
            return node
    return None

def find_node_by_id(node_id):
    for node in conversation_tree:
        if node['nodeId'] == node_id:
            return node
    return None

def format_conversation_history(history):
    formatted = ""
    for msg in history:
        role = "Interviewer" if msg["role"] == "system" else "User"
        formatted += f"{role}: {msg['content']}\n"
    return formatted

def generate_response(prompt, conversation_history=None):
    system_prompt = """
    You are Monika, an AI interviewer for the Frontend Developer role. 
    Your task is to follow a tree-based conversation flow to conduct an interview.
    Always respond in a professional and friendly manner.
    Keep your responses concise and to the point.
    Do not add any explanations about your role or the process.
    """
    
    full_prompt = system_prompt
    
    if conversation_history:
        full_prompt += "\n\nConversation history:\n" + format_conversation_history(conversation_history)
    
    full_prompt += f"\n\nYour next action based on the current node prompt: {prompt}"
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(full_prompt)
    
    # Clean up the response
    clean_response = response.text.strip()
    if (clean_response.startswith('"') and clean_response.endswith('"')) or \
       (clean_response.startswith("'") and clean_response.endswith("'")):
        clean_response = clean_response[1:-1]
    
    return clean_response

def evaluate_edge_condition(user_input, edges, conversation_history):
    if not edges:
        return None
    
    formatted_history = format_conversation_history(conversation_history)
    
    prompt = f"""
    You are an AI assistant that analyzes interview responses to determine the next step in a conversation flow.
    
    Conversation history:
    {formatted_history}
    
    Based on the user's most recent response: "{user_input}"
    
    Which of the following conditions best matches the user's response? 
    Respond ONLY with the number of the matching condition.
    
    {', '.join([f"{i+1}. {edge['condition']}" for i, edge in enumerate(edges)])}
    
    Output just the number of the matching condition.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    try:
        condition_number = int(response.text.strip())
        if 1 <= condition_number <= len(edges):
            return edges[condition_number - 1]["targetNodeId"]
    except (ValueError, IndexError):
        pass
    
    return edges[0]["targetNodeId"] if edges else None

def test_interview_flow(scenario_name, user_inputs):
    print(f"\n=== Testing Scenario: {scenario_name} ===\n")
    
    # Initialize the conversation history
    conversation_history = []
    
    # Start with the root node
    current_node = get_root_node()
    if not current_node:
        print("Error: Root node not found in conversation tree")
        return
    
    # Generate and display initial prompt
    initial_response = generate_response(current_node['prompt'])
    print(f"AI: {initial_response}")
    
    conversation_history.append({
        "role": "system",
        "content": initial_response
    })
    
    # Process each user input
    for user_input in user_inputs:
        print(f"User: {user_input}")
        
        # Add user input to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Determine next node
        next_node_id = None
        if current_node.get('edges'):
            next_node_id = evaluate_edge_condition(
                user_input,
                current_node['edges'],
                conversation_history
            )
        
        # Move to next node or stay at current node
        current_node = find_node_by_id(next_node_id) if next_node_id else current_node
        
        # Generate and display AI response
        response = generate_response(current_node['prompt'], conversation_history)
        print(f"AI: {response}")
        
        # Add AI response to conversation history
        conversation_history.append({
            "role": "system",
            "content": response
        })
    
    print("\n=== End of Scenario ===\n")

# Test scenarios
if __name__ == "__main__":
    # Scenario 1: User is John and ready for the interview
    test_interview_flow(
        "User is John and ready",
        [
            "Yes, I'm John.",
            "Yes, I'm ready to start the interview."
        ]
    )
    
    # Scenario 2: User is John but not ready for the interview
    test_interview_flow(
        "User is John but not ready",
        [
            "Yes, that's me. I'm John.",
            "Actually, I need to reschedule. I'm not ready right now."
        ]
    )
    
    # Scenario 3: User is not John
    test_interview_flow(
        "User is not John",
        [
            "No, I'm not John. I think you have the wrong person."
        ]
    ) 