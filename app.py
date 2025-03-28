from flask import Flask, request, jsonify, render_template, session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
import os
import json
from dotenv import load_dotenv

# Initialize environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Load the conversation flow tree from JSON
conversation_tree = []

def load_conversation_tree():
    """Load conversation flow structure from JSON file"""
    global conversation_tree
    with open('conversation_flow.json', 'r') as file:
        conversation_tree = json.load(file)
    
    return conversation_tree

# Initial load
load_conversation_tree()

def get_root_node():
    """Find and return the root node of the conversation tree"""
    for node in conversation_tree:
        if node.get('rootNode', False):
            return node
    return None

def find_node_by_id(node_id):
    """Locate and return a specific node by its ID"""
    for node in conversation_tree:
        if node['nodeId'] == node_id:
            return node
    return None

def format_conversation_history(history):
    """Convert conversation history to a readable string format"""
    formatted = ""
    for msg in history:
        role = "Interviewer" if msg["role"] == "system" else "User"
        formatted += f"{role}: {msg['content']}\n"
    return formatted

def evaluate_edge_condition(user_input, edges, conversation_history):
    """Analyze user response to determine the next conversation path using Gemini"""
    if not edges:
        return None
    
    # Format conversation history for context
    formatted_history = format_conversation_history(conversation_history)
    
    # Create a template for the LLM to classify the user's response
    template = """
    You are an AI assistant that analyzes interview responses to determine the next step in a conversation flow.

    Conversation history:
    {conversation_history}
    
    Based on the user's most recent response: "{user_input}"
    
    First, determine if the response is relevant to the conversation context and if it meaningfully addresses the previous question.
    If the response is irrelevant, nonsensical, or random text (like "ndkndigubibrjarfm") or something which is not a proper answer to the question, respond with "IRRELEVANT".
    
    If the response is relevant, determine which of the following conditions BEST reflects the user's response in the context of a structured interview.
    Focus *solely* on whether the response aligns with the *intent* of the conditions provided.
    
    {conditions}
    
    Output ONLY "IRRELEVANT" or the number of the matching condition.
    """
    
    prompt_template = PromptTemplate(
        input_variables=["conversation_history", "user_input", "conditions"],
        template=template
    )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    conditions = ', '.join([f"{i+1}. {edge['condition']}" for i, edge in enumerate(edges)])
    
    response = chain.invoke({
        "conversation_history": formatted_history,
        "user_input": user_input,
        "conditions": conditions
    })
    
    llm_response = response["text"].strip()
    
    # Check if the response is irrelevant
    if llm_response == "IRRELEVANT":
        return "IRRELEVANT"
    
    try:
        # Extract the condition number from the response
        condition_number = int(llm_response)
        if 1 <= condition_number <= len(edges):
            return edges[condition_number - 1]["targetNodeId"]
    except (ValueError, IndexError):
        # If the response couldn't be parsed as an integer or is out of range
        pass
    
    # Default to the first edge if evaluation fails
    return edges[0]["targetNodeId"] if edges else None

def generate_response(node, conversation_history=None, is_irrelevant_response=False):
    """Generate interview response using Gemini based on conversation node and history"""
    system_template = """
    You are Monika, an AI interviewer for the Frontend Developer role. 
    Your primary goal is to conduct a structured interview following a predefined flow.

    {conversation_history}

    Current prompt: {prompt}

    **Guidelines:**
    * Respond to the candidate in a professional, friendly, and conversational manner
    * Craft a natural-sounding response that fulfills the prompt's requirements
    * If the candidate's response is irrelevant, nonsensical, or clearly outside the scope of the current question, politely acknowledge their input but gently guide the conversation back to the intended topic
    * Adapt your tone and level of detail based on the candidate's previous responses
    * Keep your responses concise and focused on the task at hand
    * Do NOT break character or mention that you're an AI following instructions
    * Do NOT use quotation marks around words like "meet" or "hello" or any other words
    * Be direct and concise in your responses

    {irrelevant_flag}

    Your response:
    """
    irrelevant_flag = ""
    if is_irrelevant_response:
        irrelevant_flag = """
    The user's previous response was irrelevant or nonsensical.
    IMPORTANT: You MUST politely acknowledge this and then repeat the original question from your prompt.
    Say something like: "I'm sorry, but I need a clear response to proceed with the interview. Let me rephrase my question: [ask the question again based on your prompt without giving the introduction again]"
    """
    
    prompt_template = PromptTemplate(
        input_variables=["conversation_history", "prompt", "irrelevant_flag"],
        template=system_template
    )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    history = ""
    if conversation_history:
        history = "Conversation history:\n" + format_conversation_history(conversation_history)
    
    prompt = node.get('prompt', '')
    
    response = chain.invoke({
        "conversation_history": history,
        "prompt": prompt,
        "irrelevant_flag": irrelevant_flag
    })
    
    # Improved cleaning of response
    clean_response = response["text"].strip()
    # Remove any quotation marks if the response is enclosed in them
    if (clean_response.startswith('"') and clean_response.endswith('"')) or \
       (clean_response.startswith("'") and clean_response.endswith("'")):
        clean_response = clean_response[1:-1]
    
    return clean_response

@app.route('/')
def index():
    """Initialize interview session and render landing page"""
    # Reset the conversation
    session.clear()
    
    # Force reload the conversation tree to ensure we have the latest version
    global conversation_tree
    with open('conversation_flow.json', 'r') as file:
        conversation_tree = json.load(file)
    
    # Get the root node
    root_node = get_root_node()
    if not root_node:
        return "Conversation flow not configured properly", 500
    
    # Store the current node ID in the session
    session['current_node_id'] = root_node['nodeId']
    session['conversation_history'] = []
    
    # Generate the initial prompt
    initial_response = generate_response(root_node)
    session['conversation_history'].append({
        "role": "system",
        "content": initial_response
    })
    
    response = render_template('index.html', initial_message=initial_response)
    # Add cache control headers
    return response, 200, {'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Expires': '0'}

@app.route('/chat', methods=['POST'])
def chat():
    """Process user messages and generate appropriate interview responses"""
    # Force reload the conversation tree to ensure we have the latest version
    global conversation_tree
    with open('conversation_flow.json', 'r') as file:
        conversation_tree = json.load(file)
    
    user_input = request.json.get('message', '')
    
    # Get conversation history from session
    conversation_history = session.get('conversation_history', [])
    
    # Store user message in conversation history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Get current node
    current_node_id = session.get('current_node_id')
    current_node = find_node_by_id(current_node_id)
    
    if not current_node:
        return jsonify({"error": "Invalid conversation state"}), 400
    
    # Determine the next node based on user input
    next_node_id = None
    is_irrelevant_response = False
    
    if current_node.get('edges'):
        next_node_id = evaluate_edge_condition(
            user_input, 
            current_node['edges'], 
            conversation_history
        )
        
        # Handle irrelevant responses
        if next_node_id == "IRRELEVANT":
            is_irrelevant_response = True
            next_node_id = None  # Stay on current node
    
    # If no matching edge, irrelevant response, or no edges defined, stay on the current node
    next_node = find_node_by_id(next_node_id) if next_node_id else current_node
    
    # Generate response based on the next node's prompt
    response = generate_response(next_node, conversation_history, is_irrelevant_response)
    
    # Update the session
    session['current_node_id'] = next_node['nodeId']
    conversation_history.append({
        "role": "system",
        "content": response
    })
    session['conversation_history'] = conversation_history
    
    # Check if the send button should be disabled
    disable_send_button = next_node.get('disableSendButton', False)
    
    return jsonify({
        "message": response,
        "disableSendButton": disable_send_button
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 