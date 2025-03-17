import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI API

app = FastAPI(title="AI Feedback Service")

# Define request model
class AnalysisRequest(BaseModel):
    content: str  # This can be a code snippet
    context: str  # Additional context (e.g., "code review")

# Define response model
class AnalysisResponse(BaseModel):
    openai_feedback: str

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    prompt = f"""
You are an expert code reviewer. Based on the following content and context, provide detailed feedback and suggestions.

Content:
{request.content}

Context:
{request.context}

Please provide your feedback in a clear, concise, and actionable manner.
"""
    try:
        # Call the OpenAI API in a separate thread so as not to block the event loop
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert reviewer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.7)
        )
        feedback = response.choices[0].message.content.strip()
        return AnalysisResponse(openai_feedback=feedback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
