#!/bin/bash

# Script pour créer une nouvelle release
# Usage: ./scripts/release.sh [patch|minor|major]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "Usage: $0 [patch|minor|major]"
    echo ""
    echo "Ce script automatise la création d'une nouvelle release:"
    echo "  - Vérifie que le repository est propre"
    echo "  - Incrémente la version selon le type spécifié"
    echo "  - Met à jour les fichiers de version"
    echo "  - Crée un commit et un tag"
    echo "  - Pousse vers le repository distant"
    echo ""
    echo "Types de version:"
    echo "  patch  - Correction de bugs (1.0.0 -> 1.0.1)"
    echo "  minor  - Nouvelles fonctionnalités (1.0.0 -> 1.1.0)"
    echo "  major  - Breaking changes (1.0.0 -> 2.0.0)"
    echo ""
    echo "Exemples:"
    echo "  $0 patch   # Pour une correction de bug"
    echo "  $0 minor   # Pour une nouvelle fonctionnalité"
    echo "  $0 major   # Pour un changement majeur"
}

# Vérifier les arguments
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

VERSION_TYPE=$1

if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo -e "${RED}❌ Type de version invalide: $VERSION_TYPE${NC}"
    echo -e "${YELLOW}Types valides: patch, minor, major${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Création d'une nouvelle release ($VERSION_TYPE)${NC}"

# Vérifier que nous sommes sur la branche main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ Vous devez être sur la branche 'main' pour créer une release${NC}"
    echo -e "${YELLOW}Branche actuelle: $CURRENT_BRANCH${NC}"
    exit 1
fi

# Vérifier que le repository est propre
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Le repository contient des modifications non commitées${NC}"
    echo -e "${YELLOW}Veuillez commiter ou stasher vos modifications avant de continuer${NC}"
    git status --short
    exit 1
fi

# Récupérer les dernières modifications
echo -e "${BLUE}📥 Récupération des dernières modifications...${NC}"
git fetch origin main
git pull origin main

# Lire la version actuelle
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}❌ Impossible de lire la version actuelle depuis pyproject.toml${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Version actuelle: $CURRENT_VERSION${NC}"

# Calculer la nouvelle version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

case $VERSION_TYPE in
    "patch")
        PATCH=$((PATCH + 1))
        ;;
    "minor")
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    "major")
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
NEW_TAG="v$NEW_VERSION"

echo -e "${GREEN}🎯 Nouvelle version: $NEW_VERSION${NC}"

# Demander confirmation
echo -e "${YELLOW}⚠️  Êtes-vous sûr de vouloir créer la release $NEW_TAG? (y/N)${NC}"
read -r CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Release annulée${NC}"
    exit 0
fi

# Mettre à jour les fichiers de version
echo -e "${BLUE}📝 Mise à jour des fichiers de version...${NC}"

# Mettre à jour pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml && rm pyproject.toml.bak

# Mettre à jour src/__version__.py
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/__version__.py && rm src/__version__.py.bak

# Vérifier que les modifications ont été appliquées
echo -e "${BLUE}✅ Vérification des modifications:${NC}"
echo -e "  pyproject.toml: $(grep -E '^version = ' pyproject.toml)"
echo -e "  __version__.py: $(grep -E '^__version__ = ' src/__version__.py)"

# Générer le changelog pour cette version
echo -e "${BLUE}📚 Generating changelog...${NC}"
if command -v git-cliff &> /dev/null; then
    git-cliff --tag "$NEW_TAG" --output CHANGELOG.md
    echo -e "${GREEN}✅ Changelog généré dans CHANGELOG.md${NC}"
else
    echo -e "${YELLOW}⚠️  git-cliff n'est pas installé, changelog non généré${NC}"
fi

# Créer le commit de release
echo -e "${BLUE}💾 Création du commit de release...${NC}"
git add pyproject.toml src/__version__.py
if [ -f CHANGELOG.md ]; then
    git add CHANGELOG.md
fi

git commit -m "chore(release): prepare for $NEW_TAG

- Bump version to $NEW_VERSION
- Update version files
- Generate changelog"

# Créer le tag
echo -e "${BLUE}🏷️  Création du tag $NEW_TAG...${NC}"
git tag -a "$NEW_TAG" -m "Release $NEW_TAG

$(git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~10")..HEAD)"

# Pousser vers le repository distant
echo -e "${BLUE}📤 Push vers le repository distant...${NC}"
git push origin main
git push origin "$NEW_TAG"

echo -e "${GREEN}🎉 Release $NEW_TAG créée avec succès!${NC}"
echo -e "${BLUE}🔗 La release sera automatiquement créée sur GitHub via le workflow GitHub Actions${NC}"
echo -e "${BLUE}📋 Vous pouvez suivre le progrès sur: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions${NC}"
