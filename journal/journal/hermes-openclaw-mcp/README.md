# Hermes ↔ OpenClaw via MCP

Documentation de mon installation et de mes tests réalisés sur VPS Hostinger KVM2.

## Objectif
Connecter Hermes (agent principal) à OpenClaw (sous-agent) via MCP afin de permettre la délégation de tâches entre agents.

## Infrastructure utilisée
- VPS Hostinger KVM2
- Docker Manager
- Conteneur Hermes
- Conteneur OpenClaw
- Bridge Python MCP → HTTP
- Service systemd pour socat

## Contenu de ce dossier
- `README.md` : résumé rapide du projet
- `GUIDE_COMPLET.md` : guide détaillé d’installation
- `scripts/` : scripts utiles
- `systemd/` : service de persistance
- `templates/` : fichiers modèles de configuration

## Important
Ne jamais versionner :
- les vrais tokens
- les clés API
- les mots de passe
- les fichiers `.env` réels

## Statut
Installation documentée à partir d’un cas réel avec erreurs, diagnostics et corrections.
