// Configuration for commitlint - commit message validation
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Required commit type
    'type-enum': [
      2,
      'always',
      [
        'feat',     // new feature
        'fix',      // bug fix
        'docs',     // documentation
        'style',    // formatting, missing semicolons, etc.
        'refactor', // code refactoring
        'perf',     // performance improvement
        'test',     // adding tests
        'chore',    // maintenance
        'ci',       // continuous integration
        'build',    // build system
        'revert'    // commit revert
      ]
    ],
    // Subject length
    'subject-max-length': [2, 'always', 72],
    'subject-min-length': [2, 'always', 10],
    // Subject format
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    // Type format
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    // Scope format (optional)
    'scope-case': [2, 'always', 'lower-case'],
    // Header length
    'header-max-length': [2, 'always', 100],
    // Body and footer
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [2, 'always']
  },
  // Custom help messages
  helpUrl: 'https://www.conventionalcommits.org/',
  prompt: {
    messages: {
      type: 'Select the type of change you are committing:',
      scope: 'What is the scope of this change (optional):',
      customScope: 'Enter a custom scope:',
      subject: 'Write a short, imperative description of the change:\n',
      body: 'Provide a more detailed description of the change (optional):\n',
      breaking: 'List any BREAKING CHANGES (optional):\n',
      footer: 'List any ISSUES CLOSED by this change (optional):\n',
      confirmCommit: 'Are you sure you want to proceed with the commit above?'
    },
    types: [
      { value: 'feat', name: 'feat:     ✨ New feature' },
      { value: 'fix', name: 'fix:      🐛 Bug fix' },
      { value: 'docs', name: 'docs:     📚 Documentation' },
      { value: 'style', name: 'style:    🎨 Formatting, style' },
      { value: 'refactor', name: 'refactor: ♾️  Refactoring' },
      { value: 'perf', name: 'perf:     ⚡️ Performance improvement' },
      { value: 'test', name: 'test:     🧪 Adding tests' },
      { value: 'chore', name: 'chore:    🔧 Maintenance' },
      { value: 'ci', name: 'ci:       👷 Continuous integration' },
      { value: 'build', name: 'build:    📦 Build system' },
      { value: 'revert', name: 'revert:   ⏪ Commit revert' }
    ]
  }
};
