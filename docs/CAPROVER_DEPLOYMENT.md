# CapRover Deployment Guide

## Deployment Options

### Option A: Deploy from Docker Hub (Recommended)

If the image is published to Docker Hub, deploy directly:

1. Create app in CapRover dashboard
2. Go to **Deployment** → **Deploy via ImageName**
3. Enter: `miometrix/dolibarr-mcp:2.1.0`
4. Click **Deploy**

### Option B: Deploy from Source (Build on CapRover)

CapRover will build the image from the Dockerfile:

```bash
# Via CLI
caprover deploy -a dolibarr-mcp
```

Or create manually in CapRover dashboard.

---

## Publishing to Docker Hub (First Time)

Before using Option A, publish the image:

```bash
# Login to Docker Hub
docker login

# Build and tag the image
cd /path/to/dolibarr-mcp-custom
docker build -f docker/Dockerfile -t miometrix/dolibarr-mcp:2.1.0 .
docker tag miometrix/dolibarr-mcp:2.1.0 miometrix/dolibarr-mcp:latest

# Push to Docker Hub
docker push miometrix/dolibarr-mcp:2.1.0
docker push miometrix/dolibarr-mcp:latest
```

Or use GitHub Actions (automatic on push to main):
1. Add secrets to GitHub repo: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
2. Push to main branch - image builds automatically

---

### 2. Configure Environment Variables

In CapRover dashboard, go to **App Configs** → **Environmental Variables**:

```
# Required - Dolibarr API
DOLIBARR_URL=https://your-dolibarr.com/api/index.php
DOLIBARR_API_KEY=your_dolibarr_api_key

# Required - MCP Authentication
MCP_AUTH_ENABLED=true
MCP_API_KEY=<generate with: python scripts/generate_api_key.py>

# Optional - Cache (requires separate DragonflyDB/Redis service)
CACHE_ENABLED=true
DRAGONFLY_HOST=srv-captain--dragonfly
DRAGONFLY_PORT=6379

# Optional - Output format
OUTPUT_FORMAT=toon
LOG_LEVEL=INFO

# Server config
MCP_TRANSPORT=http
MCP_HTTP_PORT=8080
MCP_HTTP_HOST=0.0.0.0
```

### 3. Enable HTTPS

In CapRover dashboard:
- Enable HTTPS
- Force HTTPS redirect

### 4. Connect Container Network

If using DragonflyDB cache, ensure both apps are on the same network:

```bash
# In DragonflyDB app config, note the internal name: srv-captain--dragonfly
# Use this as DRAGONFLY_HOST in MCP config
```

## Generate API Key

```bash
# On your local machine
cd dolibarr-mcp-custom
python scripts/generate_api_key.py --env

# Output:
# MCP_API_KEY=a1b2c3d4...
```

## Connecting from AI Agents

### Claude Code / MCP Client

```json
{
  "mcpServers": {
    "dolibarr": {
      "url": "https://dolibarr-mcp.your-domain.com/",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

### Open WebUI

In Open WebUI settings, add MCP connection:
- URL: `https://dolibarr-mcp.your-domain.com/`
- Headers: `Authorization: Bearer YOUR_MCP_API_KEY`

### HTTP API Example

```bash
curl -X POST https://dolibarr-mcp.your-domain.com/ \
  -H "Authorization: Bearer YOUR_MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_customers", "arguments": {"limit": 5}}}'
```

## Health Check

```bash
# No auth required
curl https://dolibarr-mcp.your-domain.com/health

# Response:
# {"status": "healthy", "service": "dolibarr-mcp", "version": "2.1.0", "auth_enabled": true}
```

## DragonflyDB Setup (Optional but Recommended)

1. Create new CapRover app: `dragonfly`

2. Deploy from Docker Hub:
   - Image: `docker.dragonflydb.io/dragonflydb/dragonfly:latest`

3. Configure:
   - Port: 6379 (internal only, no need to expose)
   - Memory limit: 256MB

4. In MCP app, set:
   ```
   DRAGONFLY_HOST=srv-captain--dragonfly
   ```

## CI/CD: Despliegue Automático desde GitHub

### Configurar GitHub Actions + CapRover

1. **En CapRover**, obtén el token de la app:
   - Dashboard → Apps → `dolibarr-mcp` → Deployment
   - Copia el **App Token** (o genera uno nuevo)

2. **En GitHub**, agrega los secrets al repositorio:
   - Settings → Secrets and variables → Actions → New repository secret

   ```
   CAPROVER_SERVER=https://captain.tu-dominio.com
   CAPROVER_APP=dolibarr-mcp
   CAPROVER_TOKEN=tu-app-token-aqui
   ```

3. **Push a main** - el workflow automáticamente:
   - Clona el repo
   - Envía a CapRover
   - CapRover construye la imagen desde el Dockerfile
   - Despliega el contenedor

### Webhook Manual (Alternativa)

Si prefieres no usar GitHub Actions:

1. En CapRover, habilita **Method 3: Deploy from Github** en Deployment
2. Agrega el webhook URL a tu repo de GitHub
3. Cada push dispara el build automáticamente

---

## Troubleshooting

### Auth Errors (401/403)

1. Check API key is set: `MCP_API_KEY` in CapRover env vars
2. Verify header format: `Authorization: Bearer <key>`
3. Check rate limits (100 req/min default)

### Connection Issues

1. Verify Dolibarr URL is accessible from CapRover server
2. Check DOLIBARR_API_KEY has correct permissions
3. Review logs: CapRover dashboard → Logs

### Cache Not Working

1. Verify DragonflyDB is running
2. Check network connectivity between services
3. Set `CACHE_ENABLED=false` to disable if issues persist
