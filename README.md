# Interview Chatbot

A structured interview chatbot powered by Google's Gemini LLM with a tree-based conversation flow.

## Instructions to Run the Chatbot

1. **Clone the repository**
   ```bash
   git clone https://github.com/ganeshpandey16/intervue
   cd <repository-directory>
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Create a `.env` file in the root directory with:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     SECRET_KEY=your_flask_secret_key
     ```
   - Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **Start the application**
   ```bash
   python app.py
   ```
   - The application will run at `http://localhost:8080`

## Design Choices

### Conversation Flow Architecture

- **Tree-based Structure**: The application uses a JSON-based tree structure to define the interview flow, with each node representing a state in the conversation.
- **Node Components**:
  - `nodeId`: Unique identifier for the node
  - `rootNode`: Boolean flag for the starting node
  - `prompt`: Context and instructions for generating the interviewer's response
  - `edges`: Array of condition-target pairs defining potential paths
  - `disableSendButton`: Optional flag to end the conversation

### LLM Integration and Edge Evaluation

- **Response Generation**:
  - Uses Gemini to generate contextually appropriate responses based on the node prompt and conversation history
  - The system provides the LLM with the conversation context and specific instructions for each node
  - Temperature of 0.5 balances creativity with consistency

- **Edge Condition Evaluation**:
  - LLM analyzes user responses to classify them according to defined edge conditions
  - The evaluation process:
    1. Considers the full conversation history for context
    2. Analyzes the user's latest response against predefined conditions
    3. Classifies the response as matching a specific edge or as irrelevant
    4. Temperature of 0 ensures deterministic classification
  - The system uses a zero-shot classification approach, asking the LLM to output only the condition number

### Error Handling and Edge Cases

- **Irrelevant Response Detection**: The LLM identifies off-topic or nonsensical responses and flags them accordingly
- **Fallback Mechanisms**:
  - If no edge conditions match, defaults to the first edge
  - If a response is irrelevant, stays on the current node and prompts for clarification
  - If no edges exist for a node, conversation ends

### Frontend Design

- **Responsive Interface**: Works across desktop and mobile devices
- **Dynamic Typing Indicators**: Visual feedback when the system is generating a response
- **Conversation Termination**: Clear indication when interview has concluded

### Conversation Data Management

- **Session-based State**: Uses Flask sessions to maintain conversation state
- **History Preservation**: Stores the full conversation history to provide context for the LLM
- **Real-time Updates**: Reloads the conversation tree on each request to ensure using the latest definition

## Features

- Tree-based conversation flow using JSON to define nodes and edges
- Integration with Google's Gemini AI for response generation and condition evaluation
- Elegant web interface with modern styling and interactive elements
- Dynamic typing indicators that show when the AI is generating a response
- Intelligent handling of irrelevant or off-topic responses
- Automatic conversation termination at appropriate endpoints
- Responsive design with a professional navbar featuring the Intervue logo

## Conversation Flow Structure

The conversation flow is defined in the `conversation_flow.json` file using the following structure:

```json
[
    {
        "nodeId": "node1",
        "rootNode": true,
        "prompt": "You are Monika, an AI interviewer for the Frontend Developer role. You're starting an interview with a candidate named Ganesh. Introduce yourself and ask if you're speaking with Ganesh today.",
        "edges": [
            {
                "condition": "user is Ganesh",
                "targetNodeId": "node2"
            },
            {
                "condition": "user is not Ganesh",
                "targetNodeId": "node3"
            }
        ]
    },
    ...
]
```

Each node contains:
- `nodeId`: Unique identifier for the node
- `rootNode`: Boolean indicating if this is the starting node (only one node should have this set to true)
- `prompt`: The text prompt used to generate the chatbot's response
- `edges`: Array of condition-target pairs defining possible paths
- `disableSendButton` (optional): When set to true, ends the conversation at this node

## Extending the Application

You can modify the `conversation_flow.json` file to create your own interview flow with different prompts and conditions. The structure is flexible and allows for complex conversation trees with multiple paths.

To add a new question or topic to the interview:

1. Add a new node with a unique `nodeId`
2. Define a prompt for the interviewer
3. Create edges with conditions for possible user responses
4. Set the `targetNodeId` for each edge to point to the next node in the flow

## Technologies Used

- **Flask**: Web framework for the backend
- **LangChain**: Framework for working with LLMs
- **Google Gemini**: Advanced language model for natural responses
- **HTML/CSS/JavaScript**: Frontend interface and interactions 
