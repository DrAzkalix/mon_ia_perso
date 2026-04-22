# Guide complet — Hermes ↔ OpenClaw via MCP

## But
Ce dossier documente une installation réelle permettant de connecter Hermes à OpenClaw via MCP sur un VPS Hostinger KVM2.

## Objectif technique
Permettre à Hermes, agent principal, de déléguer certaines tâches à OpenClaw, sous-agent spécialisé, à travers un bridge MCP vers HTTP.

## Architecture
- Hermes = agent principal
- OpenClaw = sous-agent
- Bridge Python = traduction MCP vers HTTP
- socat = relais TCP
- systemd = persistance du bridge au redémarrage

## Infrastructure
- VPS Hostinger KVM2
- Docker Manager
- Conteneur Hermes
- Conteneur OpenClaw

## Grandes étapes
1. Activer l’endpoint HTTP d’OpenClaw
2. Créer un réseau Docker partagé entre Hermes et OpenClaw
3. Installer et tester socat
4. Installer le SDK MCP dans Hermes
5. Créer le bridge Python
6. Créer le wrapper shell
7. Déclarer le bridge dans Hermes
8. Tester la délégation
9. Mettre en place la persistance avec systemd

## Points de vigilance
- Ne jamais publier les vrais tokens
- Ne jamais publier les vraies clés API
- Toujours utiliser des fichiers `.example` pour GitHub
- Toujours tester la connectivité avant de déclarer le MCP

## Fichiers associés
- `scripts/openclaw_bridge.py`
- `scripts/openclaw_bridge.sh.example`
- `systemd/openclaw-socat-bridge.service.example`

## Source
Documentation rédigée à partir d’une installation réelle et d’un guide PDF de travail.
