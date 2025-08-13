// Configuration pour commitlint - validation des messages de commit
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Type de commit requis
    'type-enum': [
      2,
      'always',
      [
        'feat',     // nouvelle fonctionnalité
        'fix',      // correction de bug
        'docs',     // documentation
        'style',    // formatage, point-virgules manquants, etc.
        'refactor', // refactoring du code
        'perf',     // amélioration des performances
        'test',     // ajout de tests
        'chore',    // maintenance
        'ci',       // intégration continue
        'build',    // système de build
        'revert'    // annulation d'un commit
      ]
    ],
    // Longueur du sujet
    'subject-max-length': [2, 'always', 72],
    'subject-min-length': [2, 'always', 10],
    // Format du sujet
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    // Format du type
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    // Format du scope (optionnel)
    'scope-case': [2, 'always', 'lower-case'],
    // Longueur du header
    'header-max-length': [2, 'always', 100],
    // Body et footer
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [2, 'always']
  },
  // Messages d'aide personnalisés
  helpUrl: 'https://www.conventionalcommits.org/',
  prompt: {
    messages: {
      type: 'Sélectionnez le type de changement que vous commitez:',
      scope: 'Quel est le scope de ce changement (optionnel):',
      customScope: 'Entrez un scope personnalisé:',
      subject: 'Écrivez une description courte et impérative du changement:\n',
      body: 'Fournissez une description plus détaillée du changement (optionnel):\n',
      breaking: 'Listez les BREAKING CHANGES (optionnel):\n',
      footer: 'Listez les ISSUES FERMÉES par ce changement (optionnel):\n',
      confirmCommit: 'Êtes-vous sûr de vouloir procéder avec le commit ci-dessus?'
    },
    types: [
      { value: 'feat', name: 'feat:     ✨ Nouvelle fonctionnalité' },
      { value: 'fix', name: 'fix:      🐛 Correction de bug' },
      { value: 'docs', name: 'docs:     📚 Documentation' },
      { value: 'style', name: 'style:    🎨 Formatage, style' },
      { value: 'refactor', name: 'refactor: ♻️  Refactoring' },
      { value: 'perf', name: 'perf:     ⚡️ Amélioration des performances' },
      { value: 'test', name: 'test:     🧪 Ajout de tests' },
      { value: 'chore', name: 'chore:    🔧 Maintenance' },
      { value: 'ci', name: 'ci:       👷 Intégration continue' },
      { value: 'build', name: 'build:    📦 Système de build' },
      { value: 'revert', name: 'revert:   ⏪ Annulation de commit' }
    ]
  }
};
