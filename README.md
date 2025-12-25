# 💬 AI-Powered Database Query Assistant

A natural language interface to interact with your databases using AI. Ask questions in plain English, get SQL queries, results, and automatic visualizations—no SQL knowledge required!

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-121212?style=flat&logo=chainlink&logoColor=white)](https://langchain.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)

---

## 🚀 Features

### 💾 Smart Database Connection

- Support for **SQLite**, **PostgreSQL**, and **MySQL**
- Connect via file selection or custom connection URL
- Auto-detect database schema and tables

### 🤖 Natural Language to SQL

- Ask questions in plain English (or any language!)
- AI automatically generates and executes SQL queries
- Powered by **Google Gemini** and **LangChain Agent**

### 📊 Auto-Visualization

- Intelligent chart generation based on query results
- Supports: Bar charts, Line charts, Pie charts, Histograms, Scatter plots
- Automatic detection of best chart type for your data

### 🔄 Context-Aware Conversation

- Memory of previous questions for follow-up queries
- Chat-based interface for seamless interaction
- Retry mechanism with validation for better accuracy

### 📈 Advanced Features

- **LangSmith Integration**: Monitor and trace all LLM interactions
- **SQL Query Preview**: View generated SQL in collapsible sections
- **Error Handling**: Smart retry with validation and error recovery
- **Interactive Tables**: Browse results with Streamlit's data viewer

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io) - Interactive web interface
- **LLM Framework**: [LangChain](https://langchain.com) - Agent orchestration
- **LLM Model**: [Google Gemini](https://ai.google.dev) - Natural language understanding
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org) - Universal database connector
- **Visualization**: [Plotly](https://plotly.com) - Interactive charts
- **Monitoring**: [LangSmith](https://smith.langchain.com) - LLM observability

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://ai.google.dev))
- (Optional) LangSmith API key for monitoring

### Steps

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd "NEW PROJECT"
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   LANGCHAIN_API_KEY=your_langsmith_api_key_here  # Optional
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com  # Optional
   ```

4. **Add your database files** (optional)

   Place your `.db` or `.sqlite` files in the `database/` folder for easy access.

5. **Run the application**

   ```bash
   streamlit run app.py
   ```

6. **Open your browser**

   Navigate to `http://localhost:8501`

---

## 🎯 Usage

### Quick Start

1. **Connect to a database**

   - Choose "Use Existing Database" and select from available files
   - Or choose "Custom Database URL" and enter your connection string
   - Click **Connect**

2. **Ask questions naturally**

   - Example: _"What are the top 5 products by price?"_
   - Example: _"Show me sales trends for the last 6 months"_
   - Example: _"How many customers are from California?"_

3. **View results**
   - See the AI-generated answer
   - Browse the data table
   - Explore auto-generated visualizations
   - Check the SQL query used (expandable)

### Example Queries

```
📌 "List all table names in the database"
📌 "Show the first 10 rows from the customers table"
📌 "What's the total revenue this year?"
📌 "Compare sales by region and show a bar chart"
📌 "Find all orders above $1000"
```

### Supported Databases

- **SQLite**: `sqlite:///path/to/database.db`
- **PostgreSQL**: `postgresql://user:password@host:port/database`
- **MySQL**: `mysql://user:password@host:port/database`

---

## 📂 Project Structure

```
NEW PROJECT/
├── app.py                      # Main Streamlit application
├── modules/
│   ├── database_query.py       # Database query agent module
│   ├── csv_analysis.py         # CSV analysis module
│   ├── research_agent.py       # Research agent module
│   ├── google_drive.py         # Google Drive integration
│   └── auto_dashboard.py       # Auto dashboard module
├── database/                   # Database files folder
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
└── README.md                   # This file
```

---

## ⚙️ Configuration

### Customize the LLM Model

Edit `modules/database_query.py` to change the model:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # Change to your preferred model
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)
```

### Adjust Retry & Validation

Modify the retry logic in the agent response section:

```python
max_retries = 2  # Change this value
```

---

## 🔒 Privacy & Security

- All processing happens locally or via your own API keys
- No data is sent to third parties (except LLM API calls)
- Database credentials are stored locally in `.env`
- LangSmith monitoring is optional and can be disabled

---

## 🐛 Known Limitations

- **API Rate Limits**: Google Gemini has free tier quotas
- **Complex Queries**: Very complex SQL may require manual refinement
- **Large Tables**: Auto-visualization limited to 100 rows for performance
- **Memory**: Conversation context limited to last 6 messages (3 exchanges)

---

## 🚧 Roadmap / Future Improvements

- [ ] Export results and charts to PDF reports
- [ ] Compare data from CSV files vs database
- [ ] Advanced RAG for document Q&A
- [ ] Multi-database comparison queries
- [ ] Custom chart styling and templates
- [ ] FastAPI backend for production deployment

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 🙏 Acknowledgments

- **LangChain** for the powerful agent framework
- **Google Gemini** for state-of-the-art LLM capabilities
- **Streamlit** for making web apps easy and beautiful
- **Plotly** for stunning interactive visualizations

---

## 📧 Contact

For questions, issues, or collaboration:

- Open an issue on GitHub

---

**Built with ❤️ using AI and Python**
