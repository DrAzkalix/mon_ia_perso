# Guide d'installation — Hermes ↔ OpenClaw via MCP

> **Infrastructure multi-agents IA sur VPS Hostinger**  
> Connexion de deux agents via le protocole MCP (Model Context Protocol)

---

## 📋 Table des matières

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Étape 1 — Activer l'endpoint HTTP d'OpenClaw](#étape-1--activer-lendpoint-http-dopenclaw)
5. [Étape 2 — Pont réseau Docker + socat](#étape-2--pont-réseau-docker--socat)
6. [Étape 3 — SDK MCP + Bridge Python](#étape-3--sdk-mcp--bridge-python)
7. [Étape 4 — Wrapper shell + déclaration MCP](#étape-4--wrapper-shell--déclaration-mcp)
8. [Étape 5 — Tests de délégation](#étape-5--tests-de-délégation)
9. [Étape 6 — Persistance via systemd](#étape-6--persistance-via-systemd)
10. [Dépannage (FAQ)](#dépannage-faq)
11. [Commandes essentielles (antisèche)](#commandes-essentielles-antisèche)
12. [Sécurité](#sécurité)

---

## Introduction

Ce guide vous permet de connecter **deux agents IA** hébergés sur un même VPS :
- **Hermes** — L'agent principal qui reçoit vos demandes
- **OpenClaw (Alex)** — Un sous-agent spécialisé (ex: marketing)

La communication utilise le **protocole MCP** avec un bridge Python custom.

### Ce que vous allez construire

```
Vous ──→ Hermes ──MCP──→ Bridge Python ──HTTP──→ OpenClaw (Alex)
                           traducteur              ↓
                                              Répond à Hermes
```

**Durée estimée :** 2h30 - 3h (avec pauses compilation)

---

## Architecture

### Vue d'ensemble

| Composant | Rôle | Emplacement |
|-----------|------|-------------|
| **HERMES** | Agent principal (utilise MCP) | Container Docker `VOTRE_HERMES` |
| **Bridge Python** | Traduit MCP → HTTP | Dans Hermes : `/opt/data/` |
| **socat** | Relais TCP (18790 → 18789) | Dans OpenClaw (installé via brew) |
| **OPENCLAW** | Sous-agent spécialisé | Container Docker `VOTRE_OPENCLAW` |
| **systemd** | Gardien de socat (persistance) | Hôte VPS : `/etc/systemd/system/` |

### Flux d'une requête

1. Vous écrivez à Hermes
2. Hermes décide d'utiliser `openclaw:ask` ou `openclaw:delegate`
3. Hermes lance le bridge Python (via MCP stdio)
4. Le bridge fait un `POST HTTP` vers `VOTRE_OPENCLAW:18790`
5. socat relaie vers le port 18789 (loopback OpenClaw)
6. Alex (OpenClaw) traite et répond
7. La réponse remonte par le chemin inverse
8. Vous recevez la réponse

---

## Prérequis

### Sur votre VPS Hostinger

Vous devez avoir installé via le **Docker Manager** :
- ✅ Un projet `hermes-agent-*`
- ✅ Un projet `openclaw-*`
- ✅ Un projet `traefik` (reverse-proxy, installé par défaut)

### Accès nécessaires

- ✅ Session **SSH root** sur le VPS (bouton "Terminal" dans Docker Manager)
- ✅ Votre **token Gateway OpenClaw** (bouton "Jeton de passerelle" dans le panel)

### Identifier vos noms de conteneurs

```bash
docker ps
```

Notez les noms exacts dans la colonne **NAMES** :

| Rôle | Format | Votre nom réel |
|------|--------|----------------|
| Hermes | `hermes-agent-XXXX-hermes-agent-1` | `VOTRE_HERMES` |
| OpenClaw | `openclaw-XXXX-openclaw-1` | `VOTRE_OPENCLAW` |

> ⚠️ **Important :** Partout où vous voyez `VOTRE_HERMES` ou `VOTRE_OPENCLAW` dans ce guide, remplacez-les par vos noms réels.

---

## Étape 1 — Activer l'endpoint HTTP d'OpenClaw

### Pourquoi ?

Par défaut, OpenClaw n'expose pas son API HTTP. On doit l'activer pour qu'Hermes puisse l'appeler.

### 1.1 Entrer dans le conteneur OpenClaw

```bash
docker exec -it VOTRE_OPENCLAW bash
```

Votre prompt change pour indiquer que vous êtes à l'intérieur du conteneur.

### 1.2 Sauvegarder la configuration

```bash
cp /data/.openclaw/openclaw.json /data/.openclaw/openclaw.json.bak
```

> 💡 **Règle d'or :** Toujours sauvegarder avant de modifier.

### 1.3 Modifier la config avec jq

```bash
cd /data/.openclaw && \
jq '.gateway.bind = "custom" |
    .gateway.customBindHost = "0.0.0.0" |
    .gateway.http = {
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }' openclaw.json > openclaw.json.new && \
mv openclaw.json.new openclaw.json && \
echo "✅ Config mise à jour"
```

### 1.4 Sortir et redémarrer

```bash
exit
docker restart VOTRE_OPENCLAW
sleep 10
docker logs --tail 20 VOTRE_OPENCLAW
```

**✅ Vérification :** Vous devez voir dans les logs :
- `[gateway] starting HTTP server...`
- `[gateway] ready (N plugins...)`

---

## Étape 2 — Pont réseau Docker + socat

### Pourquoi ?

Les deux conteneurs sont sur des réseaux isolés. On crée un réseau partagé pour qu'ils puissent communiquer.

### 2.1 Créer le réseau-pont

```bash
docker network create hermes-openclaw-bridge
docker network connect hermes-openclaw-bridge VOTRE_OPENCLAW
docker network connect hermes-openclaw-bridge VOTRE_HERMES
```

### 2.2 Installer socat dans OpenClaw

```bash
docker exec -it VOTRE_OPENCLAW bash
brew install socat
which socat
# Résultat attendu : /data/linuxbrew/.linuxbrew/bin/socat
exit
```

> ⏱️ **Patience :** Cette étape prend 5-10 minutes (compilation d'openssl).

### 2.3 Lancer socat manuellement (test)

```bash
docker exec -it VOTRE_OPENCLAW bash
socat -d TCP-LISTEN:18790,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:18789 &
exit
```

### 2.4 Tester la connectivité

⚠️ **Remplacez `VOTRE_TOKEN` par votre vrai token Gateway OpenClaw :**

```bash
docker exec VOTRE_HERMES sh -c \
  'curl -s -H "Authorization: Bearer VOTRE_TOKEN" \
   http://VOTRE_OPENCLAW:18790/v1/models'
```

**✅ Vérification :** Vous devez voir un JSON contenant `openclaw/main` dans la liste des modèles.

> 🚨 Si vous voyez `401 Unauthorized` : vous avez laissé littéralement le texte `VOTRE_TOKEN` au lieu de le remplacer par votre vrai token.

---

## Étape 3 — SDK MCP + Bridge Python

### Pourquoi ?

Hermes parle MCP, OpenClaw parle HTTP. Le bridge Python fait la traduction entre les deux.

### 3.1 Installer le SDK MCP dans Hermes

```bash
docker exec VOTRE_HERMES \
  uv pip install --python /opt/hermes/.venv/bin/python3 mcp

# Vérification
docker exec VOTRE_HERMES \
  /opt/hermes/.venv/bin/python3 -c \
  "from mcp.server import Server; import httpx; print('✅ OK')"
```

### 3.2 Créer le script bridge Python

Copiez-collez ce bloc en entier :

```bash
docker exec VOTRE_HERMES bash -c '
cat > /opt/data/openclaw_bridge.py << PYEOF
#!/usr/bin/env python3
import asyncio, json, logging, os, sys
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

BASE_URL = os.environ.get("OPENCLAW_BASE_URL", "http://VOTRE_OPENCLAW:18790/v1")
API_KEY = os.environ.get("OPENCLAW_API_KEY", "")
MODEL = os.environ.get("OPENCLAW_MODEL", "openclaw/main")

logging.basicConfig(level=logging.INFO, format="[bridge] %(message)s", stream=sys.stderr)
server = Server("openclaw-bridge")

@server.list_tools()
async def list_tools():
    return [
        Tool(name="ask",
             description="Ask Alex a quick question",
             inputSchema={"type":"object","properties":{"question":{"type":"string"}},"required":["question"]}),
        Tool(name="delegate",
             description="Delegate a full task to Alex",
             inputSchema={"type":"object","properties":{"prompt":{"type":"string"}},"required":["prompt"]}),
    ]

async def _call(messages):
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": MODEL, "messages": messages})
        return r.json()["choices"][0]["message"]["content"]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "ask":
        msg = [{"role":"user","content": arguments["question"]}]
    else:
        msg = [{"role":"user","content": arguments["prompt"]}]
    reply = await _call(msg)
    return [TextContent(type="text", text=reply)]

async def main():
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
PYEOF
chmod +x /opt/data/openclaw_bridge.py'
```

**✅ Vérification :**
```bash
docker exec VOTRE_HERMES ls -la /opt/data/openclaw_bridge.py
```

Vous devez voir un fichier d'environ 1500-1800 octets avec les permissions `-rwxr-xr-x`.

---

## Étape 4 — Wrapper shell + déclaration MCP

### Pourquoi ?

Le bridge Python a besoin de 3 variables d'environnement (token, URL, modèle). Le wrapper les définit avant de lancer Python.

### 4.1 Créer le wrapper shell

⚠️ **IMPORTANT :** Préparez cette commande dans un **éditeur de texte local**, remplacez `VOTRE_TOKEN` par votre vrai token, puis copiez-collez le tout :

```bash
docker exec VOTRE_HERMES bash -c '
cat > /opt/data/openclaw_bridge.sh << BASHEOF
#!/bin/bash
export OPENCLAW_API_KEY="VOTRE_TOKEN"
export OPENCLAW_BASE_URL="http://VOTRE_OPENCLAW:18790/v1"
export OPENCLAW_MODEL="openclaw/main"
exec /opt/hermes/.venv/bin/python3 /opt/data/openclaw_bridge.py
BASHEOF
chmod +x /opt/data/openclaw_bridge.sh'
```

### 4.2 Déclarer le bridge dans Hermes

```bash
echo "Y" | docker exec -i VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes mcp add openclaw \
  --command /opt/data/openclaw_bridge.sh

# Vérification
docker exec VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes mcp list
```

**✅ Vérification :** Vous devez voir une ligne `openclaw ✓ enabled` avec le transport pointant vers `openclaw_bridge.sh`.

---

## Étape 5 — Tests de délégation

### Test 1 — Ping/Pong

```bash
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Utilise le tool openclaw:ask pour demander à Alex : 'Réponds en une ligne : ping'. Reproduis sa réponse."
```

**✅ Résultat attendu :** Alex répond "Pong" ou similaire.

### Test 2 — Haïku créatif

```bash
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Utilise openclaw:delegate pour demander à Alex un haïku en français sur le printemps."
```

**✅ Résultat attendu :** Un haïku de 3 lignes rédigé par Alex.

### Test 3 — Auto-découverte

```bash
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Tu as accès à un sous-agent Alex via openclaw:ask et openclaw:delegate. Demande-lui qui il est."
```

**✅ Résultat attendu :** Alex se présente (rôle, capacités, environnement).

---

## Étape 6 — Persistance via systemd

### Pourquoi ?

socat tourne actuellement en arrière-plan manuel. Si vous redémarrez le VPS ou OpenClaw, il meurt. systemd le relancera automatiquement.

### 6.1 Créer le service systemd

```bash
cat > /etc/systemd/system/openclaw-socat-bridge.service << 'SYSEOF'
[Unit]
Description=OpenClaw ↔ Hermes TCP bridge (socat 18790 → 18789)
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=5s
ExecStartPre=/bin/bash -c 'until docker ps --format "{{.Names}}" 2>/dev/null | grep -q "^VOTRE_OPENCLAW$"; do sleep 3; done'
ExecStartPre=-/usr/bin/docker exec VOTRE_OPENCLAW bash -c "pkill -f 'socat.*TCP-LISTEN:18790' || true"
ExecStart=/usr/bin/docker exec VOTRE_OPENCLAW \
  /data/linuxbrew/.linuxbrew/bin/socat -d \
  TCP-LISTEN:18790,bind=0.0.0.0,fork,reuseaddr \
  TCP:127.0.0.1:18789
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SYSEOF
```

### 6.2 Activer et démarrer

```bash
# Recharger systemd
systemctl daemon-reload

# Activer le démarrage au boot
systemctl enable openclaw-socat-bridge.service

# Tuer le socat manuel existant
docker exec VOTRE_OPENCLAW pkill -f 'socat.*TCP-LISTEN:18790'

# Démarrer le service
systemctl start openclaw-socat-bridge.service

# Vérifier l'état
systemctl status openclaw-socat-bridge.service --no-pager
```

**✅ Vérification :** Cherchez la ligne `Active: active (running)` (en vert).

### 6.3 Test de résilience

```bash
# Tuer socat volontairement
docker exec VOTRE_OPENCLAW pkill -9 -f 'socat.*18790'

# Attendre 8 secondes
sleep 8

# Vérifier que socat est ressuscité
docker exec VOTRE_OPENCLAW ps aux | grep socat | grep -v grep
```

**✅ Vérification :** Vous voyez une ligne socat avec un nouveau PID et une heure de démarrage récente.

---

## Dépannage (FAQ)

### Connection refused sur le port 18790

**Cause :** socat ne tourne pas.

**Solution :**
```bash
systemctl status openclaw-socat-bridge
```
Si le service est en erreur, consultez les logs :
```bash
journalctl -u openclaw-socat-bridge -n 50
```

### Could not resolve host

**Cause :** Le pont réseau Docker n'est pas en place.

**Solution :** Relancez les 3 commandes `docker network create + connect` de l'étape 2.1.

### HTTP/1.1 401 Unauthorized

**Cause :** Token invalide ou littéralement `VOTRE_TOKEN` non remplacé.

**Solution :** Vérifiez le contenu du wrapper :
```bash
docker exec VOTRE_HERMES cat /opt/data/openclaw_bridge.sh
```
Si le token est vide ou incorrect, recréez le wrapper avec le bon token.

### Le bridge dit "OPENCLAW_API_KEY is empty"

**Cause :** Le wrapper shell n'a pas été créé correctement.

**Solution :** Recréez `/opt/data/openclaw_bridge.sh` avec votre vrai token.

### Config invalid au redémarrage d'OpenClaw

**Cause :** Un champ de config n'est pas reconnu par votre version d'OpenClaw.

**Solution :** Restaurez la sauvegarde :
```bash
docker exec VOTRE_OPENCLAW bash -c \
  'cp /data/.openclaw/openclaw.json.bak /data/.openclaw/openclaw.json'
docker restart VOTRE_OPENCLAW
```

---

## Commandes essentielles (antisèche)

### Diagnostic quotidien

```bash
# État du service socat
systemctl status openclaw-socat-bridge

# Logs récents
journalctl -u openclaw-socat-bridge --since "1 hour ago"

# Liste des serveurs MCP
docker exec VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes mcp list

# Test rapide de bout en bout
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Utilise openclaw:ask pour que Alex dise 'ping'."
```

### Intervention d'urgence

```bash
# Redémarrer le service socat
systemctl restart openclaw-socat-bridge

# Redémarrer Hermes (perd la session)
docker restart VOTRE_HERMES

# Redémarrer OpenClaw
docker restart VOTRE_OPENCLAW
# Puis attendre ~20s et tester
```

### Rotation du token

Si vous devez changer votre token :

```bash
# Dans un éditeur local, préparez la commande avec le nouveau token
docker exec VOTRE_HERMES bash -c '
cat > /opt/data/openclaw_bridge.sh << BASHEOF
#!/bin/bash
export OPENCLAW_API_KEY="NOUVEAU_TOKEN"
export OPENCLAW_BASE_URL="http://VOTRE_OPENCLAW:18790/v1"
export OPENCLAW_MODEL="openclaw/main"
exec /opt/hermes/.venv/bin/python3 /opt/data/openclaw_bridge.py
BASHEOF
chmod +x /opt/data/openclaw_bridge.sh'

# Test
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Utilise openclaw:ask pour que Alex dise 'ping'."
```

---

## Sécurité

### Gestion du token

- ✅ **Ne partagez jamais** votre token (screenshots, logs, chat)
- ✅ **Stockez-le** dans un gestionnaire de mots de passe
- ✅ **Régénérez-le** tous les 3-6 mois ou immédiatement en cas de doute
- ✅ **Limitez son exposition** : seul endroit = `openclaw_bridge.sh`

### Permissions fichiers

Restreignez l'accès au wrapper (root uniquement) :

```bash
docker exec VOTRE_HERMES chmod 700 /opt/data/openclaw_bridge.sh
```

### Monitoring

En production, surveillez :
- L'état du service `openclaw-socat-bridge`
- Les logs pour détecter des séries de `401 Unauthorized`
- Sauvegardez régulièrement `openclaw.json` et le service systemd

---

## Pour aller plus loin

### Créer des skills Hermes qui utilisent Alex automatiquement

Au lieu de taper manuellement `openclaw:ask`, créez un skill qui détecte les mots-clés ("rédige", "marketing", "copywriting") et délègue automatiquement.

### Étendre à plusieurs sous-agents

Répétez la même méthode pour connecter Hermes à d'autres agents spécialisés :
- **Dev-Agent** (génération de code)
- **Data-Agent** (analyse de données)
- **SEO-Agent** (audit SEO)
- **Research-Agent** (recherche web)

Hermes devient alors un **orchestrateur** qui route les demandes vers le bon expert.

### Améliorations techniques

- **Cache Redis** devant le bridge pour éviter de refacturer les mêmes prompts
- **Streaming (SSE)** pour voir les réponses d'Alex en temps réel
- **Telemetry (OpenTelemetry)** pour tracer les appels et mesurer les latences
- **Rate limiting** dans le bridge pour éviter les abus
- **Secrets manager** (Vault, AWS Secrets Manager) au lieu du token en clair

---

## Ressources

- **Spécification MCP :** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **SDK MCP Python :** [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- **Documentation socat :** [dest-unreach.org/socat](https://www.dest-unreach.org/socat/)
- **Guide systemd :** `man systemd.service`
- **Repo du projet :** [github.com/DrAzkalix/mon_ia_perso](https://github.com/DrAzkalix/mon_ia_perso)

---

**Guide version 1.0 — Avril 2026**  
Basé sur une installation réelle menée de zéro avec un apprenant débutant.
