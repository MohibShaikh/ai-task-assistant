# 🚂 Railway Deployment Guide

## Quick Deploy to Railway

### Step 1: Create GitHub Repository

1. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/yourusername/ai-task-assistant.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Railway

1. **Go to Railway.app**
   - Visit [railway.app](https://railway.app)
   - Sign up/Login with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `ai-task-assistant` repository

3. **Configure Environment Variables**
   - Go to your project settings
   - Add these environment variables:

   ```env
   # Required
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   PINECONE_INDEX_NAME=your_index_name
   SECRET_KEY=your_secure_secret_key
   FLASK_ENV=production
   
   # Optional
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

4. **Deploy**
   - Railway will automatically detect it's a Python app
   - It will use the `requirements.txt` file
   - The `railway.json` config will handle the deployment

### Step 3: Get Your Pinecone API Keys

1. **Create Pinecone Account**
   - Go to [pinecone.io](https://pinecone.io)
   - Sign up for free account

2. **Create Index**
   - Click "Create Index"
   - Name: `ai-task-assistant`
   - Dimensions: `768`
   - Metric: `cosine`
   - Cloud: Choose closest to you

3. **Get API Keys**
   - Go to API Keys section
   - Copy your API key
   - Note your environment (e.g., `us-east-1-aws`)

### Step 4: Configure Environment Variables

In Railway dashboard, add these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `PINECONE_API_KEY` | `your_api_key` | Your Pinecone API key |
| `PINECONE_ENVIRONMENT` | `us-east-1-aws` | Your Pinecone environment |
| `PINECONE_INDEX_NAME` | `ai-task-assistant` | Your index name |
| `SECRET_KEY` | `random_secret_key` | Flask secret key |
| `FLASK_ENV` | `production` | Production mode |

### Step 5: Deploy and Test

1. **Monitor Deployment**
   - Watch the build logs
   - Check for any errors

2. **Test Your App**
   - Visit your Railway URL
   - Test registration/login
   - Test task creation

## Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn web_app:app --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### requirements.txt
```
flask>=2.3.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
numpy>=1.24.0
pyyaml>=6.0
requests>=2.31.0
python-dotenv>=1.0.0
pinecone>=2.2.0
colorama>=0.4.6
bcrypt>=4.0.0
flask-talisman>=1.1.0
flask-limiter>=2.8.0
gunicorn>=21.0.0
flask-cors>=6.0.0
```

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` syntax
   - Ensure all dependencies are compatible
   - Check Railway logs for specific errors

2. **App Won't Start**
   - Verify environment variables are set
   - Check if Pinecone API key is valid
   - Ensure index exists in Pinecone

3. **Health Check Fails**
   - Verify `/health` endpoint works
   - Check if app is binding to correct port
   - Review Railway logs

4. **Memory Issues**
   - Railway free tier has 512MB RAM
   - Consider upgrading for larger models
   - Optimize model loading

### Logs and Monitoring

1. **View Logs**
   - Go to Railway dashboard
   - Click on your service
   - View "Deployments" tab

2. **Health Check**
   - Visit: `https://your-app.railway.app/health`
   - Should return JSON status

3. **Environment Variables**
   - Check all variables are set correctly
   - No typos in variable names

## Cost Optimization

### Free Tier Limits
- **512MB RAM**
- **1GB Storage**
- **500 hours/month**
- **1 concurrent deployment**

### Upgrade Options
- **$5/month**: 1GB RAM, 2GB Storage
- **$10/month**: 2GB RAM, 4GB Storage
- **$20/month**: 4GB RAM, 8GB Storage

## Security Best Practices

1. **Environment Variables**
   - Never commit secrets to Git
   - Use Railway's secure environment variables
   - Rotate API keys regularly

2. **HTTPS**
   - Railway provides free SSL certificates
   - All traffic is encrypted

3. **Rate Limiting**
   - App includes rate limiting
   - Configured for production use

## Custom Domain

1. **Add Custom Domain**
   - Go to Railway dashboard
   - Click "Settings" → "Domains"
   - Add your domain

2. **DNS Configuration**
   - Point your domain to Railway's CNAME
   - Wait for SSL certificate (automatic)

## Monitoring and Alerts

1. **Health Checks**
   - Railway monitors `/health` endpoint
   - Automatic restarts on failure

2. **Logs**
   - View real-time logs in dashboard
   - Set up log aggregation if needed

3. **Metrics**
   - Monitor CPU and memory usage
   - Track response times

## Backup and Recovery

1. **Database Backup**
   - Pinecone data is automatically backed up
   - Consider exporting data periodically

2. **Code Backup**
   - GitHub serves as your code backup
   - Use Git tags for releases

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Community**: [discord.gg/railway](https://discord.gg/railway)
- **Status**: [status.railway.app](https://status.railway.app)

---

🎉 **Your AI Task Assistant is now deployed on Railway!** 