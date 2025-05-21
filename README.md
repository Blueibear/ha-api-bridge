# Home Assistant API Bridge

This repo contains:
- \`ha_entity_server.py\` — your Flask app  
- \`gpt_proxy.py\` — the proxy that injects your API key  
- \`requirements.txt\`  
- Cloudflared tunnel config in \`~/.cloudflared/config.yml\` (not committed)  
- Instructions to run locally or via systemd  

## Quick start

\`\`\`bash
pip install -r requirements.txt
python3 ha_entity_server.py &
python3 gpt_proxy.py &
\`\`\`
