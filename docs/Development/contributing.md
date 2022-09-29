# How to Contribute
Hi there! And thanks for checking out this contribution guide. If you're considering helping out, it's greatly appreciated ✨❤️ 

!!! Note
    Proxima is an application used everyday by myself and my editing team. While it may not be at a major release yet, it is used heavily in a production environment.
    If you have any questions about its development or usage please start a [discussion](https://github.com/in03/proxima/discussions/categories/q-a) or if you have a problem, open an [issue](https://github.com/in03/proxima/issues).

If you're not into coding but you'd still like to help, you can:

- Contribute wikis, guides and other sorts of documentation to help others use Proxima
- Contribute icons, graphics and other visual goodies to make Proxima feel more accessible
- Contribute usage feedback; bugs, questions, concerns, complaints, queries, suggestions
- And if you haven't already, please consider starring the repo! ✨

---

# Preferred Practices, Tools and Styles
Below are the building blocks of Proxima's development environment. Everyone does things differently and suggestions for improvement are always welcome, but consistency is important! Please make sure you're familiar with the following 😎👍

## Git basics

### Issues

#### Create a new issue
If you spot a problem, [search if an issue already exists](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-issues-and-pull-requests#search-by-the-title-body-or-comments). If a related issue doesn't exist, you can open a new issue using a relevant [issue form](https://github.com/in03/Proxima/issues/new/choose). 

#### Solve an issue
Scan through our [existing issues](https://github.com/in03/Proxima/issues) to find one that interests you. You can narrow down the search using `labels` as filters. See [Labels](/contributing/how-to-use-labels.md) for more information. As a general rule, we don’t assign issues to anyone. If you find an issue to work on, you are welcome to open a PR with a fix.

### Make Changes
To make changes you'll have to clone the repo and set up the dev environment, to do so you'll need the following tools:
- git
- poetry
- python >=3.10 | python 3.6 (for legacy resolve-17 branch)
- DaVinci Resolve Studio with scripting enabled
- preferred code editor (recommend VSCode)

## Branching workflow
Currently this repo does not use a 'develop' branch, just a 'main' branch with multiple 'topic' branches. Any time a new feature is to be added or bug is to be fixed, a GitHub issue must exist and a new branch created named after this issue, with the syntax 'topic-type/issue-number/brief-description'. Hyphens instead of spaces, slashes to separate tokens. i.e:

```
git branch feat/103/chunking-support
```

The topic serves to give a quick indication of the scope and longevity of the branch and help make a semantically-versioned pull-request process quicker. The issue number links to the issue complete with all comments and discussion that detail exactly what work needs to be completed. The brief description should be as short as possible and serves to remind others what the branch addresses at a glance, without having to look up the issue number. Otherwise it can be easy to work on a branch only to find out later that it was the wrong one. Recommended topic types are:

- feat (a single feature or enhancement to be implemented)
- bug (a single bug to be fixed)
- WIP (a long-running idea or feature with potentially multiple moving parts, not to be finished with anytime soon)
- junk (a test/experimental branch to play around with that was never designed to be merged with main)

## Collaborating with Pull Requests


## Poetry
Poetry manages dependency resolution, build/packaging/deployment and development virtual environment.
To develop Proxima you will need poetry installed. Follow instructions for installation here:
https://python-poetry.org/

## Conventional Commits
This repo uses conventional commit style. Future intentions are to automate semantically-versioned releases using 'BREAKING CHANGE' footers to bump a major version, 'feat:' to bump a minor version and 'bug:' to bump a patch version. Other types do not bump semantic version numbers. Non-conventional commits will not fail checks, so they are still supported, but they are not recommended. 
The following commit types in particular are recommended:

  - feat
  - fix
  - docs
  - style
  - refactor
  - perf
  - test
  - build
  - ci
  - chore
  - revert


## Semantic Versioning
As mentioned in the **Conventional Commits** section, semantic versioning is planned to be employed on app releases. A GitHub app, 'Semantic-prs' is used to ensure at least pull-requests use conventional commit style so versioning can be reliably automated. As development is still early, major functionality is still being fleshed out and major backwards incompatible changes are likely for the time being. The official version remains at 0.1.0 for now with git commit hashes being used for meaningful version-tracking and constrains for the time being. After the first major release, Proxima will follow semantic versioning.

## Pre-commit Hooks
Pre-commit hooks are recommended, but are opt-in, since individual developers must set them up. They're installed with the other Poetry development dependencies, but must be set up manually with `pre-commit install`. From then on, any commit will run through a series of local checks. If fixes are automatically applied, simply stage changes and commit again. Pre-commit checks are defined in `.pre-commit-config.yaml`

## Pre-commit CI
Alongside pre-commit hooks is pre-commit CI, which runs as a GitHub app. So long as pre-commit hooks are set-up properly, pre-commit CI won't catch anything, otherwise it will show a failed check. Pre-commit CI also uses `.pre-commit-config.yaml`

## Automatic Issues from TODOs
This repository uses a GitHub Action to convert in-code todo comments into issues. Todos should be written like this; with a short title, 
description and label when necessary:

```
# TODO: Post-encode linking not working
# Seems like this function is being passed an empty list?
# labels: bug
```

Once pushed to the repo, these TODOS are automatically pulled out and turned into issues, with the title for the issue title, the remaining lines as a description, a short code excerpt embedded and the label set appropriately. The idea for these TODOs is to quickly track short-term problems that need addressing. An issue that arises when these TODOs stick-around is they cross-pollinate branches, creating multiple issues (which are branch agnostic). The key takeaway here is that ideally **no TODOs should remain before a pull-request.** Further documentation for this workflow is available here: https://github.com/alstr/todo-to-issue-action
