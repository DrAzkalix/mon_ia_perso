# Installation — Hermes ↔ OpenClaw via MCP

## Prérequis
- Un VPS Hostinger KVM2
- Docker Manager actif
- Un conteneur Hermes
- Un conteneur OpenClaw
- Un accès SSH root au VPS
- Le token Gateway OpenClaw

## Étape 1 — Identifier les conteneurs
Lancer sur l’hôte VPS :

```bash
docker ps
```

Noter les noms exacts de :
- `VOTRE_HERMES`
- `VOTRE_OPENCLAW`

## Étape 2 — Activer l’endpoint HTTP d’OpenClaw
Entrer dans le conteneur OpenClaw :

```bash
docker exec -it VOTRE_OPENCLAW bash
```

Sauvegarder la configuration :

```bash
cp /data/.openclaw/openclaw.json /data/.openclaw/openclaw.json.bak
```

Modifier la configuration avec `jq` pour activer l’endpoint HTTP.

## Étape 3 — Redémarrer OpenClaw
Depuis l’hôte VPS :

```bash
docker restart VOTRE_OPENCLAW
docker logs --tail 20 VOTRE_OPENCLAW
```

## Étape 4 — Créer le réseau Docker partagé
Depuis l’hôte VPS :

```bash
docker network create hermes-openclaw-bridge
docker network connect hermes-openclaw-bridge VOTRE_OPENCLAW
docker network connect hermes-openclaw-bridge VOTRE_HERMES
```

## Étape 5 — Installer et lancer socat
Entrer dans OpenClaw :

```bash
docker exec -it VOTRE_OPENCLAW bash
brew install socat
```

Lancer socat :

```bash
socat -d TCP-LISTEN:18790,bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:18789 &
```

## Étape 6 — Installer le SDK MCP dans Hermes
Depuis l’hôte VPS :

```bash
docker exec VOTRE_HERMES uv pip install --python /opt/hermes/.venv/bin/python3 mcp
```

## Étape 7 — Ajouter les scripts
Ajouter dans le repo ou dans le conteneur Hermes :
- `scripts/openclaw_bridge.py`
- `scripts/openclaw_bridge.sh.example`

Créer ensuite la vraie version locale de `openclaw_bridge.sh` avec le vrai token, sans la publier sur GitHub.

## Étape 8 — Déclarer le bridge MCP dans Hermes
Depuis l’hôte VPS :

```bash
echo "Y" | docker exec -i VOTRE_HERMES /opt/hermes/.venv/bin/hermes mcp add openclaw --command /opt/data/openclaw_bridge.sh
```

Vérifier :

```bash
docker exec VOTRE_HERMES /opt/hermes/.venv/bin/hermes mcp list
```

## Étape 9 — Tester
Exemple de test :

```bash
docker exec -it VOTRE_HERMES /opt/hermes/.venv/bin/hermes chat -Q -q "Utilise le tool openclaw:ask pour demander a Alex : ping"
```

## Étape 10 — Persistance
Utiliser le fichier :

- `système/openclaw-socat-bridge.service.example`

puis l’adapter avec les vrais noms de conteneurs avant installation sur le VPS.

## Sécurité
- Ne jamais publier le vrai token
- Ne jamais publier les clés API
- Garder le vrai `openclaw_bridge.sh` hors GitHub
