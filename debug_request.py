import httpx
import asyncio

async def test_create_complaint():
    url = "http://localhost:3000/api/complaints"
    
    # Mock data matching frontend
    data = {
        "text": "Huge garbage pile near the main junction causing smell",
        "latitude": "17.444",
        "longitude": "78.444",
        "address": "Test Address"
    }
    
    # Send as multipart/form-data
    try:
        async with httpx.AsyncClient() as client:
            print(f"Sending POST to {url}...")
            response = await client.post(url, data=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_create_complaint())
