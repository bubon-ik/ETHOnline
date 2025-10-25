# 🚀 DEPLOYMENT GUIDE - BlockScout AI Bot

## 🌐 Railway Deployment (RECOMMENDED - FREE)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

### Step 2: Deploy from GitHub
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `ETHOnline` repository
4. Railway will automatically detect `Procfile`

### Step 3: Set Environment Variables
In Railway dashboard, go to Variables tab and add:

```
TELEGRAM_API_TOKEN=your_telegram_bot_token
CLAUDE_API_KEY=your_claude_api_key
```

### Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Your bot will be running 24/7!

---

## 🐳 Alternative: Heroku (PAID)

### Step 1: Install Heroku CLI
```bash
# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Or download from heroku.com
```

### Step 2: Login and Create App
```bash
heroku login
heroku create your-bot-name
```

### Step 3: Set Environment Variables
```bash
heroku config:set TELEGRAM_API_TOKEN=your_token
heroku config:set CLAUDE_API_KEY=your_key
```

### Step 4: Deploy
```bash
git push heroku main
```

---

## 🔧 Local Development

### Run Locally
```bash
cd /home/user/Documents/ETHOnline
source venv/bin/activate
python bot.py
```

### Test Commands
- `/start` - Welcome message
- `/analyze vitalik.eth` - Test analysis
- `/help` - Command reference

---

## 📊 Monitoring

### Railway Dashboard
- View logs in real-time
- Monitor resource usage
- Restart if needed

### Bot Status
- Check if bot responds in Telegram
- Monitor API calls in logs
- Verify MCP tool usage

---

## 🚨 Troubleshooting

### Bot Not Responding
1. Check Railway logs for errors
2. Verify environment variables
3. Restart deployment

### API Errors
1. Check Claude API quota
2. Verify Telegram token
3. Review rate limits

### MCP Tool Issues
1. Check Blockscout API status
2. Verify tool calls in logs
3. Test with simple queries

---

## 🏆 Production Checklist

- [x] ✅ Bot deployed and running
- [x] ✅ Environment variables set
- [x] ✅ Procfile configured
- [x] ✅ Logs accessible
- [x] ✅ Bot responds in Telegram
- [x] ✅ MCP tools working
- [x] ✅ Error handling active

**Your bot is ready for ETHOnline 2025!** 🎉
