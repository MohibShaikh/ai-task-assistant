# AI Task Assistant

An intelligent task management system with AI-powered suggestions, vector-based memory, and multi-platform support (Web + Flutter Mobile App).

## 🌟 Features

- **AI-Powered Task Management**: Smart task suggestions and categorization
- **Vector Memory**: Advanced semantic search using Pinecone vector database
- **Multi-Platform**: Web interface and Flutter mobile app
- **Security**: OWASP-compliant with rate limiting, CORS, and secure authentication
- **Analytics**: Task completion tracking and productivity insights
- **Google OAuth**: Secure login with Google accounts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flutter SDK (for mobile app)
- Pinecone API key
- Google OAuth credentials (optional)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
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

### Mobile App Setup

1. **Navigate to Flutter app**
   ```bash
   cd flutter_app
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   flutter run
   ```

## 📁 Project Structure

```
AI_Task_Assistant/
├── web_app.py              # Main Flask application
├── task_assistant.py       # AI task processing
├── pinecone_memory.py      # Vector database operations
├── user_manager.py         # User authentication & management
├── smart_suggestions.py    # AI-powered suggestions
├── task_analytics.py       # Analytics and insights
├── security_monitor.py     # Security monitoring
├── static/                 # Web assets (CSS, JS)
├── templates/              # HTML templates
├── tests/                  # Test files
├── flutter_app/            # Flutter mobile application
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

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

### Pinecone Setup

1. Create a Pinecone account at [pinecone.io](https://pinecone.io)
2. Create a new index with dimension 768
3. Get your API key and environment
4. Update your `.env` file

## 🚀 Deployment

### Free Cloud Platforms

The app is ready for deployment on:
- **Railway**: [Deployment Guide](DEPLOYMENT_GUIDE.md#railway)
- **Render**: [Deployment Guide](DEPLOYMENT_GUIDE.md#render)
- **Heroku**: [Deployment Guide](DEPLOYMENT_GUIDE.md#heroku)

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Configure HTTPS
- [ ] Set up proper logging
- [ ] Configure database (if using external DB)
- [ ] Set up monitoring
- [ ] Configure CORS for production domains

## 🔒 Security Features

- **OWASP Compliance**: Follows OWASP Top 10 security guidelines
- **Rate Limiting**: Prevents abuse with Flask-Limiter
- **CORS Protection**: Secure cross-origin requests
- **Input Validation**: Sanitized user inputs
- **Secure Headers**: HTTP security headers with Flask-Talisman
- **Password Hashing**: Bcrypt for secure password storage
- **Session Management**: Secure session handling

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [Architecture Guide](ARCHITECTURE_GUIDE.md)
- **Security**: [Security Assessment](SECURITY_ASSESSMENT.md)
- **Testing**: [Testing Guide](TESTING_GUIDE.md)
- **Deployment**: [Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🔄 Version History

- **v1.0.0**: Initial release with web interface
- **v1.1.0**: Added Flutter mobile app
- **v1.2.0**: Enhanced security features
- **v1.3.0**: Google OAuth integration
- **v1.4.0**: Production deployment ready 