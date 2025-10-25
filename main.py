from google import genai

# The client will automatically pick up the API key from an environment variable.
client = genai.Client()

# Use the 'gemini-2.5-flash' model for powerful, free access
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a short poem about an AI chatbot."
)

print(response.text)