# 📝 AI Exercise Correction

An AI-powered tool that automatically corrects exercises from uploaded images. Simply take a photo of your exercise sheet, and get instant, detailed corrections with explanations.

## ✨ Features

- **📷 Multi-Image Upload**: Upload multiple pages of exercises at once
- **🌍 Multi-Language Support**: Works with any language - automatically detects and responds in the exercise's language
- **🎯 Structured Output**: Clean, organized corrections with questions and answers
- **📄 Export Options**: Download as Markdown (.md) or PDF
- **⚙️ Customizable**: Set output language and add custom preferences

## 🚀 Live Demo

[Try it here](https://your-app.streamlit.app) *(Update with your deployed URL)*

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 3 Flash (via OpenRouter)
- **PDF Generation**: fpdf2
- **API**: OpenRouter with structured JSON outputs

## 📱 Mobile Usage

This app works great on mobile! Add it to your home screen:
- **Android**: Menu → "Add to Home Screen"
- **iPhone**: Share → "Add to Home Screen"

## 🔧 Local Development

### Prerequisites
- Python 3.10+
- OpenRouter API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/exercise-correction-ai.git
cd exercise-correction-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API key:
```
OPENROUTER_KEY=your-api-key-here
```

4. Run the app:
```bash
streamlit run app.py
```

## ☁️ Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add your `OPENROUTER_KEY` in Secrets
5. Deploy!

## 📋 Output Format

The AI returns structured corrections in this format:

```
## Exercise 1

*Given data (if any)*

**1. Question text**

Answer with explanation

**2. Another question**

Another answer

---
```

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai) for AI API access
- [Streamlit](https://streamlit.io) for the web framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) for the AI model
