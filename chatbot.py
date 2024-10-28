import os
from groq import Groq
from agent import agent_loop

# Create the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"), )

def kevin(chat_history=[]):
    while True:
        # Get user input from the console
        user_input = input(">>K>> ")
        
        if "stuart" in user_input.lower():
            print("BANANA!!!!")
            stuart(chat_history)
            break

        # Append the user input to the chat history
        chat_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(model="llama3-8b-8192",
                                                    messages=chat_history,
                                                    max_tokens=100,
                                                    temperature=1.2)
        
        # Append the response to the chat history
        chat_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })
        # Print the response
        print("Kevin:", response.choices[0].message.content)
        

def stuart(chat_history):
    
    while True:
        stuarts_input = input(">>S>> ")
        
        if 'kevin' in stuarts_input.lower():
            print("BANANA!!!!")
            kevin()
        
        stuarts_result = agent_loop(
            query=stuarts_input,
            verbose=False
        )
        
        print("Stuart:", stuarts_result)
        
        chat_history.append({"role": "user", "content": stuarts_input})
        chat_history.append({"role": "assistant", "content": stuarts_result})


# Initialize the chat history
chat_history = []

user_input = input(">>> ")

if 'stuart' in user_input.lower():
    print("BANANA!!!!")
    stuart(chat_history)
elif 'kevin' in user_input.lower():
    print("BANANA!!!!")
    kevin(chat_history)
else:
    print("BOB!!!")