# Testing Guide

Ce guide explique comment tester la qualité du code et valider l'environnement de développement pour le projet AWS SSO Report.

## Scripts de Test Disponibles

### 🚀 Test Rapide - `scripts/quick-test.sh`

Script léger pour les tests quotidiens :

```bash
./scripts/quick-test.sh
```

**Ce qu'il fait :**
- Active l'environnement virtuel Python
- Lance tous les pre-commit hooks
- Affiche un résumé des résultats

**Utilisation recommandée :** Avant chaque commit

### 🔍 Test Complet - `scripts/test-quality.sh`

Script complet pour validation complète :

```bash
./scripts/test-quality.sh
```

**Ce qu'il fait :**
- ✅ Vérifie et active l'environnement virtuel Python
- ✅ Contrôle que Docker est lancé
- ✅ Installe et lance tous les pre-commit hooks
- ✅ Teste les GitHub Actions avec `act`
- ✅ Effectue un test d'import des modules Python
- ✅ Fournit un rapport détaillé avec couleurs

**Utilisation recommandée :** Avant les pull requests, après des changements majeurs

## Prérequis

### Environnement Python
```bash
# Créer l'environnement virtuel (si pas déjà fait)
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Docker
- **macOS :** Docker Desktop doit être lancé
- **Linux :** `sudo systemctl start docker`

### Act (pour les tests GitHub Actions)
```bash
# macOS avec Homebrew
brew install act

# Ou suivre les instructions : https://github.com/nektos/act#installation
```

## Tests Manuels

### Pre-commit Hooks Seulement
```bash
source venv/bin/activate
pre-commit run --all-files
```

### GitHub Actions Localement
```bash
# Test complet
act -j quality-checks --container-architecture linux/amd64

# Test avec plus de détails
act -j quality-checks --container-architecture linux/amd64 --verbose
```

### Tests Python
```bash
source venv/bin/activate
python -m pytest tests/
```

## Résolution des Problèmes Courants

### ❌ "Docker is not running"
**Solution :** Lancer Docker Desktop (macOS) ou `sudo systemctl start docker` (Linux)

### ❌ "pre-commit not found"
**Solution :**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ "act: command not found"
**Solution :**
```bash
brew install act  # macOS
# Ou installer manuellement depuis GitHub
```

### ❌ Échecs de pre-commit hooks
**Solution :** Les hooks corrigent souvent automatiquement les problèmes. Relancer :
```bash
pre-commit run --all-files
```

### ❌ Trailing whitespace
**Solution :**
```bash
pre-commit run trailing-whitespace --all-files
```

### ❌ Black formatting
**Solution :**
```bash
pre-commit run black --all-files
```

## Intégration Continue

Les mêmes vérifications sont exécutées automatiquement sur GitHub Actions :

- **Pre-commit hooks** : trailing whitespace, YAML validation, etc.
- **Code formatting** : Black, isort
- **Linting** : flake8
- **Security** : bandit
- **Tests** : pytest

## Workflow de Développement Recommandé

1. **Développement quotidien :**
   ```bash
   ./scripts/quick-test.sh
   ```

2. **Avant un commit important :**
   ```bash
   ./scripts/test-quality.sh
   ```

3. **Avant une pull request :**
   ```bash
   ./scripts/test-quality.sh
   git add .
   git commit -m "feat: your changes"
   ```

## Structure des Tests

```
scripts/
├── test-quality.sh     # Test complet avec Docker et act
├── quick-test.sh       # Test rapide pre-commit seulement
tests/
├── test_*.py          # Tests unitaires Python
.github/workflows/
├── quality-checks.yml # CI/CD GitHub Actions
.pre-commit-config.yaml # Configuration des hooks
```

## Métriques de Qualité

Le projet maintient les standards suivants :
- ✅ **Couverture de code** : Tests unitaires avec pytest
- ✅ **Formatage** : Black + isort
- ✅ **Linting** : flake8 avec règles strictes
- ✅ **Sécurité** : bandit pour l'analyse de sécurité
- ✅ **Documentation** : Docstrings et type hints
- ✅ **Git** : Conventional commits + pre-commit hooks
