
Markdown View 
AA
moniaperso
Projet IA personnel — Infrastructure multi-agents (Hermes + OpenClaw) + journal de bord + future formation SaaS
[]() []()

📋 Table des matières
À propos
Architecture
Installation
Documentation
Journal de bord
Roadmap
Contribuer
Licence

À propos
Ce projet documente la construction d'une infrastructure multi-agents IA sur VPS Hostinger, permettant à un agent principal (Hermes) de collaborer avec des sous-agents spécialisés (OpenClaw, et bientôt d'autres).
Objectifs
Infrastructure de production — Agents IA communicants via le protocole MCP
Journal de formation — Documentation détaillée de chaque session d'apprentissage
Base pour un SaaS — Fondations pour une future plateforme de formation IA
Stack technique
Hermes Agent (ChatGPT Codex) — Agent principal
OpenClaw (Claude Sonnet 4.6) — Sous-agent spécialisé marketing
MCP (Model Context Protocol) — Communication inter-agents
Docker — Conteneurisation
systemd — Persistance et supervision
Python — Bridge MCP ↔ HTTP

Architecture
Vue d'ensemble
┌─────────────┐                ┌──────────────┐                ┌─────────────┐
│   HERMES    │─── MCP stdio ──│ Bridge Python│─── HTTP POST ──│  OPENCLAW   │
│  (Codex)    │                │  traducteur  │                │   (Alex)    │
└─────────────┘                └──────────────┘                └─────────────┘
       ↓                               ↓                               ↓
Container Docker            /opt/data/*.py + *.sh          Container Docker
hermes-agent-XXXX           Vars env: token, URL           openclaw-XXXX
       ↓                               ↓                               ↓
Réseau bridge partagé ────────────────┼────────────────────────────────┘
(hermes-openclaw-bridge)              │
                                      ↓
                            socat (relais TCP)
                         Port 18790 → 18789 (loopback)
                                      ↓
                         systemd service (persistance)
Composants
Composant
Rôle
Technologie
Hermes
Agent principal qui reçoit les demandes utilisateur
ChatGPT Codex (conteneur Docker)
OpenClaw
Sous-agent spécialisé marketing (Alex)
Claude Sonnet 4.6 (conteneur Docker)
Bridge MCP
Traduit MCP (stdio) ↔ HTTP OpenAI-compatible
Python (mcp SDK + httpx)
socat
Relais TCP pour exposer OpenClaw sur le réseau
Installé via Homebrew dans OpenClaw
systemd
Gardien qui relance socat automatiquement
Service systemd sur l'hôte VPS
Réseau Docker
Pont réseau partagé entre les conteneurs
hermes-openclaw-bridge

Installation
Prérequis
VPS Hostinger avec Docker Manager
Hermes Agent et OpenClaw déjà installés via le panel
Token Gateway OpenClaw (bouton "Jeton de passerelle")
Accès SSH root au VPS
Guide complet
Consultez le Guide d'installation complet pour une procédure pas à pas détaillée (6 étapes, ~2h30).
Installation rapide (pour experts)
# 1. Créer le réseau partagé
docker network create hermes-openclaw-bridge
docker network connect hermes-openclaw-bridge VOTRE_OPENCLAW
docker network connect hermes-openclaw-bridge VOTRE_HERMES

# 2. Installer socat dans OpenClaw
docker exec -it VOTRE_OPENCLAW bash
brew install socat
exit

# 3. Installer le SDK MCP dans Hermes
docker exec VOTRE_HERMES uv pip install --python /opt/hermes/.venv/bin/python3 mcp

# 4. Créer le bridge Python et le wrapper shell
# (Voir guide complet pour les scripts)

# 5. Déclarer le serveur MCP
echo "Y" | docker exec -i VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes mcp add openclaw \
  --command /opt/data/openclaw_bridge.sh

# 6. Créer le service systemd
# (Voir guide complet pour le fichier de service)
systemctl daemon-reload
systemctl enable openclaw-socat-bridge.service
systemctl start openclaw-socat-bridge.service
Test rapide
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Utilise openclaw:ask pour demander à Alex : 'ping'."
Résultat attendu : Alex répond "Pong" 🏓

Documentation
Guides disponibles
Guide d'installation complet (Markdown, ~8000 mots)
PDF de formation (27 pages, technique + pédagogique)
Structure de la documentation
docs/
├── guide-installation-hermes-openclaw.md   # Guide markdown pour GitHub
├── hermes-openclaw-guide-complet.pdf       # PDF de formation complet
└── images/                                 # Schémas d'architecture (à venir)
Scripts et fichiers
Tous les scripts nécessaires sont documentés dans le guide. Fichiers clés :
openclaw_bridge.py — Bridge Python MCP ↔ HTTP
openclaw_bridge.sh — Wrapper shell avec variables d'environnement
openclaw-socat-bridge.service — Service systemd pour la persistance

Journal de bord
Le dossier journal/ contient les sessions d'apprentissage chronologiques :
Date
Sujet
Durée
Fichier
2026-04-22
Installation complète Hermes ↔ OpenClaw via MCP
3h30
2026-04-22-installation-hermes-openclaw-mcp.md
Chaque journal contient :
Objectifs de la session
Étapes réalisées avec temps passé
Points d'accrochage rencontrés et solutions
Apprentissages techniques et pédagogiques
Prochaines étapes envisagées

Roadmap
✅ Phase 1 — Infrastructure de base (Complété)
[x] Installation Hermes + OpenClaw sur VPS
[x] Connexion via MCP avec bridge Python custom
[x] Persistance via systemd
[x] Tests de délégation (ping, haïku, auto-présentation)
[x] Documentation complète (guide + PDF)
🚧 Phase 2 — Optimisation (En cours)
[ ] Créer des skills Hermes qui délèguent automatiquement à Alex
[ ] Ajouter un cache Redis pour éviter de refacturer les mêmes prompts
[ ] Implémenter du streaming (SSE) pour voir les réponses en temps réel
[ ] Instrumenter avec OpenTelemetry pour mesurer les latences
📅 Phase 3 — Extension multi-agents
[ ] Ajouter un agent Code (génération et review)
[ ] Ajouter un agent Data (analyse, SQL, visualisation)
[ ] Ajouter un agent SEO (audit, plan éditorial)
[ ] Créer un orchestrateur intelligent (routage automatique)
🎓 Phase 4 — Formation SaaS
[ ] Créer un module de formation "Architecture multi-agents IA"
[ ] Interface Telegram pour interagir avec Hermes
[ ] Packager le bridge MCP comme module PyPI réutilisable
[ ] Plateforme de formation avec suivi de progression

Contribuer
Les contributions sont les bienvenues ! Voici comment participer :
Signaler un bug
Ouvrez une issue avec :
Description du problème
Étapes pour reproduire
Logs d'erreur (si applicable)
Environnement (VPS, version Docker, etc.)
Proposer une amélioration
Forkez le repo
Créez une branche pour votre feature (git checkout -b feature/amelioration)
Commitez vos changements (git commit -am 'Ajout de X')
Pushez vers la branche (git push origin feature/amelioration)
Ouvrez une Pull Request
Ajouter une entrée au journal
Si vous avez reproduit l'installation ou ajouté une fonctionnalité, partagez votre expérience :
Créez un fichier journal/YYYY-MM-DD-titre-session.md
Suivez le format du journal existant
Ouvrez une Pull Request

Ressources
Liens utiles
Spécification MCP : modelcontextprotocol.io
SDK MCP Python : github.com/modelcontextprotocol/python-sdk
Documentation socat : dest-unreach.org/socat
Hermes Agent : Documentation officielle
Communauté
Discussions : GitHub Discussions
Issues : GitHub Issues

Licence
Ce projet est sous licence MIT — voir le fichier LICENSE pour plus de détails.
Vous êtes libre de :
✅ Utiliser le code à des fins personnelles ou commerciales
✅ Modifier et adapter le code
✅ Distribuer le code original ou modifié
À condition de :
⚖️ Inclure la notice de copyright et de licence
📄 Mentionner les modifications apportées

Auteur
Dr. FIRAS (DrAzkalix)
PhD en IA • Formateur Udemy • Créateur YouTube
GitHub: @DrAzkalix
Projet formation : hermes-skills-autopilot

Remerciements
Anthropic pour Claude et le protocole MCP
OpenAI pour l'API compatible utilisée par OpenClaw
Hostinger pour la plateforme VPS avec Docker Manager
La communauté MCP pour les ressources et exemples

Dernière mise à jour : Avril 2026
Version : 1.0.0
Statut : Infrastructure opérationnelle ✅
