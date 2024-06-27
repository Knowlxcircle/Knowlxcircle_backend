from django.shortcuts import render
import google.generativeai as genai
import pathlib
import textwrap
from IPython.display import display
from IPython.display import Markdown
from knowlxcirclebackend.settings import GOOGLE_API_KEY


genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.0-pro")


