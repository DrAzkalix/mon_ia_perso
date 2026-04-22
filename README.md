moniaperso
🤖 Infrastructure multi-agents IA — Hermes + OpenClaw + journal de bord + future formation SaaS
   

📋 Table des matières
À propos
Architecture
Installation
Documentation
Journal de bord
Roadmap
Contribuer
Ressources
Licence

🎯 À propos
Ce projet documente la construction d'une infrastructure multi-agents IA sur VPS Hostinger, permettant à un agent principal (Hermes) de collaborer avec des sous-agents spécialisés (OpenClaw, et bientôt d'autres).
Objectifs
🏗️ Infrastructure de production — Agents IA communicants via le protocole MCP
📓 Journal de formation — Documentation détaillée de chaque session d'apprentissage
🎓 Base pour un SaaS — Fondations pour une future plateforme de formation IA
Stack technique
Composant
Rôle
Technologie
Hermes Agent
Agent principal
ChatGPT Codex
OpenClaw (Alex)
Sous-agent spécialisé marketing
Claude Sonnet 4.6
MCP
Protocole inter-agents
Model Context Protocol
Docker
Conteneurisation
Docker + Docker Compose
systemd
Persistance et supervision
systemd services
Bridge Python
Traducteur MCP ↔ HTTP
Python 3.11 + mcp SDK

🏗️ Architecture
Vue d'ensemble
┌─────────────┐                ┌──────────────┐                ┌─────────────┐
│   HERMES    │─── MCP stdio ──│ Bridge Python│─── HTTP POST ──│  OPENCLAW   │
│  (Codex)    │                │  traducteur  │                │   (Alex)    │
└─────────────┘                └──────────────┘                └─────────────┘
       │                              │                               │
       ▼                              ▼                               ▼
Container Docker            /opt/data/*.py + *.sh          Container Docker
hermes-agent-XXXX           Vars env: token, URL            openclaw-XXXX
       │                                                            │
       └──────────────── hermes-openclaw-bridge ────────────────────┘
                           (réseau Docker partagé)
                                      │
                                      ▼
                            socat (relais TCP)
                         Port 18790 → 18789 (loopback)
                                      │
                                      ▼
                         systemd service (persistance 24/7)
Composants détaillés
Composant
Rôle
Emplacement
Hermes
Reçoit les demandes utilisateur, utilise MCP
Container hermes-agent-XXXX
Bridge Python
Traduit MCP (stdio) ↔ HTTP OpenAI-compatible
/opt/data/openclaw_bridge.py
Wrapper Shell
Injecte les variables d'environnement
/opt/data/openclaw_bridge.sh
socat
Relais TCP (18790 public → 18789 loopback)
Installé via brew dans OpenClaw
OpenClaw (Alex)
Sous-agent spécialisé
Container openclaw-XXXX
systemd
Gardien qui relance socat en cas de crash
/etc/systemd/system/
Flux d'une requête
1. L'utilisateur écrit à Hermes
2. Hermes décide d'utiliser openclaw:ask ou openclaw:delegate
3. Hermes lance le bridge Python via MCP stdio
4. Le bridge fait un POST HTTP vers VOTRE_OPENCLAW:18790
5. socat relaie vers le port 18789 (loopback OpenClaw)
6. Alex (OpenClaw) traite et répond
7. La réponse remonte par le chemin inverse
8. L'utilisateur reçoit la réponse

🚀 Installation
Prérequis
✅ VPS Hostinger avec Docker Manager activé
✅ Hermes Agent et OpenClaw installés via le panel
✅ Token Gateway OpenClaw (bouton "Jeton de passerelle")
✅ Accès SSH root au VPS
📖 Guide complet
Consulte le Guide d'installation complet pour une procédure pas à pas détaillée (6 étapes, ~2h30).
Un PDF de formation (27 pages, technique + pédagogique) est également disponible.
⚡ Installation rapide (pour experts)
⚠️ Remplace VOTRE_HERMES, VOTRE_OPENCLAW et VOTRE_TOKEN par tes valeurs réelles.
1. Créer le réseau Docker partagé
docker network create hermes-openclaw-bridge
docker network connect hermes-openclaw-bridge VOTRE_OPENCLAW
docker network connect hermes-openclaw-bridge VOTRE_HERMES
2. Activer l'endpoint HTTP d'OpenClaw
docker exec -it VOTRE_OPENCLAW bash
cp /data/.openclaw/openclaw.json /data/.openclaw/openclaw.json.bak
cd /data/.openclaw && jq '.gateway.bind = "custom" |
    .gateway.customBindHost = "0.0.0.0" |
    .gateway.http.endpoints.chatCompletions.enabled = true' \
  openclaw.json > openclaw.json.new && mv openclaw.json.new openclaw.json
exit
docker restart VOTRE_OPENCLAW
3. Installer socat dans OpenClaw
docker exec -it VOTRE_OPENCLAW bash
brew install socat   # Patience : 5-10 min (compilation openssl)
exit
4. Installer le SDK MCP dans Hermes
docker exec VOTRE_HERMES \
  uv pip install --python /opt/hermes/.venv/bin/python3 mcp
5. Créer le bridge Python et le wrapper shell
Voir le guide complet pour les scripts détaillés.
6. Déclarer le serveur MCP dans Hermes
echo "Y" | docker exec -i VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes mcp add openclaw \
  --command /opt/data/openclaw_bridge.sh
7. Créer le service systemd (persistance)
systemctl daemon-reload
systemctl enable openclaw-socat-bridge.service
systemctl start openclaw-socat-bridge.service
systemctl status openclaw-socat-bridge.service
🧪 Test rapide
docker exec -it VOTRE_HERMES \
  /opt/hermes/.venv/bin/hermes chat -Q \
  -q "Utilise openclaw:ask pour demander a Alex : 'ping'."
Résultat attendu : Alex répond Pong 🏓

📚 Documentation
Guides disponibles
Fichier
Format
Taille
Description
Guide complet
Markdown
~17 KB
Guide technique pour GitHub
PDF de formation
PDF
27 pages
Support de formation complet
Structure du projet
mon_ia_perso/
│
├── README.md                                      # Ce fichier
│
├── documents/                                     # Documentation technique
│   ├── guide-installation-hermes-openclaw.md     # Guide markdown
│   └── guide complet d'Hermes OpenClaw.pdf       # PDF formation (27 pages)
│
└── journal/                                       # Journal de bord chronologique
    ├── CARNET_BORD_TEMPLATE.md                   # Template de journal
    ├── LISTE DE CONTROLE_DEPLOIEMENT.md          # Checklist
    └── hermes-openclaw-mcp/                      # Session du 22 avril 2026
        └── 2026-04-22-installation...md
Scripts clés (documentés dans le guide)
openclaw_bridge.py — Bridge Python MCP ↔ HTTP (~1760 octets)
openclaw_bridge.sh — Wrapper shell avec env vars (~220 octets)
openclaw-socat-bridge.service — Service systemd (~675 octets)

📓 Journal de bord
Le dossier journal/ contient les sessions d'apprentissage chronologiques.
Date
Sujet
Durée
Statut
2026-04-22
Installation complète Hermes ↔ OpenClaw via MCP
3h30
✅ Complété
Format de chaque journal
Chaque entrée contient :
🎯 Objectifs de la session
📝 Étapes réalisées avec temps passé
⚠️ Points d'accrochage rencontrés et solutions
💡 Apprentissages techniques et pédagogiques
🚀 Prochaines étapes envisagées

🗺️ Roadmap
✅ Phase 1 — Infrastructure de base (Complété)
[x] Installation Hermes + OpenClaw sur VPS Hostinger
[x] Connexion via MCP avec bridge Python custom
[x] Persistance via systemd (relance automatique)
[x] Tests de délégation validés (ping, haïku, auto-présentation)
[x] Documentation complète (guide markdown + PDF 27 pages)
[x] Repo GitHub public avec README professionnel
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

🤝 Contribuer
Les contributions sont les bienvenues !
Signaler un bug
Ouvre une issue avec :
Description du problème
Étapes pour reproduire
Logs d'erreur (si applicable)
Environnement (VPS, version Docker, etc.)
Proposer une amélioration
# 1. Fork le repo
# 2. Créer une branche
git checkout -b feature/amelioration

# 3. Commiter les changements
git commit -am "Ajout de X"

# 4. Pusher la branche
git push origin feature/amelioration

# 5. Ouvrir une Pull Request
Ajouter une entrée au journal
Si tu as reproduit l'installation ou ajouté une fonctionnalité :
Crée un fichier journal/YYYY-MM-DD-titre-session.md
Suis le format du journal existant
Ouvre une Pull Request

📖 Ressources
Documentation officielle
🔗 Spécification MCP : modelcontextprotocol.io
🔗 SDK MCP Python : github.com/modelcontextprotocol/python-sdk
🔗 Documentation socat : dest-unreach.org/socat
🔗 Anthropic Claude : docs.anthropic.com
Projets liés
🔗 hermes-skills-autopilot : github.com/DrFIRASS/hermes-skills-autopilot

📄 Licence
Ce projet est sous licence MIT — voir le fichier LICENSE pour plus de détails.
Tu es libre de :
✅ Utiliser le code à des fins personnelles ou commerciales
✅ Modifier et adapter le code
✅ Distribuer le code original ou modifié
À condition de :
⚖️ Inclure la notice de copyright et de licence
📝 Mentionner les modifications apportées

👤 Auteur
Dr. Azkalix
🔗 GitHub : @DrAzkalix

🙏 Remerciements
Anthropic pour Claude et le protocole MCP
OpenAI pour l'API compatible utilisée par OpenClaw
Hostinger pour la plateforme VPS avec Docker Manager
La communauté MCP pour les ressources et exemples

**Dernière mise à jour :** Avril 2026 · **Version :** 1.0.0 · **Statut :** ✅ Opérationnel ⭐ **Si ce projet te plaît, n'hésite pas à lui mettre une étoile !** ⭐ 
