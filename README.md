# Search InCorporate 🔍🏢

**Search InCorporate** is an AI-powered company intelligence application that instantly researches any business, extracts key insights, identifies pain points, and analyzes competitors—all presented in a beautiful, ChatGPT-like interface.

## 🌟 Features

* **Deep Company Research**: Simply enter a company name or website URL. The AI will autonomously crawl the web, search knowledge graphs, and extract structured data about the business.
* **Competitor Analysis**: Automatically identifies direct competitors, complete with their descriptions and website links.
* **Pain Points & Insights**: Leverages Large Language Models (LLMs) to infer the company's biggest challenges and market pain points based on real-time search data.
* **Live Console & Timeline**: Watch the AI work in real-time with a live terminal console and a 5-stage progress timeline (Searching, Crawling, Extracting, AI Analysis, PDF Generation).
* **PDF Report Generation**: Download the complete research findings as a cleanly formatted PDF document.
* **Discord Integration**: Configure a Discord Webhook to automatically broadcast your research findings directly to your team's Discord channel.
* **Persistent History**: Navigate seamlessly between past searches via the sleek sidebar. Background searches continue running even when you click away!

## 🛠️ Technology Stack

### Backend (Python/FastAPI)
* **FastAPI**: High-performance async API backend.
* **BeautifulSoup & Selenium**: Intelligent web scraping pipeline with automatic fallback for JavaScript-heavy or protected sites.
* **Serper.dev**: Google Search and Knowledge Graph API integration.
* **OpenRouter & Cohere**: LLM orchestration for massive context windows, information extraction, and JSON structuring.
* **ReportLab**: Dynamic PDF generation.

### Frontend (React/TypeScript)
* **React + Vite**: Lightning-fast modern frontend setup.
* **TailwindCSS**: Beautiful, responsive, and sleek dark-mode UI.
* **Framer Motion**: Smooth micro-animations, loading states, and transitions.
* **Lucide React**: Clean vector iconography.

## 🚀 Getting Started

### Prerequisites
You will need API keys for the following services to run the backend:
* `OPENROUTER_API_KEY` or `COHERE_API_KEY` (for AI extraction)
* `SERPER_API_KEY` (for Google search queries)

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment and install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file in the backend root and add your API keys.
5. Run the FastAPI server: `python -m app.main`
   * The backend will start on `http://localhost:8000`.

### Frontend Setup
1. Navigate to the `frontend/reluUI` directory.
2. Install dependencies: `npm install`
3. Start the Vite development server: `npm run dev`
4. Open the application in your browser.

## 💡 Usage
1. Open the app and type a company name (e.g., "Tesla" or "stripe.com").
2. Hit **Enter** to begin the autonomous research pipeline.
3. Watch the live console to see what the AI is fetching.
4. When finished, review the structured data, download the PDF, or send it to Discord!

---
*Made with ☕ by [Tarandeep Singh](https://tarandeep-singh.vercel.app/)*
