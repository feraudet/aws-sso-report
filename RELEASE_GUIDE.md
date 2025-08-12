# 🚀 Guide de Release et Conventional Commits

Ce guide explique comment utiliser le système de release automatique et les conventions de commit mises en place dans ce projet.

## 📋 Table des matières

- [Format des messages de commit](#format-des-messages-de-commit)
- [Création d'une release](#création-dune-release)
- [Workflows GitHub Actions](#workflows-github-actions)
- [Tests locaux avec act](#tests-locaux-avec-act)
- [Dépannage](#dépannage)

## 📝 Format des messages de commit

Ce projet utilise les **Conventional Commits** pour standardiser les messages de commit et automatiser la génération du changelog.

### Format de base

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types de commit disponibles

| Type | Description | Exemple |
|------|-------------|---------|
| `feat` | ✨ Nouvelle fonctionnalité | `feat: add user authentication` |
| `fix` | 🐛 Correction de bug | `fix: resolve login timeout issue` |
| `docs` | 📚 Documentation | `docs: update API documentation` |
| `style` | 🎨 Formatage, style | `style: fix code formatting` |
| `refactor` | ♻️ Refactoring | `refactor: simplify data processing` |
| `perf` | ⚡ Performance | `perf: optimize database queries` |
| `test` | 🧪 Tests | `test: add unit tests for auth module` |
| `chore` | 🔧 Maintenance | `chore: update dependencies` |
| `ci` | 👷 CI/CD | `ci: add automated testing` |
| `build` | 📦 Build system | `build: update webpack config` |
| `revert` | ⏪ Annulation | `revert: undo previous commit` |

### Exemples de commits valides

```bash
# Nouvelle fonctionnalité
feat: add CSV export functionality

# Correction de bug avec scope
fix(auth): resolve token expiration handling

# Breaking change
feat!: change API response format

BREAKING CHANGE: The API now returns data in a different format
```

### Validation automatique

Les messages de commit sont automatiquement validés par :
- **Pre-commit hook** : Validation locale avant le commit
- **GitHub Actions** : Validation sur les pull requests

## 🎯 Création d'une release

### Méthode automatique (recommandée)

Utilisez le script fourni pour créer une release :

```bash
# Correction de bug (1.0.0 -> 1.0.1)
./scripts/release.sh patch

# Nouvelle fonctionnalité (1.0.0 -> 1.1.0)
./scripts/release.sh minor

# Changement majeur (1.0.0 -> 2.0.0)
./scripts/release.sh major
```

Le script automatise :
- ✅ Vérification de l'état du repository
- ✅ Incrémentation de la version
- ✅ Mise à jour des fichiers de version
- ✅ Génération du changelog
- ✅ Création du commit et du tag
- ✅ Push vers GitHub

### Méthode manuelle

Si vous préférez créer une release manuellement :

```bash
# 1. Mettre à jour la version dans pyproject.toml et src/__version__.py
# 2. Générer le changelog
git-cliff --tag v1.0.0 --output CHANGELOG.md

# 3. Commiter les changements
git add .
git commit -m "chore(release): prepare for v1.0.0"

# 4. Créer le tag
git tag -a v1.0.0 -m "Release v1.0.0"

# 5. Pousser vers GitHub
git push origin main
git push origin v1.0.0
```

## 🤖 Workflows GitHub Actions

### 1. Workflow de qualité du code (`python.yml`)

**Déclencheurs :**
- Push sur `main` ou `develop`
- Pull requests vers `main` ou `develop`

**Actions :**
- ✅ Installation des dépendances
- ✅ Exécution des hooks pre-commit
- ✅ Vérification du formatage (Black, isort)
- ✅ Analyse statique (flake8, bandit, mypy)
- ✅ Tests fonctionnels

### 2. Workflow de validation des commits (`commit-validation.yml`)

**Déclencheurs :**
- Pull requests

**Actions :**
- ✅ Validation des messages de commit
- ✅ Aperçu de la prochaine version
- ✅ Dry-run de semantic-release

### 3. Workflow de release (`release.yml`)

**Déclencheurs :**
- Tags de version (`v*.*.*`)
- Déclenchement manuel

**Actions :**
- ✅ Génération du changelog
- ✅ Mise à jour des fichiers de version
- ✅ Création des packages de distribution
- ✅ Création de la release GitHub
- ✅ Upload des artifacts

## 🧪 Tests locaux avec act

### Installation et configuration

```bash
# Installation (déjà fait)
brew install act

# Test du workflow de qualité
act --container-architecture linux/amd64 -j quality-checks

# Test du workflow de validation des commits
act pull_request --container-architecture linux/amd64

# Test du workflow de release (simulation)
act --container-architecture linux/amd64 -e .github/workflows/release.yml
```

### Variables d'environnement pour les tests

Créez un fichier `.env` pour les tests locaux :

```bash
# .env (ne pas commiter)
GITHUB_TOKEN=your_github_token_here
```

## 🔧 Configuration des hooks pre-commit

### Installation

```bash
# Installation des hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Test des hooks
pre-commit run --all-files
```

### Hooks configurés

- ✅ **trailing-whitespace** : Supprime les espaces en fin de ligne
- ✅ **end-of-file-fixer** : Assure une ligne vide en fin de fichier
- ✅ **check-yaml** : Valide la syntaxe YAML
- ✅ **requirements-txt-fixer** : Trie requirements.txt
- ✅ **black** : Formatage du code Python
- ✅ **isort** : Tri des imports
- ✅ **flake8** : Analyse statique
- ✅ **bandit** : Analyse de sécurité
- ✅ **conventional-pre-commit** : Validation des messages de commit

## 🚨 Dépannage

### Problèmes courants

#### 1. Message de commit rejeté

```bash
# Erreur
conventional-pre-commit..............................Failed

# Solution : Utiliser le format correct
git commit -m "feat: add new feature description"
```

#### 2. Hooks pre-commit échouent

```bash
# Corriger automatiquement les problèmes de formatage
pre-commit run --all-files

# Puis recommiter
git add .
git commit -m "style: fix formatting issues"
```

#### 3. Workflow de release échoue

- Vérifiez que le tag suit le format `v*.*.*`
- Assurez-vous que `GITHUB_TOKEN` a les permissions nécessaires
- Vérifiez que git-cliff est disponible

#### 4. Tests act échouent

```bash
# Vérifier que Docker est démarré
docker info

# Utiliser l'architecture correcte sur Mac M1/M2
act --container-architecture linux/amd64
```

### Commandes utiles

```bash
# Voir l'historique des releases
git tag -l

# Voir les commits depuis la dernière release
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Générer un changelog pour une version spécifique
git-cliff --tag v1.0.0

# Tester un commit message
echo "feat: test message" | npx commitlint
```

## 📚 Ressources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [git-cliff Documentation](https://git-cliff.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [act Documentation](https://github.com/nektos/act)
