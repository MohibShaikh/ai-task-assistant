# AI Task Assistant - Backend API

A powerful AI-powered task management backend with intelligent suggestions, vector-based memory, and comprehensive security features.

## 🌟 Features

- **AI-Powered Task Management**: Smart task suggestions and categorization
- **Vector Memory**: Advanced semantic search using Pinecone vector database
- **Hugging Face API**: Cloud-based embeddings for multilingual support
- **RESTful API**: Complete backend API for task management
- **Security**: OWASP-compliant with rate limiting, CORS, and secure authentication
- **Analytics**: Task completion tracking and productivity insights
- **Google OAuth**: Secure login with Google accounts (optional)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Pinecone API key
- Hugging Face API token (optional, for better performance)
- Google OAuth credentials (optional)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MohibShaikh/ai-task-assistant
   cd AI_Task_Assistant
   ```

2. **Set up virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp config_sample.env .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python web_app.py
   ```

## 📁 Project Structure

```
AI_Task_Assistant/
├── web_app.py              # Main Flask application
├── hf_api.py              # Hugging Face API wrapper
├── task_assistant.py       # AI task processing
├── pinecone_memory.py      # Vector database operations
├── user_manager.py         # User authentication & management
├── smart_suggestions.py    # AI-powered suggestions
├── task_analytics.py       # Analytics and insights
├── security_monitor.py     # Security monitoring
├── static/                 # Web assets (CSS, JS)
├── templates/              # HTML templates
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name

# Hugging Face API (Optional but recommended)
HF_TOKEN=your_hugging_face_token

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

### Hugging Face API Setup

For better performance and multilingual support:

1. Create a Hugging Face account at [huggingface.co](https://huggingface.co)
2. Go to Settings → Access Tokens
3. Create a new token with "Read" permissions
4. Add `HF_TOKEN=your_token` to your `.env` file

**Benefits:**
- No local model loading (~500MB RAM saved)
- Better multilingual support (Roman Urdu, etc.)
- Always up-to-date models
- Faster deployment

See `HUGGING_FACE_SETUP.md` for detailed instructions.

### Pinecone Setup

1. Create a Pinecone account at [pinecone.io](https://pinecone.io)
2. Create a new index with dimension 768
3. Get your API key and environment
4. Update your `.env` file

## 🚀 Deployment

### Cloud Platforms

This backend is ready for deployment on:
- **Railway**: Connect GitHub repository and set environment variables
- **Render**: Use `requirements.txt` and `gunicorn`
- **Heroku**: Use `Procfile` and `runtime.txt`
- **VPS**: Use `gunicorn` for production

### Production Files

The following files are included for production deployment:
- `requirements.txt` - Python dependencies
- `Procfile` - Production server configuration
- `runtime.txt` - Python version specification

## 🔒 Security Features

- **OWASP Compliance**: Follows OWASP Top 10 security guidelines
- **Rate Limiting**: Prevents abuse with Flask-Limiter
- **CORS Protection**: Secure cross-origin requests
- **Input Validation**: Sanitized user inputs
- **Secure Headers**: HTTP security headers with Flask-Talisman
- **Password Hashing**: Bcrypt for secure password storage
- **Session Management**: Secure session handling

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/validate` - Session validation

### Tasks
- `GET /api/tasks` - Get user tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Analytics
- `GET /api/analytics` - Get user analytics
- `GET /api/suggestions` - Get AI suggestions

### Health Check
- `GET /health` - Application health status

## 🧪 Testing

Run tests from the `tests/` directory:

```bash
# Security tests
python tests/test_security.py

# Authentication tests
python tests/test_auth.py

# Task management tests
python tests/test_task_update.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **API Documentation**: Check the endpoints above
- **Security**: All security features are OWASP-compliant
- **Flutter Integration**: See `FLUTTER_SEPARATION.md`

---

🎉 **Your AI Task Assistant backend is ready for production deployment!** 
