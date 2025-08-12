#!/bin/bash

# Script pour tester localement avec l'environnement virtuel activé
# Usage: ./scripts/test-local.sh [command]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier si nous sommes dans le bon répertoire
if [ ! -f "pyproject.toml" ]; then
    log_error "Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    log_error "Environnement virtuel non trouvé. Créez-le avec: python -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
log_info "Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que l'environnement virtuel est activé
if [ -z "$VIRTUAL_ENV" ]; then
    log_error "Impossible d'activer l'environnement virtuel"
    exit 1
fi

log_success "Environnement virtuel activé: $VIRTUAL_ENV"

# Fonction pour exécuter les tests
run_tests() {
    log_info "Exécution des tests..."
    python -m pytest tests/ -v
}

# Fonction pour exécuter pre-commit
run_precommit() {
    log_info "Exécution des hooks pre-commit..."
    pre-commit run --all-files
}

# Fonction pour exécuter les vérifications de qualité
run_quality_checks() {
    log_info "Vérifications de qualité du code..."
    
    log_info "Black formatting..."
    black --check --diff .
    
    log_info "isort import sorting..."
    isort --check-only --diff .
    
    log_info "flake8 linting..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    log_info "bandit security checks..."
    bandit -r . -ll
}

# Fonction pour tester avec act
run_act_tests() {
    log_info "Test des workflows avec act..."
    
    if ! command -v act &> /dev/null; then
        log_error "act n'est pas installé. Installez-le avec: brew install act"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker n'est pas en cours d'exécution. Démarrez Docker Desktop."
        exit 1
    fi
    
    log_info "Test du workflow de qualité..."
    act --container-architecture linux/amd64 -j quality-checks
    
    log_info "Test du workflow de validation des commits..."
    act pull_request --container-architecture linux/amd64 -W .github/workflows/commit-validation.yml
}

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commandes disponibles:"
    echo "  tests           Exécuter les tests Python"
    echo "  precommit       Exécuter les hooks pre-commit"
    echo "  quality         Exécuter les vérifications de qualité"
    echo "  act             Tester les workflows avec act"
    echo "  all             Exécuter tous les tests (tests + precommit + quality)"
    echo "  help            Afficher cette aide"
    echo ""
    echo "Si aucune commande n'est spécifiée, 'all' sera exécuté."
}

# Traitement des arguments
case "${1:-all}" in
    "tests")
        run_tests
        ;;
    "precommit")
        run_precommit
        ;;
    "quality")
        run_quality_checks
        ;;
    "act")
        run_act_tests
        ;;
    "all")
        log_info "Exécution de tous les tests..."
        run_precommit
        run_quality_checks
        run_tests
        log_success "Tous les tests ont réussi!"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        log_error "Commande inconnue: $1"
        show_help
        exit 1
        ;;
esac

log_success "Terminé!"
