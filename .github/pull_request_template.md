# 🚀 Pull Request

## 📋 Description

### Summary of Changes
<!-- Briefly describe the modifications made -->

### Type of Change
- [ ] 🐛 **Bug fix** (fixes an issue)
- [ ] ✨ **Feature** (new functionality)
- [ ] 💥 **Breaking change** (incompatible change)
- [ ] 📚 **Documentation** (documentation update)
- [ ] 🔧 **Chore** (maintenance, dependencies)
- [ ] ⚡ **Performance** (performance improvement)
- [ ] 🧪 **Tests** (adding or modifying tests)
- [ ] 🎨 **Style** (formatting, code style)

## 🔗 Related Issues

<!-- Reference related issues -->
- Fixes #(issue number)
- Closes #(issue number)
- Related to #(issue number)

## 🧪 Tests

### Tests Added/Modified
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests
- [ ] Security tests
- [ ] No tests required

### Code Coverage
- [ ] Code coverage is maintained (≥ 80%)
- [ ] New tests added for modified code
- [ ] Existing tests updated if necessary

### Manual Tests Performed
<!-- Describe the manual tests you performed -->

```bash
# Test commands used
python -m pytest tests/
pre-commit run --all-files
act --container-architecture linux/amd64 -j quick-validation
```

## 📸 Screenshots (if applicable)

<!-- Add screenshots for interface changes -->

## 🔄 Migration/Breaking Changes

### Breaking Changes
- [ ] No breaking changes
- [ ] Configuration changes required
- [ ] API changes
- [ ] Data structure changes

### Migration Guide
<!-- If applicable, describe how to migrate from the previous version -->

## 📋 Checklist

### Code Quality
- [ ] My code follows the project conventions
- [ ] I have performed a self-review of my code
- [ ] I have commented complex parts of my code
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works

### Documentation
- [ ] I have updated the corresponding documentation
- [ ] I have updated docstrings if necessary
- [ ] I have added usage examples if applicable

### Git & Commits
- [ ] My commits follow conventions (Conventional Commits)
- [ ] I have rebased my branch on the latest version of main
- [ ] My branch has no merge conflicts
- [ ] I have squashed fix commits

### CI/CD
- [ ] All GitHub Actions workflows pass
- [ ] Pre-commit tests pass locally
- [ ] I have tested with `act` if possible

## 🔍 Review Focus

### Areas of Attention for Reviewers
<!-- Indicate parts of the code that require special attention -->

### Specific Questions
<!-- Ask specific questions to reviewers -->

## 📊 Performance Impact

- [ ] No performance impact
- [ ] Performance improvement
- [ ] Minor negative performance impact
- [ ] Significant performance impact (justified below)

### Performance Impact Justification
<!-- If applicable, explain why the performance impact is acceptable -->

## 🔒 Security Considerations

- [ ] No security impact
- [ ] Security improvement
- [ ] New AWS permissions required (listed below)
- [ ] New dependencies added (checked for vulnerabilities)

### New AWS Permissions
<!-- List the new permissions required -->

## 🌍 Deployment Notes

### Required Configuration
<!-- Describe necessary configuration changes -->

### Environment Variables
<!-- List new environment variables -->

### Deployment Order
<!-- If applicable, describe the required deployment order -->

## 📝 Additional Notes

<!-- Any additional information useful for reviewers -->

---

## 🏷️ Suggested Labels

<!-- Labels will be automatically added by workflows -->
- `size/small` `size/medium` `size/large` - PR size
- `priority/high` `priority/medium` `priority/low` - Priority
- `area/aws-api` `area/data-processing` `area/reports` - Functional area

## 🤝 Reviewers

<!-- Mention specific reviewers if necessary -->
@username - For expertise in area X
@username - For architecture validation

---

**Thank you for your contribution! 🎉**
