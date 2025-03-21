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
# Intervue: Edge Condition Evaluation Design

The core of the Intervue application's conversational flow relies on the intelligent evaluation of edge conditions using Google's Gemini LLM. This document explains the design choices behind this system.

## LLM-Based Edge Condition Evaluation

The application uses a sophisticated approach to determine the next step in an interview conversation by analyzing user responses and matching them to predefined conditions:

### Evaluation Process

1. **Context Formation**: The system first formats the entire conversation history to provide full context to the LLM.

2. **Zero-Shot Classification**: Using a prompt template specifically designed for evaluation, the system asks Gemini to classify the user's response according to the edge conditions defined for the current node.

3. **Response Analysis**: The LLM analyzes whether the user's input is:
   - Relevant to the conversation context
   - Aligned with any of the predefined edge conditions

4. **Deterministic Classification**: The evaluation uses Gemini 2.0 Flash with temperature=0.2 to ensure consistent and deterministic classification results.


1. **Irrelevant Response Handling**:
   - When the LLM returns "IRRELEVANT", the system keeps the user on the current node
   - The next response includes a flag to politely redirect the conversation back to the intended topic

2. **Edge Matching**:
   - When the LLM identifies a matching condition, it returns the number of that condition
   - The system navigates to the target node specified by the matching edge

3. **Fallback Mechanism**:
   - If the LLM response can't be parsed as a valid condition number, the system defaults to the first edge
   - If no edges exist, the system remains on the current node

### Advantages of this Approach

1. **Natural Language Understanding**: The system comprehends the intent behind user responses rather than relying on keyword matching.

2. **Contextual Awareness**: By providing the full conversation history, the LLM can make decisions based on the complete interaction context.

3. **Flexible Condition Definitions**: Edge conditions can be defined in natural language rather than rigid patterns or rules.

4. **Graceful Error Handling**: The system identifies and manages irrelevant or nonsensical responses without breaking the conversation flow.

This design creates a more natural and responsive interview experience while maintaining the structured flow necessary for effective interviewing. 
