import requests
import time
import subprocess
import sys

def run_server():
    return subprocess.Popen([sys.executable, "main.py"])

def test_chat_endpoints():
    base_url = "http://localhost:6000"
    
    # Test Kevin
    response = requests.post(f"{base_url}/chat", json={"message": "Hello Kevin", "agent": "kevin"})
    print(f"Kevin's response: {response.json()}")
    assert response.status_code == 200
    
    # Test Stuart
    response = requests.post(f"{base_url}/chat", json={"message": "Hello Stuart", "agent": "stuart"})
    print(f"Stuart's response: {response.json()}")
    assert response.status_code == 200
    
    # Test Bob
    response = requests.post(f"{base_url}/chat", json={"message": "Hello Bob", "agent": "bob"})
    print(f"Bob's response: {response.json()}")
    assert response.status_code == 200
    
    # Test chat history
    response = requests.get(f"{base_url}/chat_history")
    print(f"Chat history: {response.json()}")
    assert response.status_code == 200
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    server_process = run_server()
    try:
        # Wait for the server to start
        time.sleep(2)
        test_chat_endpoints()
    finally:
        server_process.terminate()