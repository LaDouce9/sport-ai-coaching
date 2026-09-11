---
name: test-skill
description: À activer lorsque l'utilisateur teste les skills ou demande une traduction.
---

# Test Skill

Ce skill sert à valider le chargement et l'activation automatique des skills par l'agent.

## Comportement obligatoire

Dès que ce skill est actif :

1. **Préfixe visuel obligatoire** : Débuter obligatoirement la réponse par la bannière suivante :
   `🧪 [TEST-SKILL ACTIF]`
2. **Signature de fin** : Terminer la réponse par la ligne :
   `✅ Fin de transmission du test-skill`

