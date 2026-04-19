# ✅ CHECKLIST DE DÉPLOIEMENT - IA PERSO (HERMÈS + OPENCLAW)

**Projet :** IA Perso - Création et documentation pour formation SaaS  
**Auteur :** DrAzkalix  
**Date création :** 2026-04-19  

---

## 📌 Comment utiliser cette checklist

- Coche les cases au fur et à mesure que tu complètes chaque tâche.
- Note les dates et durées réelles.
- Ajoute des notes si besoin.
- Plus tard, Hermès pourra lire cette checklist pour générer la formation.

---

## 🎯 SPRINT 1 : INFRASTRUCTURE VPS

### Tâche 1.1 : Accéder au KVM2 Hostinger

- [ ] Aller dans le panneau Hostinger
- [ ] Trouver les identifiants VPS KVM2
- [ ] Noter l'adresse IP du VPS
- [ ] Vérifier que le VPS est « en ligne »
- [ ] Tester un premier accès

**Date complétée :** ___________  
**Durée réelle :** ___________  
**Notes :** ______________________________________________________

---

### Tâche 1.2 : Configurer accès SSH / Terminal

- [ ] Télécharger un client SSH (PuTTY, MobaXterm, Terminal…)
- [ ] Entrer l'adresse IP du VPS
- [ ] Entrer le port SSH (généralement 22)
- [ ] Entrer les identifiants (root ou utilisateur)
- [ ] Accepter la clé SSH
- [ ] Première connexion réussie

**Date complétée :** ___________  
**Durée réelle :** ___________  
**Notes :** ______________________________________________________

---

### Tâche 1.3 : Tester la connexion

- [ ] Faire un `ping` au VPS
- [ ] Exécuter `uname -a`
- [ ] Exécuter `df -h`
- [ ] Vérifier que tout répond correctement
- [ ] Fermer et rouvrir la session SSH

**Date complétée :** ___________  
**Durée réelle :** ___________  
**Notes :** ______________________________________________________

---

### Tâche 1.4 : Configurer nom de domaine (OPTIONNEL)

- [ ] Aller dans les DNS Hostinger
- [ ] Ajouter un enregistrement A vers l'IP du VPS
- [ ] Attendre la propagation DNS
- [ ] Vérifier que le domaine pointe bien vers le VPS
- [ ] Tester l’accès via le domaine

**Date complétée :** ___________  
**Durée réelle :** ___________  
**Domaine utilisé :** ____________________________________________  
**Notes :** ______________________________________________________

---

## 🔧 SPRINT 2 : INSTALLATION HERMÈS

*(On remplira cette partie quand tu en seras là.)*

---

## 🤖 SPRINT 3 : OPENCLAW + INTÉGRATION

*(À compléter plus tard.)*

---

## 📚 SPRINT 4 : DOCUMENTATION & TEST

*(À compléter plus tard.)*

---

## 📊 Résumé de progression (à mettre à jour à la main)

| Sprint | Tâches | Complétées | % | Durée réelle |
|--------|--------|-----------|---|--------------|
| 1      | 4      | __        | __% | __h         |
| 2      | 4      | __        | __% | __h         |
| 3      | 4      | __        | __% | __h         |
| 4      | 4      | __        | __% | __h         |
| **TOTAL** | 16 | __        | __% | __h         |

---

**Version :** 1.0  
**Pour :** DrAzkalix (Alban)  
**Utilisé par :** Alban + Hermès (pour générer la formation)
