# 🍜 Kitchen Intel - Streamlit Authentication

A secure Streamlit application with username/password authentication using **environment variables only**.

## 🚀 Quick Start

1. **Set up authentication:**
   ```bash
   python3 setup_env_auth.py
   ```

2. **Set environment variables** (copy from setup script output)

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

4. **Login** with your credentials

## 🔐 Environment Variables

### Required Variables
```bash
AUTH_USERNAME=admin
AUTH_NAME=Administrator
AUTH_EMAIL=admin@example.com
AUTH_PASSWORD=$2b$12$your_bcrypt_hashed_password
API_URL=http://localhost:8080
API_KEY=your_api_key_here
```

### Optional Variables
```bash
# Cookie configuration (omit for session-only auth)
AUTH_COOKIE_NAME=kitchen_intel_auth_cookie
AUTH_COOKIE_KEY=your_secret_key_here
AUTH_COOKIE_EXPIRY=1

# Suppress warnings
PYTHONWARNINGS=ignore
```

## 🐳 Docker Deployment

```bash
# Build
docker build -t kitchen-intel .

# Run with environment variables
docker run -p 8080:8080 \
  -e AUTH_USERNAME=admin \
  -e AUTH_NAME="Administrator" \
  -e AUTH_EMAIL=admin@example.com \
  -e AUTH_PASSWORD='$2b$12$your_hash' \
  -e API_URL=http://localhost:8080 \
  -e API_KEY=your_api_key \
  kitchen-intel
```

## 🌐 Platform Deployment

### Railway
Set environment variables in Railway dashboard and deploy!

### Render.com
Set environment variables in Render dashboard and deploy!

### Heroku
```bash
heroku config:set AUTH_USERNAME=admin
heroku config:set AUTH_NAME="Administrator"
heroku config:set AUTH_EMAIL=admin@example.com
heroku config:set AUTH_PASSWORD='$2b$12$your_hash'
```

## 📁 Project Structure

```
├── main.py                 # Application entry point
├── kitchen_intel_app.py    # Main app logic
├── auth/
│   ├── authentication_manager.py  # Core auth logic
│   ├── config_manager.py          # Environment variable handling
│   └── app_wrapper.py             # Authentication gate
├── setup_env_auth.py       # Setup script
├── test_hash.py           # Password hashing utility
├── Dockerfile             # Docker configuration
├── start.sh              # Startup script
└── requirements.txt       # Python dependencies
```

## 🔧 Features

✅ **Environment Variables Only** - No TOML/YAML files needed  
✅ **Secure Password Hashing** - Bcrypt encryption  
✅ **Session Management** - Optional cookie-based sessions  
✅ **API Authentication** - Automatic API key headers  
✅ **Docker Ready** - Production-ready containerization  
✅ **Platform Agnostic** - Works on Railway, Render, Heroku, etc.  
✅ **Clean Logout** - Proper session cleanup  
✅ **Error Handling** - Comprehensive error management  

## 🛠️ Development

### Local Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run setup script: `python3 setup_env_auth.py`
4. Create `.env` file with generated variables
5. Start app: `streamlit run main.py`

### Testing
```bash
# Test password hashing
python3 test_hash.py

# Test configuration parsing
python3 test_toml_parsing.py
```

## 🔒 Security

- Passwords stored as bcrypt hashes
- Environment variables for secure credential management
- Session-only authentication by default (no persistent cookies)
- API key authentication for backend requests
- No sensitive data in code or version control

## 📚 Documentation

- [Environment Setup Guide](ENV_SETUP.md) - Detailed setup instructions
- [Deployment Guide](DEPLOYMENT.md) - Platform-specific deployment
- [Railway Fix](railway-fix.md) - Railway deployment troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Simple. Secure. Environment Variables Only.** 🎯