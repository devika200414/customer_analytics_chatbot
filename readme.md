# Customer Analytics Chatbot

A PDF-based Q&A chatbot that answers questions using content from an uploaded report — powered by Google's Gemini API, Sentence Transformers, and FAISS for retrieval.

## What it does

Upload a PDF (e.g. a customer analytics report), and the chatbot:

1. Extracts and chunks the text from the PDF
2. Converts chunks into embeddings using Sentence Transformers
3. Stores embeddings in a FAISS vector index for fast similarity search
4. Retrieves the most relevant chunks for a user's question
5. Sends the question + relevant context to Gemini to generate an accurate, grounded answer

### Example

```text
You: total customers
Bot: Based on the report, the total number of customers is 4338.
```

## Tech Stack

- **Python**
- **Google Gemini API** (`google-genai`) — LLM for answer generation
- **Sentence Transformers** — Text embeddings
- **FAISS** — Vector similarity search
- **python-dotenv** — Environment variable management
- **NumPy / Pandas** — Data handling

## Project Structure

```text
customer_analytics_chatbot/
├── app.py                # Main entry point / chat loop
├── chatbot.py            # Core chatbot logic (retrieval + generation)
├── analytics.py          # Data analytics helper functions
├── charts.py             # Chart generation
├── create_pdf.py         # PDF report creation utility
├── insights.py           # Insight generation from data
├── faiss_store/          # Saved FAISS vector index
├── chunks.pkl            # Cached text chunks from the PDF
├── source.hash           # Hash to detect if source PDF has changed
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not committed)
```

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd customer_analytics_chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key_here
```

### 5. Run the application

```bash
python app.py
```

## Usage

- On the first run, the application processes the source PDF, creates text chunks, and builds a FAISS vector index.
- The generated index is cached using `chunks.pkl` and `faiss_store/`.
- On subsequent runs, if the source PDF has not changed (verified using `source.hash`), the cached index is reused for faster startup.
- Ask questions about the uploaded report in the terminal.
- Type `exit` to close the chatbot.

## Notes

- Never commit your `.env` file or API key to GitHub.
- If the source PDF changes, delete `chunks.pkl` and `faiss_store/` or allow `source.hash` to trigger automatic index regeneration.

## Future Improvements

- Add a Gradio or Streamlit web interface
- Support multiple PDF documents
- Add conversation history and multi-turn context
- Improve chunking and retrieval accuracy
- Deploy the chatbot to the cloud

## License

This project is licensed under the MIT License.