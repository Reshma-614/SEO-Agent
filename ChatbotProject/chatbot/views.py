# chatbot/views.py

# from django.http import JsonResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from langchain_together import ChatTogether
# from langchain_community.document_loaders import YoutubeLoader
# from langchain.prompts import PromptTemplate
# import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from langchain_together import ChatTogether
from langchain_community.document_loaders import YoutubeLoader
from langchain.prompts import PromptTemplate
from reportlab.pdfgen import canvas
import json
import io


# Replace with your actual LangChain Together API key
API_KEY = "e3ef1a73ba4014ccff81b38e022569e56c4f43837deb758fdb46ad52896f94a7"  # Make sure to replace this with your API key

# Initialize LangChain with API key and model
llm = ChatTogether(api_key=API_KEY, temperature=0.0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# Create a prompt template
prompt_template = PromptTemplate(
    input_variables=["video_transcript"],
    template="Summarize the following video transcript: {video_transcript}"
)

# Use the RunnableSequence to define the chain
chain = prompt_template | llm  # New RunnableSequence chain

def chatbot_home(request):
    """Render the chatbot interface."""
    return render(request, "chatbot/index.html")


@csrf_exempt
def chatbot_summary(request):
    """Handle API requests for video transcript summaries."""
    if request.method == "POST":
        data = json.loads(request.body)
        video_url = data.get("video_url", "")

        try:
            # Load YouTube video transcript
            loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=False)
            video_data = loader.load()

            # Generate summary
            transcript = video_data[0].page_content
            summary = chain.invoke({"video_transcript": transcript})

            return JsonResponse({"summary": summary.content}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def generate_pdf(request):
    """Generate a PDF of the video summary."""
    if request.method == "POST":
        data = json.loads(request.body)
        summary_text = data.get("summary", "")

        if not summary_text:
            return JsonResponse({"error": "No summary provided"}, status=400)

        try:
            # Create a PDF file in memory
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer)
            pdf.drawString(100, 750, "YouTube Video Summary")
            pdf.drawString(100, 730, "-" * 50)
            pdf.drawString(100, 710, summary_text[:1000])  # Ensure the summary fits on the page
            pdf.save()

            # Rewind buffer and return PDF as response
            buffer.seek(0)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename=summary.pdf"
            return response

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
