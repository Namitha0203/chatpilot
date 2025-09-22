from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import ChatMessage
from .serializers import ChatMessageSerializer

# 🔹 ChatView: handles POST requests to send prompts
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)

        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()

        reply = result["choices"][0]["message"]["content"]

        chat = ChatMessage.objects.create(user=request.user, prompt=prompt, response=reply)
        serializer = ChatMessageSerializer(chat)
        return Response(serializer.data)

# 🔹 ChatHistoryView: handles GET requests to view past messages
class ChatHistoryView(ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user).order_by('-created_at')

# 🔹 ChatPageView: renders the chat input page
@method_decorator(login_required, name='dispatch')
class ChatPageView(APIView):
    def get(self, request):
        return render(request, 'chat/chat.html')

# 🔹 HistoryPageView: renders the chat history page
@method_decorator(login_required, name='dispatch')
class HistoryPageView(APIView):
    def get(self, request):
        messages = ChatMessage.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'chat/history.html', {'messages': messages})

# 🔹 Home view: renders the homepage
def home(request):
    return render(request, 'chat/home.html')
