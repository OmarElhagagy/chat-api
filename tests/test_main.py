import asyncio
import websockets
import requests
import json

API_URL = "http://localhost:80"
WS_URL = "ws://localhost:80/ws"

async def test_api():
    print("=== Testing Scalable Chat API ===")
    
    # Test registration
    print("\n1. Registering users...")
    users = []
    for i in range(1, 4):
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json={
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "password123"
            }
        )
        if response.status_code == 201:
            print(f"  ✓ User{i} registered successfully")
            users.append({"username": f"user{i}", "password": "password123"})
        else:
            print(f"  ✗ Failed to register User{i}: {response.text}")
    
    # Test login
    print("\n2. Testing login...")
    tokens = {}
    for user in users:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            data={
                "username": user["username"],
                "password": user["password"]
            }
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            tokens[user["username"]] = token
            print(f"  ✓ {user['username']} logged in successfully")
        else:
            print(f"  ✗ Failed to login {user['username']}: {response.text}")
    
    # Test room creation
    print("\n3. Creating chat room...")
    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    response = requests.post(
        f"{API_URL}/api/chat/rooms",
        headers=headers,
        json={"name": "Test Room"}
    )
    
    if response.status_code == 201:
        room = response.json()
        room_id = room.get("id")
        print(f"  ✓ Room created: {room['name']} (ID: {room_id})")
    else:
        print(f"  ✗ Failed to create room: {response.text}")
        return
    
    # Test sending messages via REST API
    print("\n4. Sending messages via REST API...")
    for user, token in tokens.items():
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_URL}/api/chat/messages",
            headers=headers,
            json={"room_id": room_id, "content": f"Hello from {user}!"}
        )
        
        if response.status_code == 201:
            print(f"  ✓ Message sent from {user}")
        else:
            print(f"  ✗ Failed to send message from {user}: {response.text}")
    
    # Test reading messages
    print("\n5. Reading messages...")
    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    response = requests.get(
        f"{API_URL}/api/chat/rooms/{room_id}/messages",
        headers=headers
    )
    
    if response.status_code == 200:
        messages = response.json()
        print(f"  ✓ Retrieved {len(messages)} messages")
        for msg in messages:
            print(f"    - {msg['username']}: {msg['content']}")
    else:
        print(f"  ✗ Failed to read messages: {response.text}")
    
    # Test WebSocket connection
    print("\n6. Testing WebSocket connection...")
    try:
        # Connect to WebSocket with user1
        uri = f"{WS_URL}/{room_id}?token={tokens['user1']}"
        async with websockets.connect(uri) as websocket:
            print(f"  ✓ WebSocket connection established for user1")
            
            # Wait for history messages
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            history = json.loads(response)
            print(f"  ✓ Received history with {len(history.get('messages', []))} messages")
            
            # Send message via WebSocket
            await websocket.send(json.dumps({"content": "Message via WebSocket!"}))
            print(f"  ✓ Sent WebSocket message")
            
            # Wait for message confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            message = json.loads(response)
            print(f"  ✓ Message confirmed: {message.get('message', {}).get('content')}")
    
    except Exception as e:
        print(f"  ✗ WebSocket test failed: {e}")
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    asyncio.run(test_api())
