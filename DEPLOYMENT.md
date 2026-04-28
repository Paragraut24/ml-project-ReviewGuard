# Deployment Guide

This guide covers deploying ReviewGuard to various cloud platforms.

## Prerequisites

Before deploying, ensure you have:

- [ ] A HuggingFace account (for model hosting)
- [ ] Your BERT model uploaded to HuggingFace (private repository recommended)
- [ ] HuggingFace API token (if using private models)
- [ ] Git installed locally
- [ ] Python 3.11+ installed locally (for testing)

## Environment Variables

All platforms require these environment variables:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `HF_MODEL_ID` | Yes | HuggingFace model identifier | `username/model-name` |
| `HF_TOKEN` | Optional* | HuggingFace API token | `hf_xxxxx` |
| `MODEL_BACKEND` | No | Backend selection | `auto` (default) |
| `FLASK_DEBUG` | No | Debug mode | `0` (production) |
| `SECRET_KEY` | Yes | Flask secret key | Random 32-byte hex |
| `PORT` | No | Server port | `5000` (default) |

*Required only for private models

### Generating SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Platform-Specific Guides

### 1. Render (Recommended)

**Pros:** Free tier, automatic HTTPS, easy setup  
**Cons:** Cold starts on free tier

#### Steps:

1. **Fork/Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/reviewguard.git
   git push -u origin main
   ```

2. **Create New Web Service**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   - **Name:** `reviewguard`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free or Starter

4. **Set Environment Variables**
   - Go to "Environment" tab
   - Add all required variables
   - Click "Save Changes"

5. **Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait for build to complete (~5-10 minutes)
   - Access your app at `https://reviewguard.onrender.com`

#### render.yaml Configuration

The included `render.yaml` automates deployment:

```yaml
services:
  - type: web
    name: reviewguard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: HF_MODEL_ID
        sync: false
      - key: HF_TOKEN
        sync: false
      - key: SECRET_KEY
        generateValue: true
```

### 2. Railway

**Pros:** Generous free tier, fast deployments  
**Cons:** Requires credit card for free tier

#### Steps:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set HF_MODEL_ID=your-model-id
   railway variables set HF_TOKEN=your-token
   railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   railway variables set FLASK_DEBUG=0
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get URL**
   ```bash
   railway domain
   ```

### 3. Heroku

**Pros:** Mature platform, good documentation  
**Cons:** No free tier anymore

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create App**
   ```bash
   heroku create reviewguard-app
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set HF_MODEL_ID=your-model-id
   heroku config:set HF_TOKEN=your-token
   heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   heroku config:set FLASK_DEBUG=0
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Open App**
   ```bash
   heroku open
   ```

### 4. AWS (Advanced)

For production deployments with high traffic:

#### Option A: Elastic Beanstalk

1. Install EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create reviewguard-env`
4. Set environment variables in AWS Console
5. Deploy: `eb deploy`

#### Option B: ECS + Fargate

1. Create Docker image
2. Push to ECR
3. Create ECS cluster
4. Define task and service
5. Configure load balancer

### 5. Google Cloud Platform

#### App Engine

1. Install gcloud CLI
2. Create `app.yaml`
3. Deploy: `gcloud app deploy`

#### Cloud Run

1. Build container: `gcloud builds submit`
2. Deploy: `gcloud run deploy`

## Post-Deployment Checklist

After deploying, verify:

- [ ] Application loads at the deployed URL
- [ ] Landing page displays correctly
- [ ] Workbench accepts and analyzes reviews
- [ ] All navigation links work
- [ ] HTTPS is enabled
- [ ] Environment variables are set correctly
- [ ] No errors in application logs
- [ ] API endpoints respond correctly
- [ ] Rate limiting is working (if configured)

## Testing Your Deployment

### 1. Manual Testing

Visit these URLs and verify they work:

- `https://your-app.com/` - Landing page
- `https://your-app.com/workbench` - Analysis workbench
- `https://your-app.com/reports` - Performance reports
- `https://your-app.com/docs` - Documentation
- `https://your-app.com/settings` - Settings page
- `https://your-app.com/health` - Health check endpoint

### 2. API Testing

Test the prediction endpoint:

```bash
curl -X POST https://your-app.com/predict \
  -H "Content-Type: application/json" \
  -d '{"review": "AMAZING!!! Best product EVER!!!"}'
```

Expected response:
```json
{
  "verdict": "FAKE",
  "confidence": 94.2,
  "bert_score": 92.5,
  "gnn_score": 87.1,
  ...
}
```

### 3. Load Testing (Optional)

Use tools like Apache Bench or Locust:

```bash
ab -n 100 -c 10 https://your-app.com/
```

## Monitoring

### Application Logs

**Render:**
```bash
# View logs in dashboard or CLI
render logs -t reviewguard
```

**Railway:**
```bash
railway logs
```

**Heroku:**
```bash
heroku logs --tail
```

### Error Tracking

Consider integrating:

- **Sentry** - Error tracking and monitoring
- **LogRocket** - Session replay and debugging
- **New Relic** - Application performance monitoring

### Uptime Monitoring

Use services like:

- **UptimeRobot** - Free uptime monitoring
- **Pingdom** - Advanced monitoring
- **StatusCake** - Website monitoring

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms:** Build succeeds but app crashes on startup

**Solutions:**
- Check environment variables are set correctly
- Verify `HF_MODEL_ID` is correct
- Check logs for specific error messages
- Ensure `requirements.txt` includes all dependencies

#### 2. Model Loading Fails

**Symptoms:** "HuggingFace model not found" error

**Solutions:**
- Verify `HF_MODEL_ID` format: `username/model-name`
- Check model repository is public or `HF_TOKEN` is set
- Try setting `MODEL_BACKEND=hf_api` explicitly

#### 3. Slow Response Times

**Symptoms:** Requests take >30 seconds

**Solutions:**
- Use `MODEL_BACKEND=hf_api` for faster cold starts
- Upgrade to paid tier to avoid cold starts
- Implement caching for repeated requests
- Consider using a CDN

#### 4. Out of Memory

**Symptoms:** App crashes with memory errors

**Solutions:**
- Use `MODEL_BACKEND=hf_api` (offloads model to HuggingFace)
- Upgrade to plan with more RAM
- Optimize model loading (lazy loading)

### Getting Help

If you encounter issues:

1. Check application logs first
2. Review this deployment guide
3. Search existing GitHub issues
4. Open a new issue with:
   - Platform (Render/Railway/Heroku)
   - Error messages from logs
   - Steps to reproduce
   - Environment variable configuration (without secrets!)

## Security Considerations

### Production Checklist

- [ ] `FLASK_DEBUG=0` is set
- [ ] Strong `SECRET_KEY` is generated
- [ ] HTTPS is enabled
- [ ] Environment variables are not exposed in logs
- [ ] Rate limiting is configured
- [ ] CORS is properly configured
- [ ] Error messages don't expose sensitive information
- [ ] Dependencies are up to date

### Secrets Management

**Never:**
- Commit `.env` files to Git
- Share `HF_TOKEN` publicly
- Expose `SECRET_KEY` in logs
- Use default or weak secrets

**Always:**
- Use platform-specific secret management
- Rotate secrets regularly
- Use different secrets for dev/staging/prod
- Monitor for leaked secrets

## Updating Your Deployment

### Render

Automatic deployment on git push (if enabled), or:
```bash
# Manual deploy via dashboard
```

### Railway

```bash
railway up
```

### Heroku

```bash
git push heroku main
```

## Scaling

### Horizontal Scaling

Add more instances:

**Render:** Upgrade plan and increase instance count  
**Railway:** Add replicas in dashboard  
**Heroku:** `heroku ps:scale web=2`

### Vertical Scaling

Increase resources per instance:

**Render:** Upgrade to higher tier plan  
**Railway:** Increase memory/CPU in settings  
**Heroku:** `heroku ps:resize web=standard-2x`

## Cost Optimization

### Free Tier Limits

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| Render | 750 hours/month | Cold starts, sleeps after 15min inactivity |
| Railway | $5 credit/month | Requires credit card |
| Heroku | None | Paid plans only |

### Recommendations

- **Development:** Use Render free tier
- **Production (low traffic):** Railway Starter ($5/month)
- **Production (high traffic):** Render Standard ($25/month) or AWS

## Support

For deployment assistance:

- **Documentation:** Check `/docs` on your deployed app
- **GitHub Issues:** [Report deployment issues](https://github.com/Paragraut24/ml-project-ReviewGuard/issues)
- **Platform Support:** Contact your hosting platform's support

---

**Last Updated:** 2026-01-01

