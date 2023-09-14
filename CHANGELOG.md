# CHANGELOG



## v1.0.7 (2023-09-14)

### Build

* build: Bump package version ([`08cd3f5`](https://github.com/in03/proxima/commit/08cd3f58af9812581ae9eed0beaa82b1f4ec9d54))

* build: Export updated requirements.txt ([`88f980b`](https://github.com/in03/proxima/commit/88f980ba16f1996526cacdf6de86559f597bf0ca))

* build: Export updated requirements.txt ([`5733bbc`](https://github.com/in03/proxima/commit/5733bbcfa91ee1c374c49201cb664228e707c7b4))

### Chore

* chore: gitignore user config toml ([`5842d52`](https://github.com/in03/proxima/commit/5842d5244fe24bf962de2fdfeedba20367ff3616))

### Documentation

* docs: Update README

Remove new TOML support from roadmap, added to features, updated issue link to PR link ([`ebcc818`](https://github.com/in03/proxima/commit/ebcc81863bbd111a50f1a0067dee74811dfa170d))

### Fix

* fix: Broken module import paths ([`6461cd5`](https://github.com/in03/proxima/commit/6461cd567688f3848b88797221c5c33a6215128a))

* fix: Broken module import paths ([`242eb31`](https://github.com/in03/proxima/commit/242eb316bd87106899d3f7a1d6d3ff31d5215dc1))

* fix: Broken dependency ([`41a2501`](https://github.com/in03/proxima/commit/41a2501bc27ba5cc09a6c7d6f965c1ff5c28cb2a))


## v1.0.6 (2023-02-20)

### Chore

* chore: [pre-commit.ci] automatic update (#259)

updates:
- [github.com/commitizen-tools/commitizen: v2.40.0 → v2.42.0](https://github.com/commitizen-tools/commitizen/compare/v2.40.0...v2.42.0)

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`e92b4a9`](https://github.com/in03/proxima/commit/e92b4a99521b3d1e58807937097f66c433846f71))

### Documentation

* docs(is_offline): Disambiguate &#39;Offline&#39; ([`99ac4ef`](https://github.com/in03/proxima/commit/99ac4ef3cd41ef64aa29a258bdf0939fcf43813f))

* docs(is_linked): Disambiguate &#39;linked&#39; ([`572294f`](https://github.com/in03/proxima/commit/572294ff395a482f1a487360e05fa24bebd2a6b5))

### Fix

* fix: Incorrect definition of &#39;linked&#39; ([`70c3c03`](https://github.com/in03/proxima/commit/70c3c03ecc129f47e2ab41b5de6bd3942ed67632))

* fix: Inverted offline logic ([`1ce6aa5`](https://github.com/in03/proxima/commit/1ce6aa5dc0dc8a2df777b6d3967c929a4c06dcd0))

* fix(settings): Settings priority issues

Some settings had incorrect keys and were pulling defaults from the
pydantic defaults. I removed the defaults from Pydantic for better
config/code seperation.

Some settings were renamed to more accurately reflect their purpose,
leading to some breaking changes in configuration. Unfortunately, if a
user attempted to change the settings with incorrect keys,
they were ineffective anyway.

Although technically a breaking change, will treat this as semver minor
bump. The version constraints are still set to respect semver minor
changes as incompatible. ([`b11c5de`](https://github.com/in03/proxima/commit/b11c5de79e0ec84d927110c1e03f6feec0b32ee5))

### Refactor

* refactor(newest_linkable): Improve readability ([`1651bc2`](https://github.com/in03/proxima/commit/1651bc295e41b7d7ddd56b244eddb73c4cb74437))

* refactor: Rename ambiguous &#39;managed_proxy_status&#39; ([`d36c168`](https://github.com/in03/proxima/commit/d36c1685cb4cec523639140a3cef60f365621a19))

* refactor(batch): Improve readability

- De-nesting
- More comments
- Exit early
- More debug logs ([`ea5afa4`](https://github.com/in03/proxima/commit/ea5afa4e90bc1f9c0001e0b9a55c7a5a2e97157f))

* refactor: Disambiguate &#39;already linked&#39; usage ([`6c14851`](https://github.com/in03/proxima/commit/6c14851d9224db80b370c0b0e6975c3a57c9eebf))

* refactor: Disambiguate &#39;already linked&#39; usage ([`f356fd0`](https://github.com/in03/proxima/commit/f356fd0c3a87e48d985a3f9efbc63240ccf53312))

### Unknown

* Merge pull request #268 from in03/bugfix/266/detecting-proxy-status-none-as-offline ([`2f3ac3a`](https://github.com/in03/proxima/commit/2f3ac3a75aa90c989d33d9fa4b5ef624506025d5))


## v2.0.0 (2023-02-16)

### Refactor

* refactor: SettingsManager with TOML and better practices (#258) ([`89a8fa4`](https://github.com/in03/proxima/commit/89a8fa47a99e345c93e4bbbb6401658d71bad1f9))


## v1.0.5 (2023-02-09)

### Fix

* fix(build): Typed git vars were unassigned ([`ad53709`](https://github.com/in03/proxima/commit/ad5370969247f785118793a5eb775e1d49bf73b1))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/in03/proxima into main ([`7de8196`](https://github.com/in03/proxima/commit/7de819645940c86e2066e9ccac5aac90861d4c12))


## v1.0.4 (2023-02-09)

### Fix

* fix: isort broke fragile __init__ imports ([`e227ac2`](https://github.com/in03/proxima/commit/e227ac23a4daea40bcd278d9749b6442c61205de))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/in03/proxima into main ([`b783acc`](https://github.com/in03/proxima/commit/b783acc210f65b467ccc3d78b591d8741f0b8681))


## v1.0.3 (2023-02-09)

### Build

* build: Export updated requirements.txt ([`c539357`](https://github.com/in03/proxima/commit/c539357784b69706d1b3319bf154997bc7fb7992))

* build: Update black ([`627037c`](https://github.com/in03/proxima/commit/627037cb374a7ebb60fe178d82f2633f5235def3))

### Chore

* chore: [pre-commit.ci] automatic update (#253)

* chore: [pre-commit.ci] automatic update

updates:
- [github.com/psf/black: 22.12.0 → 23.1.0](https://github.com/psf/black/compare/22.12.0...23.1.0)

* chore: [pre-commit.ci] automatic fixes

---------

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`f96d749`](https://github.com/in03/proxima/commit/f96d749a5d997fa4b23d2e6f8537b3ce3f516e1a))

### Ci

* ci: Disable flake8 for now ([`a45a458`](https://github.com/in03/proxima/commit/a45a45800aabd23991dc72297d53ec137c6e3955))

* ci: Add flake8 ([`06440e6`](https://github.com/in03/proxima/commit/06440e660da38f41e927e69dbfba323295e3ddd4))

* ci: Add isort, flake8 to precommit ([`95691cc`](https://github.com/in03/proxima/commit/95691cc22e6c00083df1f4e3c750af90ca7b8276))

* ci: Enable upload to PyPi ([`f7b6a53`](https://github.com/in03/proxima/commit/f7b6a537591e0369d9d1072fd3b3b6c6d19d1215))

### Fix

* fix: git sha type error ([`02064fb`](https://github.com/in03/proxima/commit/02064fb439786c37c305e763c0c06b97fe9e230f))

* fix: git_sha attribute error ([`357c821`](https://github.com/in03/proxima/commit/357c821e6f021b7b9ef3cb8909dae727468f2775))

### Refactor

* refactor: Remove unused statement ([`0b14889`](https://github.com/in03/proxima/commit/0b14889408f570b4105d85afa9d498de566480f3))

### Style

* style: package wide isort ([`deaeb9c`](https://github.com/in03/proxima/commit/deaeb9cf57db75a61ec2e28a01e4f06db71c053c))

* style: Format all modules with black ([`f061082`](https://github.com/in03/proxima/commit/f0610826409be4a81fbd9a58ef51529a018242d7))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/in03/proxima into main ([`128023e`](https://github.com/in03/proxima/commit/128023e7f226da511f09651b37efeb37d25b4742))

* Merge branch &#39;main&#39; of https://github.com/in03/proxima into main ([`9412554`](https://github.com/in03/proxima/commit/94125549e21ca9bc6851274c6cf04e4304b7b499))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`232e0ba`](https://github.com/in03/proxima/commit/232e0baeb92fb50d2a8c99579900f43c78355dbb))


## v1.0.2 (2023-02-06)

### Build

* build: Export updated requirements.txt ([`825d736`](https://github.com/in03/proxima/commit/825d736efc3295df47cda994db0426c77e7d9d87))

* build: Using official notify-py again ([`af61774`](https://github.com/in03/proxima/commit/af617743fa29013b54ca48188729c44749a893b7))

* build(deps): bump setuptools from 65.3.0 to 65.5.1 (#243)

Bumps [setuptools](https://github.com/pypa/setuptools) from 65.3.0 to 65.5.1.
- [Release notes](https://github.com/pypa/setuptools/releases)
- [Changelog](https://github.com/pypa/setuptools/blob/main/CHANGES.rst)
- [Commits](https://github.com/pypa/setuptools/compare/v65.3.0...v65.5.1)

---
updated-dependencies:
- dependency-name: setuptools
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`31a5cfe`](https://github.com/in03/proxima/commit/31a5cfe0e8a39d9d3c972e3e651b8f253c7c8ac3))

* build: Add python-semantic-release as Poetry dependency ([`5a83136`](https://github.com/in03/proxima/commit/5a83136153707af58e94c9cd6e2fb7b68e3f4985))

### Chore

* chore: [pre-commit.ci] automatic update (#236)

updates:
- [github.com/commitizen-tools/commitizen: v2.35.0 → v2.40.0](https://github.com/commitizen-tools/commitizen/compare/v2.35.0...v2.40.0)
- [github.com/psf/black: 22.10.0 → 22.12.0](https://github.com/psf/black/compare/22.10.0...22.12.0)
- [github.com/pre-commit/pre-commit-hooks: v4.3.0 → v4.4.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.3.0...v4.4.0)

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`cb74425`](https://github.com/in03/proxima/commit/cb74425540bdc4431716a9e5a2d5600a257f2099))

### Ci

* ci: Change to sem-rel GH action ([`6b92166`](https://github.com/in03/proxima/commit/6b9216616ea42eb75cbef9165760dc5743f086a8))

* ci: Add repo and pypi secrets for auto-release ([`0db66ea`](https://github.com/in03/proxima/commit/0db66eac3d18ec2c5b4767bd8457f816d4b3d483))

* ci: Ensure full git history ([`8c1faed`](https://github.com/in03/proxima/commit/8c1faed8e129dbe7880baba7b8cfc5f9945cdf7c))

* ci: Prevent simultaneous releases ([`ea26666`](https://github.com/in03/proxima/commit/ea2666692f5c86186cb5b8aff0fbe2599a881a27))

### Documentation

* docs: Update README.md ([`7a49fd7`](https://github.com/in03/proxima/commit/7a49fd7881b8b73b18e3c5a2817b114cecd79303))

### Fix

* fix: Package path was using PWD! ([`4b2972d`](https://github.com/in03/proxima/commit/4b2972d55c274f3e74429c0c454040e13dacda0b))

### Refactor

* refactor: VC key as environment variable ([`b349a25`](https://github.com/in03/proxima/commit/b349a25049c64a7e11e898a6ea642677982a5d12))

* refactor: More robust version constraint key ([`5b020de`](https://github.com/in03/proxima/commit/5b020de9a2a519369797ca8ac1eccac0a71e441f))

### Style

* style: flake8 f541 ([`d0b29c1`](https://github.com/in03/proxima/commit/d0b29c1a4575c2c4c57d205b5f41aff354d6122e))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`9fb3650`](https://github.com/in03/proxima/commit/9fb3650cd28f6ba7e52d814bfe051e08f1120adf))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`983f712`](https://github.com/in03/proxima/commit/983f712c6e00ceb715d93e8a6aa92c99c838cb24))


## v1.0.1 (2023-01-25)

### Build

* build: Manually bump version for first major release ([`2661661`](https://github.com/in03/proxima/commit/2661661646cde78658fa5737135f7a02faaa13e7))

* build: Export updated requirements.txt ([`c744932`](https://github.com/in03/proxima/commit/c74493224e5220d80b6fc9bbbf0e0f8c46508eea))

* build: Export updated requirements.txt ([`c5e84be`](https://github.com/in03/proxima/commit/c5e84be0fa334ff4659541a6581c85d2d494f701))

* build: Make docs optional ([`39ee9ce`](https://github.com/in03/proxima/commit/39ee9ce02589c463f125a32923463997bcfdefeb))

* build: Export updated requirements.txt ([`289504b`](https://github.com/in03/proxima/commit/289504bf5ec2423f8592de647bc09a9464ac30e1))

* build: Export updated requirements.txt ([`ccef3ef`](https://github.com/in03/proxima/commit/ccef3ef55c65c922cffdcc58a8b7d3c5098befc4))

* build: Export updated requirements.txt ([`5be21b6`](https://github.com/in03/proxima/commit/5be21b6514059c334d0937b78e573fc9a4993c25))

* build: Export updated requirements.txt ([`f63bb5c`](https://github.com/in03/proxima/commit/f63bb5cbc5bc5acb9d949a1c72202c68b402a833))

* build(poetry): Add vc key to poetry include section

Forgot to explicitly include version_constraint_key when Poetry builds.
The file is not pulled into the installation when built with pip or pipx
without being explicitly included. ([`fb45d79`](https://github.com/in03/proxima/commit/fb45d79df521f215d3e228830cc28b2ae78fb60e))

* build(poetry): remove unused merge_args dev dependency ([`e884f30`](https://github.com/in03/proxima/commit/e884f30777eb1fafe75edda372f0c74dbbbba271))

### Chore

* chore: Add FUNDING.yml ([`c846285`](https://github.com/in03/proxima/commit/c8462850636eb50ce5761b364a8a07985144b6c1))

* chore: [pre-commit.ci] automatic update (#230)

* chore: [pre-commit.ci] automatic update

updates:
- [github.com/psf/black: 22.8.0 → 22.10.0](https://github.com/psf/black/compare/22.8.0...22.10.0)

* build: Export updated requirements.txt

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt;
Co-authored-by: pre-commit-ci[bot] &lt;pre-commit-ci[bot]@users.noreply.github.com&gt; ([`1d735bf`](https://github.com/in03/proxima/commit/1d735bfbf744bf18572aa4cb0fbc30346cb13e09))

* chore: [pre-commit.ci] automatic update (#188)

* chore: [pre-commit.ci] automatic update

updates:
- [github.com/commitizen-tools/commitizen: v2.27.1 → v2.35.0](https://github.com/commitizen-tools/commitizen/compare/v2.27.1...v2.35.0)
- [github.com/psf/black: 22.3.0 → 22.8.0](https://github.com/psf/black/compare/22.3.0...22.8.0)
- [github.com/pre-commit/pre-commit-hooks: v4.1.0 → v4.3.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.1.0...v4.3.0)

* refactor: Update version_constraint_key

* refactor: Update version_constraint_key

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt;
Co-authored-by: pre-commit-ci[bot] &lt;pre-commit-ci[bot]@users.noreply.github.com&gt;
Co-authored-by: Caleb Trevatt &lt;in03@users.noreply.github.com&gt; ([`c68ef3c`](https://github.com/in03/proxima/commit/c68ef3c65feec470c56dfc45b5ed6dfd67ce0667))

* chore: Remove old dependencies ([`0ed55e3`](https://github.com/in03/proxima/commit/0ed55e31a0764b1f0c38870dcf62be96bd10a6fb))

* chore: Merge branch &#39;main&#39; ([`618ba2b`](https://github.com/in03/proxima/commit/618ba2b5b809110454d7487102c533ddf9a67df5))

* chore(__pycache__): remove ignorables

Accidentally committed `__pycache__ .pyc` files somehow. ([`587d320`](https://github.com/in03/proxima/commit/587d3203daad5bd2bee6e2fa1e48a21a6ac6252f))

* chore: rollback pre-commit to 4.1.0

precommit 4.2.0 drops Python 3.6 support.
Will need to migrate to 3.7 or above soon but must be switch to Resolve
18 for &gt;3.6 support. Drops compatability with all 17 users. Need a final
17 release first. ([`0c190b2`](https://github.com/in03/proxima/commit/0c190b26c3b56f7eea6aa31d236d938619bfb616))

* chore: [pre-commit.ci] automatic update (#90)

updates:
- [github.com/pre-commit/pre-commit-hooks: v4.1.0 → v4.2.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.1.0...v4.2.0)
- [github.com/pre-commit/pre-commit-hooks: v4.1.0 → v4.2.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.1.0...v4.2.0)

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`c3ae387`](https://github.com/in03/proxima/commit/c3ae387f6b1a99bfdbff3696d67595dda67d0ec9))

* chore: alter pre-commit CI msg to pass semantic-PR CI ([`999d14e`](https://github.com/in03/proxima/commit/999d14ec92f588b89601b1809b1e167b6c37dadc))

* chore: attempt to trigger TODO-to-issues CI action ([`dab5839`](https://github.com/in03/proxima/commit/dab58394e1b8685f085c56227a5b8a40af02287c))

* chore: remove TODOs AGAIN to trigger gh issues ([`81a978e`](https://github.com/in03/proxima/commit/81a978efdde4e07e165ea16e8eecf401f2b1d7ee))

* chore: Recommit TODOs to trigger gh action ([`b20eb50`](https://github.com/in03/proxima/commit/b20eb50bf1aafcc9a6b9ef55a63571b51a75caff))

* chore: hide TODOs for recommit to trigger action ([`d7d895e`](https://github.com/in03/proxima/commit/d7d895e8a53edbc61757213b966cebf4068168fb))

* chore: Add TODOs to generate issues in github

- Fix pywin32 dependency error, set gh runner to Windows
- Delete duplicate gh-action workflow ([`890a60e`](https://github.com/in03/proxima/commit/890a60e066c8f5b41b059047a76af0d4a6828bea))

* chore: Add GitHub &#39;TODO-to-issue&#39; action ([`2290a8e`](https://github.com/in03/proxima/commit/2290a8e33a8b4451b3b7e67d6ff275985d36dabe))

* chore: update dependencies ([`1679e38`](https://github.com/in03/proxima/commit/1679e380afc640119e9656fac5d830537add23f0))

### Ci

* ci(semantic-release): Bump poetry version ([`fbf2b3f`](https://github.com/in03/proxima/commit/fbf2b3f65e19725febc05e6a6c777d6aa4ba5acb))

* ci: Pin python-semantic-release version ([`5e720b4`](https://github.com/in03/proxima/commit/5e720b40cd58d4498d4e7490b9248a2fab7a3962))

* ci: Change branch name for release criteria ([`2187ce2`](https://github.com/in03/proxima/commit/2187ce28e5772cd833119b7fd5eed91f51925830))

* ci: Remove flake8 and pytest for now ([`c31f7f2`](https://github.com/in03/proxima/commit/c31f7f2400c90fe9393840a1cfa54af845cd6437))

* ci: Add flake8 ([`6e62725`](https://github.com/in03/proxima/commit/6e6272519a32d4c7a775e0386e3ce28b083be34a))

* ci: Attempt fix poetry config error ([`73fe9bf`](https://github.com/in03/proxima/commit/73fe9bf9a33883dc30e2237c063bbdd8e915d5cc))

* ci: Remove large file check ([`9d38a48`](https://github.com/in03/proxima/commit/9d38a48838a37e6cb93733acc6df21aaf95d4617))

* ci(issues): fix GH action trigger ([`59e2026`](https://github.com/in03/proxima/commit/59e2026b0324cc55c6902621c3376b505d61149b))

* ci(issues): Moved action config to correct file

Created issue-branch.yml file in .github directory.
Configuration for create-issue-branch action isn&#39;t supposed to be in the
workflow file itself. ([`8ac21b5`](https://github.com/in03/proxima/commit/8ac21b50d2cd4c8b6d716bd75fbedfa1d8e2c33e))

* ci(issues): Fix indentation parsing error ([`67ea1b8`](https://github.com/in03/proxima/commit/67ea1b878eca4a6a84a9ac0f116fcae923490605))

* ci(issues): Fixed indentation error ([`117f13a`](https://github.com/in03/proxima/commit/117f13adfc5e60315638380604d3df4b4bea413f))

* ci: Fix syntax error in CIB (#183)

* ci(issues): Add GH action &#39;Create Issue Branch&#39;

More testing needed!

* refactor: Update version_constraint_key

* ci(issues): Fix syntax error in CIB

Forgot &#39;uses:&#39;...

* refactor: Update version_constraint_key

* refactor: Update version_constraint_key ([`809c7db`](https://github.com/in03/proxima/commit/809c7dbbb2885701782f4339b17758afc9ceb0a9))

* ci(requirements.txt): Make check pass if no change

Also now only runs on pushes, not pull-requests. ([`8f242d9`](https://github.com/in03/proxima/commit/8f242d9ed537197fc08be69cbdce87894810476f))

* ci: Fix broken export-requirements GitHub action (#170)

* ci: export requirements.txt on each push

- Added [export requirements action](https://github.com/DivideProjects/poetry-export-requirements-action)
- Renamed workflow yaml files to fit perceived scopes and be consistent

* ci: fix invalid yaml, separate ci jobs

Renamed CI workflow files yet again. Something wrong with formatting.
One job per file seems tidy enough.

* refactor: Update version-constraint key

* ci: fix requirements.txt not being pushed to repo

Action didn&#39;t include commit and push steps so file wasn&#39;t persisting.

* refactor: Update version-constraint key

* refactor: Update version-constraint key

* ci: fix syntax error in export-requirements action

Missing dash.... Gosh!

* refactor: Update version-constraint key

* refactor: Update version-constraint key

Co-authored-by: Update VC-key Action &lt;action@github.com&gt; ([`d36a48e`](https://github.com/in03/proxima/commit/d36a48e5a848b6478ace1aa1130f0dcaaff6a673))

* ci: Fix requirements.txt not being pushed to repo (#169)

* ci: export requirements.txt on each push

- Added [export requirements action](https://github.com/DivideProjects/poetry-export-requirements-action)
- Renamed workflow yaml files to fit perceived scopes and be consistent

* ci: fix invalid yaml, separate ci jobs

Renamed CI workflow files yet again. Something wrong with formatting.
One job per file seems tidy enough.

* refactor: Update version-constraint key

* ci: fix requirements.txt not being pushed to repo

Action didn&#39;t include commit and push steps so file wasn&#39;t persisting.

* refactor: Update version-constraint key

* refactor: Update version-constraint key

Co-authored-by: Update VC-key Action &lt;action@github.com&gt; ([`27cf226`](https://github.com/in03/proxima/commit/27cf22619b6b3bcac124260c151acbc94059fdab))

* ci: Export requirements.txt on build (#168) ([`8bd6c63`](https://github.com/in03/proxima/commit/8bd6c63af8e661ac00929f7d7732af64c5fd43a6))

### Documentation

* docs: Add semantic-release badge ([`ff4e59e`](https://github.com/in03/proxima/commit/ff4e59ef459445a0dc8d78ead5861a7f4feb0b0a))

* docs: Fix mkdocs.yml ([`63d30b3`](https://github.com/in03/proxima/commit/63d30b3da45b264d117aec0cca45257f988c56de))

* docs: Remove &#39;termynal&#39; plugin ([`450710e`](https://github.com/in03/proxima/commit/450710ef02cc9769e4396e24a92ade866a812a9a))

* docs: Fix mkdocs.yml ([`04943dc`](https://github.com/in03/proxima/commit/04943dc828adea1968e588ce7e81dec2ded20b8a))

* docs(job): Logger precision of language ([`1a7f1c7`](https://github.com/in03/proxima/commit/1a7f1c720690ba0ff8b99c3e23fd571d1b884371))

* docs: Add roadmap and philosophy ([`b6470c1`](https://github.com/in03/proxima/commit/b6470c11739954ea3fc5d2d90acf48ca6064cbaa))

* docs: Update README.md ([`3509175`](https://github.com/in03/proxima/commit/350917519e0dd3cb4bbfff4e582fa81999760ec3))

* docs: Update landing page ([`b268d3d`](https://github.com/in03/proxima/commit/b268d3d3ea6de25d3882df43fcb441f91c6174f1))

* docs: Update README.md

Initial updates to match new documentation on GitHub pages ([`23fd29e`](https://github.com/in03/proxima/commit/23fd29eae1f47fb7513346d17009835c749bcf4f))

* docs: Improve landing page ([`43bf724`](https://github.com/in03/proxima/commit/43bf724a7a9b15f379f64451db3e21236b0ba65c))

* docs: Update README.md

Add documentation link ([`51b6c1c`](https://github.com/in03/proxima/commit/51b6c1c1e66776fb144af805042dad9a4c9fc11f))

* docs: Update mkdocs site ([`8e3a895`](https://github.com/in03/proxima/commit/8e3a8950db551434fcbd91a73c8b27a4c6ef66dc))

* docs: Update mkdocs site ([`0078f67`](https://github.com/in03/proxima/commit/0078f67280c496527833899efcb9dd14df40b9ab))

* docs: update README


- Added badges
- Added basic UI demo GIF
- Added warning callouts
- Added contribution guide link
- Addressed Blackmagic Proxy Generator
- Added sections detailing existing features and features to come
- Restyled some sections
- Updated old configuration references ([`9f5aa99`](https://github.com/in03/proxima/commit/9f5aa9997a8152dc147bd64847e36411acc72158))

* docs(README): add demo gifs ([`192b9d6`](https://github.com/in03/proxima/commit/192b9d6c55b0713577bc7e8536309d88fc310652))

### Feature

* feat: support-semver-version-constraint (#251) ([`354523a`](https://github.com/in03/proxima/commit/354523a3d3b5bf938d2d7d90aa989033e4fc7656))

* feat(checks): Start support for busy-worker metrics ([`18431a7`](https://github.com/in03/proxima/commit/18431a76c515bb1ac976dbba54691be02d474e6c))

* feat: Extend rerender offline prompt (#232) ([`0407b58`](https://github.com/in03/proxima/commit/0407b587bbceb54237a5e3c32774cc0de21fcab4))

* feat: Redis PubSub for Queuer side progress (#225)

* Create draft PR for #224

* feat(link): Add exception info if all fail link

* refactor: Group ID as Redis channel ID

* refactor: Update version_constraint_key

* refactor: MVP Redis PubSub

* refactor: Update version_constraint_key

* refactor: Tidy deeply nested modules

* refactor: Update version_constraint_key

* fix: Remove new data flag, recalc every loop

Now just calculating progress and task info every iteration of the loop
instead of checking new data flags. It looks like there may be a race
condition of some sort causing inaccurate worker numbers.

I might consider thread locks if they work with Redis&#39; pubsub run_in_thread.

* refactor: Update version_constraint_key

* refactor: Dropped direct Redis usage altogether

Alright, this is kind of funny. Turns out I&#39;ve been reinventing the wheel
this whole time. Celery&#39;s GroupResult contains AsyncResult instances with
all the data we need to get active worker count, task completion and
task encoding progress (with a custom task state definition).

So:
- dropped Redis database polling
- dropped Redis PubSub
- use unique worker IDs instead of sequential prefix to easily start
additional workers at any time

* refactor: Update version_constraint_key

* docs: Update README.md

* build: Export updated requirements.txt

* refactor: Update version_constraint_key

Co-authored-by: in03 &lt;in03@users.noreply.github.com&gt; ([`f75e167`](https://github.com/in03/proxima/commit/f75e1677585c161fc04b9359db25d42a9bd4e242))

* feat: Rebrand to Proxima (#211)

* Create draft PR for #210

* feat(cli): Major app changes

- Rebranded &#34;Resolve Proxy Encoder&#34; as &#34;Proxima&#34;
- Changed CLI entrypoint from &#34;rprox&#34; to &#34;proxima&#34;
- Added full Celery sub command support

* refactor(figlet): Delete unused figlet font

* refactor: Rename all old names across files

* refactor: Update version_constraint_key

* docs(README): New features

- Cross off completed features
- Add features and enhancements to roadmap
- Reflect name change
- Warn dropped support for brokers other than Redis

* refactor: Update version_constraint_key

* docs(README): Grammar

* refactor: Update version_constraint_key ([`2ccae65`](https://github.com/in03/proxima/commit/2ccae6587722afbc9eb94054f41f16a192c06bc9))

* feat: Queuer-side progress indication (#190)

Some refinements and performance improvements are likely needed, but this is good enough to be merged into main. ([`4928568`](https://github.com/in03/proxima/commit/49285682fbf27e4e30aefce77cfb6d5e56fe93ca))

* feat: Add &#34;create issue branch&#34; GH action (#181)

* ci(issues): Add GH action &#39;Create Issue Branch&#39;

More testing needed!

* refactor: Update version_constraint_key ([`c3df49b`](https://github.com/in03/proxima/commit/c3df49bdc108d11e6bca2877905de9de63097a6b))

* feat: Improve version constraining (#165)

* ci: Add GH action to create queue-id file

* ci: test queue-id action

* ci: fix broken git push ref

* ci: Update Queue-ID file

* ci: terminology change - &#39;version-constraint key&#39;

Using &#39;version-constraint key&#39; instead of &#39;queue-id&#39; to be more descriptive.
Celery terminology is already opaque to end users, i.e. &#39;routing-key&#39;
vs &#39;queue&#39;. Queue is both a noun and a verb, and refers to both Celery&#39;s
queue name that receives queued tasks as well as the act of queuing them.

* ci: Fix incorrect variable name

File was being written with &#34;&#34; as key, since variable reference was wrong.

* fix: Force overwrite since file name is different

* refactor: Update version-constraint key

* fix: Unnecessary echo in version_constraint_key

* refactor: Update version-constraint key

* feat: implement mnemonic version constrain key

- moved hefty imports to CLI sub-commands for faster loading time and
quicker UI responsiveness

- queuer checks other workers compatibility against its own
`version_constraint_key` file

TODO:

- get worker queue name from `version_constraint_key` file, otherwise
all locally workers will still be using git-sha mechanism, including self.

- implement `--hide_banner` option globally with Typer

- implement `RPROX_HIDE_BANNER` environment variable

- further test version collision probability

* refactor: Update version-constraint key

* fix: remove unnecessary insecure serialization protocols

* feat(launch_workers.py): worker use new version constraint key

* refactor(launch_workers.py): logging queue-name reflect term change

Still in a bit of a weird place with terminology here. We have `queue`, `version constraint key` and `routing key`. The choice to refer to the name of the queue as `version constraint key` better reflects application usage and user expectations. &#34;Queue&#34; on its own is both a noun and a verb and we already use the term to describe a module and the process of &#34;queuing&#34; proxies. Some additional terminology changes in code may be necessary at a later date.

* refactor: Update version-constraint key

* refactor: Update version-constraint key

Co-authored-by: Update-Queue-ID &lt;update-queue-id@github.com&gt;
Co-authored-by: Update VC-key Action &lt;action@github.com&gt;

pre-commit.ci autofix ([`b4b22fc`](https://github.com/in03/proxima/commit/b4b22fc4ef9737dd7740efa15e5fc7241f9d415b))

* feat: add commitizen support (#164)

Implements #162
:sunglasses: :+1: ([`10554c8`](https://github.com/in03/proxima/commit/10554c8100a015b7f2545ff0b9f6dfd7d1fdf024))

* feat: merge misc enhancements from feat/issue-9

BREAKING CHANGES

Merged some enhancements from:
4eaaf02ec3f66143f5d871d81ebe332d94b537c8
b9d9a357f30dd8cbfc7f77644c53997f7cb4a580

Namely:
- relative imports where possible
- maintain source aspect ratio, match user set vertical resolution
- inherit timecode from Resolve clip attributes, no probing file

Since YouTour&#39;s camera config change, timecode issues were
preventing proxies from linking.

Excluded any chunked-encoding development. ([`572810e`](https://github.com/in03/proxima/commit/572810e9c3d327c265dbbdbf9a0f852b5288432c))

* feat: started work on chunking on queuer-side ([`e800d31`](https://github.com/in03/proxima/commit/e800d3195235f912ce710dc1d6ba3b08cf41659a))

* feat: start split and stitch integration ([`1dd2062`](https://github.com/in03/proxima/commit/1dd20626da282449dc6d562f3f9c3f13ec6eebc5))

* feat: Feature/issue 48 (#66)

* fix: stop spinners from breaking console logging

Bit of a verbose solution that could do with some refinement, but works.
Adresses #42

* chore: delete todos, close issues

* fix: Improve worker console progress output

- Modified `better_ffmpeg_progress` source code instead of import
- Using `rich` now instead of `better_ffmpeg_progress` `tqdm` handler
- Delete broken CI workflow. Will fix later. Unresolvable dependencies.

Addresses #48

* feat: add app settings, improve console output

- Add logfile path, disable version constrain, check for updates
- Improve console spinner behaviour, icons, etc.
- Improve console logging
- Add `--without-gossip` and `--without-mingle` to `worker_celery_args`
in `default_settings.yml`.

BREAKING CHANGE:
some settings renamed and moved!
Recommend re-initialising user config.

Address #42 and #48 ([`507102a`](https://github.com/in03/proxima/commit/507102acd0515429206851f3235e53ac863c9f38))

* feat: Add queuer/worker compatibility check (#40)

* initial dev versioning detection

* Started on github commit query

* Added git based update checking

* Add versioning detection when not package

* FIX: Merge from main, start worker compat testing

* FIX: Catch timeout when calling GitHub API

* FEAT: Queuer/Worker version mismatch warning working

* Moved worker check to CLI queue cmd, better logging

* feat: Add setting to bypass worker compat check

- Fix notify function in helpers
- Fix `worker_use_win_terminal` setting

* docs: Update README

- Recommend pipx to deal with dependency conflicts
- Explain potential issues with running Python 3.6

* [pre-commit.ci] auto fixes from pre-commit.com hooks

for more information, see https://pre-commit.ci

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`f635cee`](https://github.com/in03/proxima/commit/f635cee2978de73546d63460bbef1aebec472339))

### Fix

* fix(BuildInfo): Incorrect version import

BuildInfo was pulling the verison number from site-package&#39;s distinfo.
Running from git would yield the system installed version and if not
installed, would throw an error. ([`100e006`](https://github.com/in03/proxima/commit/100e006ab4fe63d5501ad2644837cd1926f85393))

* fix(job): Incorrect loglevel ([`b90ade1`](https://github.com/in03/proxima/commit/b90ade1b58e91e2fbf3d80aa25835a10a365e595))

* fix: Including vc key incorrectly ([`c323d60`](https://github.com/in03/proxima/commit/c323d60ab455869b6f20320eafdf406de35d2826))

* fix: Pushing vc key to wrong path ([`7637170`](https://github.com/in03/proxima/commit/76371703dc3ec9b3ba764d4b888e20a9d7d3ec4f))

* fix: Broken build_info check ([`713e6ad`](https://github.com/in03/proxima/commit/713e6ad8c49ff272395aca65b09b872493a8e4b4))

* fix: Broken vc_key resolution ([`de4440a`](https://github.com/in03/proxima/commit/de4440ade3c7a5ab78672e5b8377453fac66bbb2))

* fix: Broken vc_key resolution ([`caf7998`](https://github.com/in03/proxima/commit/caf799804067ff6ce1441daa2d5095324cd7f064))

* fix: Version constraint file path inconsistency

We were relying implicitly on the VC file path-depth matching
between different package installation methods. Moving the source a src
subfolder broke the VC key file path resolution for URL/release installs.

This should be fixed with a more robust path-matching solution at some
point. ([`93c8195`](https://github.com/in03/proxima/commit/93c8195cf51ad237ec44756a12594bc9fa418d4d))

* fix: Output directory never created ([`60e2762`](https://github.com/in03/proxima/commit/60e276284517caa49e4f2f68d9d60f84aaad3854))

* fix: Regex criteria applied incorrectly to file extension instead of name ([`dcef3fb`](https://github.com/in03/proxima/commit/dcef3fbc0811b31dc869d0e78961602c36855f44))

* fix(job): Allow modifying &#39;is_offline&#39; property ([`a98f56b`](https://github.com/in03/proxima/commit/a98f56b51a8b23163eab5045fdbdf42ffd991587))

* fix: Set existing media &#39;online&#39;, prevent  offline handler handling ([`6ba72b0`](https://github.com/in03/proxima/commit/6ba72b0cddd839f6e1bff98d36f9e5eafb496cb8))

* fix(tasks): Parsing color data in_range incorrectly ([`88d3009`](https://github.com/in03/proxima/commit/88d3009c4d2f1d585214d8fae396855a487ed5bd))

* fix(batch): Re-render mitmatch_fail queues twice ([`b590631`](https://github.com/in03/proxima/commit/b590631e136e829cc60e70efe798a20049355345))

* fix: collision-check logic flip breaks every export ([`d8a3a75`](https://github.com/in03/proxima/commit/d8a3a75cb7ede2f9b56bdeffaf1db46fab0a940b))

* fix: Incorrect loglevel ([`96bb683`](https://github.com/in03/proxima/commit/96bb6831a1cc5802e6d4d8bf8e013291a0fc6e3a))

* fix: Broken timeout print on app-exit ([`48f892a`](https://github.com/in03/proxima/commit/48f892a8bb7dcae7f4c6c483abb97abee2a7c997))

* fix: handle broken tasks worker-side ([`06dfefe`](https://github.com/in03/proxima/commit/06dfefe21a5f51e53dc74f43b3cb42d73448c6d8))

* fix: Up-to-date emoji ([`6a5d099`](https://github.com/in03/proxima/commit/6a5d099a4be073dae414fec1d1b42a841fd80664))

* fix: Relink Rerendered offline media ([`f011bfb`](https://github.com/in03/proxima/commit/f011bfb0cfa2588c9aa1f58310556241a7026831))

* fix(handlers): handle offline choice not respected ([`0dc0a5a`](https://github.com/in03/proxima/commit/0dc0a5a01d24601e4878a08ba17bc39e74f9488c))

* fix: Relative script path fetching broken

`purge` and `celery` subcommands rely on passing commands to Celery.
Previously they were passing commands to the Celery installed on path
unlike the `launch_workers` module which uses the local package instance.
If Celery isn&#39;t installed on the system (or is incompatible version),
things would break.

- Update `get_script_from_package` function
- Remove `get_celery_binary_path` function
- Remove global Celery from path fallback ([`ac0fa63`](https://github.com/in03/proxima/commit/ac0fa63497398f1374a3047f34f8109e4c0202e6))

* fix: Remove dead Redis PubSub code (#229)

* Create draft PR for #224

* feat(link): Add exception info if all fail link

* refactor: Group ID as Redis channel ID

* refactor: Update version_constraint_key

* refactor: MVP Redis PubSub

* refactor: Update version_constraint_key

* refactor: Tidy deeply nested modules

* refactor: Update version_constraint_key

* fix: Remove new data flag, recalc every loop

Now just calculating progress and task info every iteration of the loop
instead of checking new data flags. It looks like there may be a race
condition of some sort causing inaccurate worker numbers.

I might consider thread locks if they work with Redis&#39; pubsub run_in_thread.

* refactor: Update version_constraint_key

* refactor: Dropped direct Redis usage altogether

Alright, this is kind of funny. Turns out I&#39;ve been reinventing the wheel
this whole time. Celery&#39;s GroupResult contains AsyncResult instances with
all the data we need to get active worker count, task completion and
task encoding progress (with a custom task state definition).

So:
- dropped Redis database polling
- dropped Redis PubSub
- use unique worker IDs instead of sequential prefix to easily start
additional workers at any time

* refactor: Update version_constraint_key

* docs: Update README.md

* build: Export updated requirements.txt

* fix: Remove dead Redis PubSub code

* refactor: Update version_constraint_key

* chore: [pre-commit.ci] automatic fixes

* refactor: Update version_constraint_key

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt;
Co-authored-by: pre-commit-ci[bot] &lt;pre-commit-ci[bot]@users.noreply.github.com&gt; ([`36f5cf5`](https://github.com/in03/proxima/commit/36f5cf5c9b954263b57d408df5dbd2fdb4295e6c))

* fix(ffmpeg_progress): broken relative import ([`050eef8`](https://github.com/in03/proxima/commit/050eef83aab3970d23bd2972dbae2c45bb9843ce))

* fix(resolve): &#39;Is&#39; with literal syntax ([`ced1979`](https://github.com/in03/proxima/commit/ced19796afa1fc16dab2ef074c2bb550cfba05f1))

* fix: Premature link success message (#220) ([`2d6cac7`](https://github.com/in03/proxima/commit/2d6cac7705e75bb8744a306e72ac3914e6e79afe))

* fix: First stream probed is not main video stream (#219)

* Create draft PR for #200

* fix: Add probe_for_input_range func

- Probe input file for correct color range
- Add support for Resolve data level overrides

* fix: Ensure probing video stream

* refactor: Update version_constraint_key

* refactor: Update version_constraint_key ([`4e51283`](https://github.com/in03/proxima/commit/4e512833ef3183d30ba16defd5f0a74398948d53))

* fix: Data levels issues (#209)

* Create draft PR for #200

* fix: Add probe_for_input_range func

- Probe input file for correct color range
- Add support for Resolve data level overrides

* refactor: Update version_constraint_key

Co-authored-by: in03 &lt;in03@users.noreply.github.com&gt; ([`a193f6b`](https://github.com/in03/proxima/commit/a193f6bc5805d40ece8ab0508106f33d81f22ad7))

* fix(broker): Stale data checksum comparison

Turns out the __data_is_new function in ProgressTracker was broken.
It was checking to see if `data` was in `self.data_checksums`, instead of
`checksum`. Of course the answer was always no and so the data was always
&#34;new&#34;. That meant that every message was new. ([`0db7155`](https://github.com/in03/proxima/commit/0db715559707c6c99a641e38d3a6fa1fffad1652))

* fix(linking): Match proxies properly (#186)

* fix(linking): Use &#39;link_with_mpi&#39; post-encode

Decided to ditch &#39;find_and_link&#39; method for post-encode linking.
Now just passing stringified reference to media pool item through Celery
and re-mapping the original object reference for post-encode link.
Performance is fantastic.

* fix(link_with_mpi): Add prompt_requeue opt arg

Allows handle_existing_unlinked to requeue failed links but prevents
user from getting stuck in an endless loop of post-encode retries.

* fix(linking): Assert 0 proxies remain post-encode

No proxies should remain post-encode without explicitly failing to be
linked. If they do, throw an exception.

* refactor: Update version_constraint_key

* fix(linking): Fail fast if not proxy_media_path

Link function was assigned job proxy_media_path and proxy_status keys to
variables with .get() method, assigning None on KeyError.

Now calling with bracket syntax to fail fast.

* fix(linking): prevent pre-linking all

Prevent &#39;existing unlinked&#39; handler from attempting to link all
in media list when matched media triggers a link routine.

* fix(linking): Fix incorrect proxy output extension

Incorrect output extension was causing linking to fail.

* fix(linking): Fix shallow-copy loophole

Fixed issue with original media_list being altered by list comprehension.

* refactor: Update version_constraint_key

* fix(linking): Iterate and remove skipping items

Every second item wasn&#39;t being linked.
Reversed the media_list to prevent removing items ahead of the loop.

* refactor: Update version_constraint_key

* feat(linking): Add prompt_reiterate option

Add prompt_reiterate method to link_proxies_with_mpi to reiterate
timelines if media_pool_items are &#34;stale&#34;. Essentially the same as
running the existing_unlinked handler without all the setup overhead.

* refactor(linking): Quick filter with linkable type

Replace reversed comprehension with linkable type update for code that
looks better, makes more sense and probably works faster.

* refactor: Update version_constraint_key

* perf(queue): Use zip to iterate two lists at once

Use zip instead of nested for loops

* fix(handlers): restored reverse list sort

Tried to switch from hacky reverse list sort in handle_existing_unlinked.
Still seems like the best way.

* refactor: Update version_constraint_key

* fix(linking): Catch TypeError if project change

Any reasonable way a link fails we need to catch it to mark it as failed.

* feat(linking): Add prompt_reiterate option

 Find_and_link returns linked, failed, allows reiterating timelines if
 media pool items are &#34;stale&#34; and pass on for re-rendering if media is
 corrupt.

* refactor: Update version_constraint_key

* refactor: Update version_constraint_key ([`e1b40b4`](https://github.com/in03/proxima/commit/e1b40b45e89293ad817978c66e63efb15a9dee58))

* fix: Always choose newest existing proxy (#177) ([`4440841`](https://github.com/in03/proxima/commit/44408418e0f4cfb5478cebce8d71b6b268128f26))

* fix: Improved version constraint key generation (#175) ([`91a0262`](https://github.com/in03/proxima/commit/91a0262e7e6ba8f9b2df9836c51e1f4ca2bf4ac2))

* fix: Remove linked proxies from queue (#172) ([`046e595`](https://github.com/in03/proxima/commit/046e595c7b9cf3eab746da5a768dbb197ca6a7a0))

* fix: bug/issue-155/git-sha-slicing (#159) ([`0666a9a`](https://github.com/in03/proxima/commit/0666a9a220c9677cb34009c9238addc18890a220))

* fix: correct bad log-levels

fixes #138 ([`0f33845`](https://github.com/in03/proxima/commit/0f33845bea165cdddf06f482251ac0a37700ae06))

* fix: raise all warning that exit to error ([`c0951cf`](https://github.com/in03/proxima/commit/c0951cf9f006a40d23c82dd1f7fe261baa57fa3b))

* fix(resolve.py): set warning to critical before exits ([`5d3c71d`](https://github.com/in03/proxima/commit/5d3c71d851e67469f2841647409ea225fc46eb59))

* fix: remove extraneous &#39;no worker&#39; warning ([`abcd7a2`](https://github.com/in03/proxima/commit/abcd7a2ba601793bbfa68fe42a5775ba9f77129c))

* fix: unlinked_proxy KeyError (#136)

* what the heck...

* chore: [pre-commit.ci] automatic fixes

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`16a1d35`](https://github.com/in03/proxima/commit/16a1d35e59230ee602b5f5c4419ac3c4abfbb993))

* fix: broken aspect ratio from target resolution rounding error (#135)

* fix(tasks): make orientation detection a function

* fix(tasks): correctly resolve resolution

Using ffmpeg built-in special variable in &#39;scale&#39; filter: `-2:720`

* fix(tasks): remove old get resolution statements

* style(tasks): inconsistent slashes in log path

Inconsistent slashes were annoying to look at (and technically wrong) ([`896c83c`](https://github.com/in03/proxima/commit/896c83c0b7c4eb10cecfa025f09aa82f766b07b1))

* fix(handlers): revert proxy status on link failed (#124) ([`9a5ec13`](https://github.com/in03/proxima/commit/9a5ec1314a4159fe33431496b382525827c9a7dd))

* fix: clip flip detection (#119) ([`685dd64`](https://github.com/in03/proxima/commit/685dd64f88d37a06a39c51e0094fdc9e5d3e3511))

* fix(handlers): handle zero queueable properly

Fixes issue #114 ofc... ([`f4f8f62`](https://github.com/in03/proxima/commit/f4f8f629c4596c615db9333e90baf7560f149f37))

* fix: Recognise offline but relinkable proxies (#113) ([`491e29d`](https://github.com/in03/proxima/commit/491e29d2f1a069c78e66217abce980f06b45f166))

* fix: Offline proxy handler prints whole job obj (#111) ([`497824e`](https://github.com/in03/proxima/commit/497824e9ec6c348a44b6ba22ad5126a4d7226e6f))

* fix(CLI): Address printing incorrect queue name (#109) ([`50cc3d0`](https://github.com/in03/proxima/commit/50cc3d01c44533b0aefed007c467b173e528ab08))

* fix: address multiple broken features post-merge

BREAKING CHANGES:
- incorrect git-sha slicing fixed - routing key formatting has changed!
- worker queue key error fixed: tried to call local var from new process

OTHER:
- post-encode linking now works
- link speed greatly improved after removing redundant timeline searches
- linking stdout formatting improved
- all modules now following `user_settings.yml` app -&gt; loglevel ([`23a4804`](https://github.com/in03/proxima/commit/23a4804c53d3b4d78c15f4913856f88699c50225))

* fix(celery): fix wrong module path, unregistered task ([`01ab218`](https://github.com/in03/proxima/commit/01ab218266968d5beb987689454ac9be43b13728))

* fix: remove unused import &#39;icecream&#39; ([`6cd1da0`](https://github.com/in03/proxima/commit/6cd1da01f84242f96d16c6f57e77aeeb65069f58))

* fix: add missing ffmpeg library ([`a8f768a`](https://github.com/in03/proxima/commit/a8f768a3a9ac9948f8b91038e213adda9c80622e))

* fix: bug/issue 25 (#94)

* feat: start substitute default settings in ensure_keys

* feat: prompt sub missing settings instead of warn

This is really a final enhancement to the #25 &#39;Handle Missing Keys&#39;
issue. We can now substitute missing settings with default app values,
or we can type a new custom value in, all on initial app startup.

FUTURE CONSIDERATIONS:
If configuration management were to become more important in future,
the following may need to be addressed:

- If a whole section is missing with an inline comment, a different
function parses the diff to the usual. Some of this code could be better
shared with the main function. There&#39;s currently minor inconsistency.

- Missing settings are declared as `root[&#39;app&#39;][&#39;loglevel&#39;]`. This could
be more human readable. e.g. `app -&gt; loglevel`

- Expected custom values are not parsed or validated properly. They&#39;re
just taken as is.

- If a whole setting section is missing. The default value is an
ordereddict of all the missing nested key/vals within.
This isn&#39;t human readable and it&#39;s **definitely** not possible to type
out a single custom value to represent that whole structure,
instead each nested key/val within should be iterated one-by-one.

- This would all be necessary if we wanted to add a config command to
the CLI, but surely YAML is easy enough. ([`0e43505`](https://github.com/in03/proxima/commit/0e4350577797d0c4c75b0e1f2998370274b00916))

* fix: implement chunked encoding

- major project restructuring and renaming
- send calculated chunk data with job data to celery task
- create new `encode_chunk` celery task
- maintain source aspect ratio, match user set vertical resolution
- inherit timecode from Resolve clip attributes, no probing file

Still need to implement post-encode concat, moving, cleanup, link.
Unsure how to separate standard &#39;chunkless&#39; encodes with no
concat callback and chunked encodes with. May have to have an
intermediate worker task that runs chunked encodes on another worker
and gathers results asynchronously. ([`4eaaf02`](https://github.com/in03/proxima/commit/4eaaf02ec3f66143f5d871d81ebe332d94b537c8))

* fix: more package structural improvements

- merge last changes from main
- relative imports where possible
- add app level settings
- rework logger (previously reinitialised per-module)

BREAKING CHANGES:
- restructure settings, app-level and worker-level
- remove unnecessary &#39;settings&#39; keyword where present
- remove setting section keyword where present, e.g. &#34;celery_settings&#34; ([`b9d9a35`](https://github.com/in03/proxima/commit/b9d9a357f30dd8cbfc7f77644c53997f7cb4a580))

* fix: major project restructuring

BREAKING CHANGE ([`7a37143`](https://github.com/in03/proxima/commit/7a37143ef2824dc1064c40b4db9cc5d9c7efe1e1))

* fix: corrected broken module imports ([`06d3790`](https://github.com/in03/proxima/commit/06d3790d3df4fcab741c44c6a87523df6ff467a6))

* fix: restructured package, renamed files ([`9e59f86`](https://github.com/in03/proxima/commit/9e59f86ff53187de49e5bd041de3aa22cba4b274))

* fix: tidy up unused imports ([`27935c6`](https://github.com/in03/proxima/commit/27935c6fd7a92caeeaf0edda9f6f337db8c45b08))

* fix: Bug/issue 49 (#59)

* fix: Start on inaccessible worker in pipx install

* fix: call Celery &amp; worker module from within venv

- Adds support for virtual environment isolated installations
like **pipx**. Of course there&#39;s no way to test this without committing
and installing, so here&#39;s hoping!

- Better cross platform support, since this is shaping up to be the only
easy way to start workers in isolated environments. (Also untested. SOZ)

Addresses #49

* fix: correctly launch worker from within pipx venv

Can confirm that workers are now launchable when installed as an
isolated virtualenv, traditional global installation and when run
&#34;non-installed&#34; from Poetry.

Addresses #49 ([`626c892`](https://github.com/in03/proxima/commit/626c892fc4e4a45444e4856ec439d75537128053))

* fix: remove unused imports in app_settings ([`f544e55`](https://github.com/in03/proxima/commit/f544e55b2dab39e30393a13bed36d352796394b5))

### Refactor

* refactor: Update version_constraint_key ([`e4641bb`](https://github.com/in03/proxima/commit/e4641bbd57cc4aa41443a1dc54866dcfb23b0afb))

* refactor: Update version_constraint_key ([`44373ff`](https://github.com/in03/proxima/commit/44373ffb9995bfd0723692af4146fd7d9cafb01c))

* refactor: Update version_constraint_key ([`30b8f71`](https://github.com/in03/proxima/commit/30b8f717c79a5671ca40dc6dbe48544925a4b1ec))

* refactor: Update version_constraint_key ([`8cbc561`](https://github.com/in03/proxima/commit/8cbc5614c82e3cd7e8cd5340659e82bad0092a3f))

* refactor: Comment WIP code for now ([`b9af9a3`](https://github.com/in03/proxima/commit/b9af9a379015ae55deb80979fc76ad96de18ea52))

* refactor: Update version_constraint_key ([`683197f`](https://github.com/in03/proxima/commit/683197f59ab785e9500bbf44770bef47f3aeee1c))

* refactor: Incorrect loglevel for git check ([`9ef909f`](https://github.com/in03/proxima/commit/9ef909f8448b87f85f74696dec70ffca87217786))

* refactor: Update version_constraint_key ([`b382a90`](https://github.com/in03/proxima/commit/b382a907e156428ec2d01bd5dcc58350c47ca0b3))

* refactor: Update version_constraint_key ([`d5b0c84`](https://github.com/in03/proxima/commit/d5b0c8441977b6e52faad3f214216d4fbaecbe85))

* refactor: Update version_constraint_key ([`82f7fb7`](https://github.com/in03/proxima/commit/82f7fb75e8bf946dbaa9cb250d7cff4732f53dab))

* refactor: Extraneous import ([`989272f`](https://github.com/in03/proxima/commit/989272f362633e25eb9e160a6fb3d2230acc81fb))

* refactor: Update version_constraint_key ([`c5a4db8`](https://github.com/in03/proxima/commit/c5a4db81d6eb21f8bf174deefadc90ddb5944138))

* refactor: Tidy up dead code ([`ea0817f`](https://github.com/in03/proxima/commit/ea0817f337cb10231d7ee3abe51e66c547adc75c))

* refactor: demote logfile func with messy sideffects ([`53901e5`](https://github.com/in03/proxima/commit/53901e56adaba3413871fb60d92e4576424617f0))

* refactor: demote logfile func with messy sideffects ([`42ca1ec`](https://github.com/in03/proxima/commit/42ca1ec33926ca5a7fb7118d32c935d7fb25e2cc))

* refactor: Unified logger instead of module-level loggers ([`8211999`](https://github.com/in03/proxima/commit/821199980d767838c8a88a3bee71a7696b8cf550))

* refactor: Update version_constraint_key ([`ecc76db`](https://github.com/in03/proxima/commit/ecc76dbfca3225eb4a112ab1091ee62e8b1ad3ed))

* refactor(batch): Flat is better than nested ([`62c55c3`](https://github.com/in03/proxima/commit/62c55c3178452dbbc774aeb6447c4158045ab883))

* refactor: Update version_constraint_key ([`d643e5c`](https://github.com/in03/proxima/commit/d643e5c4b63bd253ce3da20a9f6eb49f6b6fd1cc))

* refactor: Update version_constraint_key ([`2682daa`](https://github.com/in03/proxima/commit/2682daa8d97982708338585ccbe607dd7d5d99e9))

* refactor: Update version_constraint_key ([`e7567ec`](https://github.com/in03/proxima/commit/e7567ec27b5750af7f4e407471c08a519bec324a))

* refactor: Update version_constraint_key ([`05547e0`](https://github.com/in03/proxima/commit/05547e0de83224b2fceef0348d5f6fcd99126539))

* refactor: Update version_constraint_key ([`52aee81`](https://github.com/in03/proxima/commit/52aee814b6345e845cb7188da126fa723b96d306))

* refactor: Update version_constraint_key ([`d5ed4e6`](https://github.com/in03/proxima/commit/d5ed4e66d33de27ef73bd662f3403c9891ad5975))

* refactor: Typer launch &gt; webbrowser ([`bb4a12e`](https://github.com/in03/proxima/commit/bb4a12e95a0e0944a6e51522bd9e82d6ba017142))

* refactor: Update version_constraint_key ([`ffc44ca`](https://github.com/in03/proxima/commit/ffc44ca7e79f8c7237cfd5e04951d3595329ccac))

* refactor: Update version_constraint_key ([`cdbde73`](https://github.com/in03/proxima/commit/cdbde7371589b4bc9322e30c3eb06dba6704b631))

* refactor: Update version_constraint_key ([`31cde43`](https://github.com/in03/proxima/commit/31cde430e793c030e6a12c111d0fb2fd9574ae15))

* refactor: Update version_constraint_key ([`7be82ca`](https://github.com/in03/proxima/commit/7be82caad1faf760bbb82283cbe2675f065759cc))

* refactor: Update version_constraint_key ([`f7a61dd`](https://github.com/in03/proxima/commit/f7a61dd55910ce4d9d70a61332dea94e6e53e314))

* refactor: Update version_constraint_key ([`1627375`](https://github.com/in03/proxima/commit/16273751f742f132270e83b6d13016a81014af53))

* refactor: Update version_constraint_key ([`517cb5d`](https://github.com/in03/proxima/commit/517cb5d3d1ac55f3371283bd2823c2da68d2f54d))

* refactor: Update version_constraint_key ([`f2d55e4`](https://github.com/in03/proxima/commit/f2d55e42b3c0056ecca5886dff1a147d32d36412))

* refactor: Update version_constraint_key ([`447ce33`](https://github.com/in03/proxima/commit/447ce330ef18be9e3da9fbd2cd648276f3f6612d))

* refactor: Update version_constraint_key ([`e2ad2c8`](https://github.com/in03/proxima/commit/e2ad2c82c865acade10d8ebd928708781ba61898))

* refactor: Update version_constraint_key ([`a2f2f74`](https://github.com/in03/proxima/commit/a2f2f740586bc637ec48027caf203ecbcb372c6a))

* refactor: Update version_constraint_key ([`ef737eb`](https://github.com/in03/proxima/commit/ef737eb3c070af17d7311ce7b417a83c265a61be))

* refactor: Update version_constraint_key ([`65bed95`](https://github.com/in03/proxima/commit/65bed95d4bd89869252d902dc96ea362183621d1))

* refactor: Swap Redis PubSub for Celery AsyncResult and custom states (#228)

* Create draft PR for #224

* feat(link): Add exception info if all fail link

* refactor: Group ID as Redis channel ID

* refactor: Update version_constraint_key

* refactor: MVP Redis PubSub

* refactor: Update version_constraint_key

* refactor: Tidy deeply nested modules

* refactor: Update version_constraint_key

* fix: Remove new data flag, recalc every loop

Now just calculating progress and task info every iteration of the loop
instead of checking new data flags. It looks like there may be a race
condition of some sort causing inaccurate worker numbers.

I might consider thread locks if they work with Redis&#39; pubsub run_in_thread.

* refactor: Update version_constraint_key

* refactor: Dropped direct Redis usage altogether

Alright, this is kind of funny. Turns out I&#39;ve been reinventing the wheel
this whole time. Celery&#39;s GroupResult contains AsyncResult instances with
all the data we need to get active worker count, task completion and
task encoding progress (with a custom task state definition).

So:
- dropped Redis database polling
- dropped Redis PubSub
- use unique worker IDs instead of sequential prefix to easily start
additional workers at any time

* refactor: Update version_constraint_key

* docs: Update README.md

* build: Export updated requirements.txt

* refactor: Update version_constraint_key ([`92f1747`](https://github.com/in03/proxima/commit/92f1747fdcd53b6d1d15acfad8ef039e06285a02))

* refactor: Update version_constraint_key ([`bb515fe`](https://github.com/in03/proxima/commit/bb515fe4f54e4e949956806546cc01247ae15768))

* refactor: Update version_constraint_key ([`cfa9e3b`](https://github.com/in03/proxima/commit/cfa9e3bcf366a81c316b71ef53cb0fc0e9c06b44))

* refactor(launch_workers): Change is with literals to &#39;==&#39; ([`bfce685`](https://github.com/in03/proxima/commit/bfce685c566d98e61935d7ba2a27e0414b3d1778))

* refactor: Update version_constraint_key ([`0bfda1f`](https://github.com/in03/proxima/commit/0bfda1fc89fad239fcd4848d9e29714f52ca9ac2))

* refactor: Update version_constraint_key ([`aa372cd`](https://github.com/in03/proxima/commit/aa372cdcafb7c62baf68fda5c0bfef6e9cd4dd2f))

* refactor: Update version_constraint_key ([`ceb6d9e`](https://github.com/in03/proxima/commit/ceb6d9e3003dcb39ba1fd2d31b6ca07394deef55))

* refactor: Update version_constraint_key ([`dea40d6`](https://github.com/in03/proxima/commit/dea40d6b7b74b0dd4b9a65bcfe38e519ed66a9b9))

* refactor: Update version_constraint_key ([`743df9a`](https://github.com/in03/proxima/commit/743df9a64aea143bacd29ce9372d367d1e80ba1f))

* refactor: Update version_constraint_key ([`84250ae`](https://github.com/in03/proxima/commit/84250ae05621ab4a7ce5f25f8cb3a911ae05c6b8))

* refactor: Update version_constraint_key ([`9881228`](https://github.com/in03/proxima/commit/9881228405b5dfd9f52f83e219a163c6f388f926))

* refactor: Update version_constraint_key ([`f542afe`](https://github.com/in03/proxima/commit/f542afe7158b59f6ccf67257320666a247a034cd))

* refactor: Update version_constraint_key ([`0a23453`](https://github.com/in03/proxima/commit/0a234533d5ff3b31e192bfb4dee46cf44778a0d1))

* refactor: Update version_constraint_key ([`d214d9a`](https://github.com/in03/proxima/commit/d214d9a3598717ac832a64fa3091b920d9b2286c))

* refactor: Update version_constraint_key ([`fa00b5a`](https://github.com/in03/proxima/commit/fa00b5a1929cae81e2653f6d79aa2881c1ccf140))

* refactor: Update version-constraint key ([`b6caa5e`](https://github.com/in03/proxima/commit/b6caa5e283f8e9154e468c99740bd0da949271de))

* refactor: Update version-constraint key ([`4026412`](https://github.com/in03/proxima/commit/40264124744ce38f201890836218778256164cbb))

* refactor: Update version-constraint key ([`ac43d05`](https://github.com/in03/proxima/commit/ac43d05b91763a5ea6448de1ba8ded0ec84e9e06))

* refactor: Update version-constraint key ([`4545e7e`](https://github.com/in03/proxima/commit/4545e7eabc10871540920e279111c5e52b089a4f))

* refactor: Update version-constraint key ([`6a6e88d`](https://github.com/in03/proxima/commit/6a6e88d37cd3ea6679abc0d726d862cf1cec1256))

* refactor: Update version-constraint key ([`1aa7bbf`](https://github.com/in03/proxima/commit/1aa7bbfdc0fc5725d755f1d576b2d809d9559a09))

### Style

* style: Consistent loglevel color ([`c0d66c4`](https://github.com/in03/proxima/commit/c0d66c4b389f6d66f4479441956f2d8b8b236518))

* style: Remove stray print ([`7f8921b`](https://github.com/in03/proxima/commit/7f8921bc0faaf34558e56311cadba23f8df7e9fb))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/in03/proxima ([`27312ea`](https://github.com/in03/proxima/commit/27312ea2b4fabbb48eed4f3be8e0e47515b2c208))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`fb2c851`](https://github.com/in03/proxima/commit/fb2c851ec242fcc0ab6505bd85cf0abdc7fb99d5))

* revert: &#34;fix(job): Incorrect loglevel&#34;

This reverts commit b90ade1b58e91e2fbf3d80aa25835a10a365e595. ([`51d05a9`](https://github.com/in03/proxima/commit/51d05a9397aab2be4d0aa2122d9cd5a27c1ed14d))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`b74f969`](https://github.com/in03/proxima/commit/b74f969c08b87b5c450230412867d52ce24d80e9))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`e2db3c2`](https://github.com/in03/proxima/commit/e2db3c28bdfd73d0be1e31f2243c182f46a05f2b))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`8eabf89`](https://github.com/in03/proxima/commit/8eabf89f9d17c5fa78544603a9f86d2e94db068b))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`265c3ea`](https://github.com/in03/proxima/commit/265c3ea485b55dce1e84a432951cd10a69f3aaae))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`7afd43f`](https://github.com/in03/proxima/commit/7afd43f63042f1b8cd487fce6b56f170424c40b2))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`9ab8f15`](https://github.com/in03/proxima/commit/9ab8f158dd179f38216b18f31b6bc55ae12b73ab))

* Refactor job dict object as Class (#234) ([`cf93b40`](https://github.com/in03/proxima/commit/cf93b401c29e8bc1eddc866ad8f9c6965c366808))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`e780151`](https://github.com/in03/proxima/commit/e7801515aafbd0a1a03e73a24704d079c323c2cd))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`23c0378`](https://github.com/in03/proxima/commit/23c037805efc4498be1b42bb28c05b45ea489589))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`ab937d7`](https://github.com/in03/proxima/commit/ab937d7d70bd54900afba740a1184cd35ea0ac24))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`c415767`](https://github.com/in03/proxima/commit/c4157677faee994b4ba5abd7adbc5aacbf7ee822))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`ea3f33b`](https://github.com/in03/proxima/commit/ea3f33b924a0d62bd8f49c7cf79f1a4a5b9864de))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`3da42d7`](https://github.com/in03/proxima/commit/3da42d7c29b77e42b26460bfbbd1d7409c05d10d))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`0af24cc`](https://github.com/in03/proxima/commit/0af24cce1988d3b6fb88de5819e5369e7150666a))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`8bf662d`](https://github.com/in03/proxima/commit/8bf662d0fa7cbe1e85fbfbe2ff81badfd4410010))

* bump: Update application semver ([`8f5827b`](https://github.com/in03/proxima/commit/8f5827b0d8acb00ad1d141098745699194a0df96))

* bump: Update all dependencies ([`5ae3839`](https://github.com/in03/proxima/commit/5ae38390c6500d51a4874faf6c393051235834ae))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder ([`2586963`](https://github.com/in03/proxima/commit/25869634a69722c2247707f136c1c806635ef395))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder ([`0fa14da`](https://github.com/in03/proxima/commit/0fa14da734af2e21069a90429bffab4761b83448))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder ([`bf91f9d`](https://github.com/in03/proxima/commit/bf91f9de77921238c36f2264822487d2a6194b92))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder ([`868b60f`](https://github.com/in03/proxima/commit/868b60f6ec3de3556cbfaf20f4195731ab73dd12))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`123e94b`](https://github.com/in03/proxima/commit/123e94b21ad636cf9f2507767b179a542345e8ab))

* build(cli.py) remove unused import &#39;merge_args&#39; ([`fc8891e`](https://github.com/in03/proxima/commit/fc8891e2ad62812836c65b1817c1b179eb026837))

* Merge pull request #116 from in03:bug/issue114

fix(handlers): handle zero queueable properly ([`e20ac1d`](https://github.com/in03/proxima/commit/e20ac1d8749e51929210edccf046eba07f06970b))

* Feat/issue103 (#107)

* feat(handlers): Swap TK msgbox to console prompts

Addresses #103

- Also addressed issue with multiple online Celery worker checks

* feat(formatting): improve console output / logging ([`1661dc7`](https://github.com/in03/proxima/commit/1661dc7a2de0390480117bceb0b42dec02562b54))

* Merge branch &#39;feature/issue-9&#39; of https://github.com/in03/resolve-proxy-encoder ([`cd83c7e`](https://github.com/in03/proxima/commit/cd83c7ec2b002a5cd1994817bc45051a93f0fdcf))

* Update README.md ([`4b65272`](https://github.com/in03/proxima/commit/4b65272b7e35c8dd8752482099620092fd34f75d))

* [pre-commit.ci] pre-commit autoupdate (#63)

updates:
- [github.com/psf/black: 21.12b0 → 22.1.0](https://github.com/psf/black/compare/21.12b0...22.1.0)

Co-authored-by: pre-commit-ci[bot] &lt;66853113+pre-commit-ci[bot]@users.noreply.github.com&gt; ([`cd44050`](https://github.com/in03/proxima/commit/cd44050de700933578a9e0c6d90085983c33ea3e))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder ([`cc8cef7`](https://github.com/in03/proxima/commit/cc8cef7c9d9198ee46bf8204510c9abcefe8e231))

* Update workflow.yml ([`7fecfbe`](https://github.com/in03/proxima/commit/7fecfbe4f7abf660a4d305b40afe62611a2b1a7d))

* FIX: Improved settings validation console logging ([`eea5feb`](https://github.com/in03/proxima/commit/eea5feb4be8bed6d5334244b7eff2d998370838d))

* FIX: user settings read before file exist check ([`d90be7b`](https://github.com/in03/proxima/commit/d90be7b268e5de97d324ca8f5d1fdfbc7ccf17f4))

* Merge pull request #35 from in03/bug/issue-25

Bug/issue 25 ([`73c0519`](https://github.com/in03/proxima/commit/73c0519b997e9fda4a7b9de67cb64e38a88e3ac2))

* Merge branch &#39;main&#39; into bug/issue-25 ([`07ec680`](https://github.com/in03/proxima/commit/07ec6800a31f9ff878031e6593f415c103b108e3))

* Fix settings across modules ([`fa80b61`](https://github.com/in03/proxima/commit/fa80b619e69a797ac3000252262b44d686fdd4bf))

* Settings validation working, keys ensured to exist ([`019d9ef`](https://github.com/in03/proxima/commit/019d9efdbb7e0f79b22e3b9ec8105a254bc3a9ac))

* Merge pull request #31 from in03/pre-commit-ci-update-config

[pre-commit.ci] pre-commit autoupdate ([`9b4c06d`](https://github.com/in03/proxima/commit/9b4c06d77bee83cfe881251bf36d3805680cc212))

* Schema now working, still working on missing keys ([`8b60199`](https://github.com/in03/proxima/commit/8b60199a3aa44f45d712b8530179aa6cec142f18))

* added quote to numbers in yaml to force int ([`2fb5bdc`](https://github.com/in03/proxima/commit/2fb5bdca66ff851cddc60f094a7dd4faa70cded0))

* Started progress bars, fixing timecode match issue ([`5bf51ca`](https://github.com/in03/proxima/commit/5bf51ca8a2bdeed59ff69d156e4c84889bfb2d3d))

* Started on schema validation and missing key check ([`aa321ef`](https://github.com/in03/proxima/commit/aa321ef2c0ab4b5743492bd056cd00bb9bf1c603))

* [pre-commit.ci] pre-commit autoupdate

updates:
- [github.com/pre-commit/pre-commit-hooks: v4.0.1 → v4.1.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.0.1...v4.1.0)
- [github.com/pre-commit/pre-commit-hooks: v4.0.1 → v4.1.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.0.1...v4.1.0) ([`4bca0fa`](https://github.com/in03/proxima/commit/4bca0faa839a4f9a8074632c9f501a2efe4843c8))

* Started on better config management ([`a975e21`](https://github.com/in03/proxima/commit/a975e21f8bb9e97ed85129b6bf74069ca2095c79))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`35e95b1`](https://github.com/in03/proxima/commit/35e95b1a1c88e4890449e1d4f1592a3032ff0a1b))

* FIX: file collisions + heaps else ([`d4c9b38`](https://github.com/in03/proxima/commit/d4c9b382e004e0caf3c890defd046975c311e28f))

* Update ci-docs.yml ([`78daff3`](https://github.com/in03/proxima/commit/78daff301c5377e6c0a29657314fa05e7a171390))

* Update and rename ci.yml to ci-docs.yml ([`f6a8e6e`](https://github.com/in03/proxima/commit/f6a8e6e837beb8e01b0bf2e915d64133c5c46a84))

* Merge pull request #30 from in03/pre-commit-ci-update-config

ci: [pre-commit.ci] pre-commit autoupdate ([`466ac93`](https://github.com/in03/proxima/commit/466ac93b89b8b0f0ff67bd5daa2b4d66ad595f7b))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`04f7850`](https://github.com/in03/proxima/commit/04f78500b35eb9d1d63d0b0f6bb3d98802c24e68))

* Increment existing proxies instead of overwrite ([`aa97d37`](https://github.com/in03/proxima/commit/aa97d3736ace16f455a45e181b10f0dcb2376b0d))

* [pre-commit.ci] pre-commit autoupdate

updates:
- [github.com/pre-commit/pre-commit-hooks: v2.5.0 → v4.0.1](https://github.com/pre-commit/pre-commit-hooks/compare/v2.5.0...v4.0.1) ([`eeb0f29`](https://github.com/in03/proxima/commit/eeb0f29c1afb6585a77814f09673ddfb6a60af09))

* Update README.md ([`723ea58`](https://github.com/in03/proxima/commit/723ea5879a13f47c4b141bc652c98992a97f8d7f))

* Added better Resolve API object checks ([`8d8fae4`](https://github.com/in03/proxima/commit/8d8fae4009f79211f1f66eae2a537d5f980cf1d0))

* Merge branch &#39;main&#39; of https://github.com/in03/resolve-proxy-encoder into main ([`8dd3e9f`](https://github.com/in03/proxima/commit/8dd3e9f700e063e86f9c66d4ddaa1d392cf2913e))

* Implemented pre-commit hooks ([`7ed294c`](https://github.com/in03/proxima/commit/7ed294c41468a2e84580cc1421f46fa41875e9d4))

* Update README.md ([`52467e0`](https://github.com/in03/proxima/commit/52467e00122e0aa87d3d95c974f77cdc400671b4))

* Merge pull request #28 from in03/bug/issue-27

Fixed bug/issue-27 ([`dbd1927`](https://github.com/in03/proxima/commit/dbd1927adc3f6d830f12fa10656f1557e86024e7))

* Fixed bug/issue-27 ([`67e5485`](https://github.com/in03/proxima/commit/67e5485dac3e59ac8c8d80a324afc0445f158105))

* Fixed purge command ([`524612a`](https://github.com/in03/proxima/commit/524612a5476c51034d6e07a3c54209862e2a6cd8))

* fixed stray debug print, unregistered task ([`6ee3635`](https://github.com/in03/proxima/commit/6ee36351d2c79180a2825d4fedfe3bc89659c01a))

* Merge pull request #24 from in03/bug/issue-21

fixed icecream dependency import error ([`b77f5e3`](https://github.com/in03/proxima/commit/b77f5e388a3add0a9bfce7f0afe926ce48ab930c))

* fixed icecream dependency import error ([`7c33b01`](https://github.com/in03/proxima/commit/7c33b0188cd63a69228ab15d4b13442ae2ef4bfa))

* Merge pull request #23 from in03/bug/issue-21

Detect offline proxies, updated docstrings ([`62e7a50`](https://github.com/in03/proxima/commit/62e7a508a42d291fb811c3aa83f07281014d57ad))

* Detect offline proxies, updated docstrings ([`fe7ba83`](https://github.com/in03/proxima/commit/fe7ba83f0152193bd9b3788ec1c480ab146bda60))

* Merge branch &#39;main&#39; of https://github.com/in03/Resolve-Proxy-Encoder into main ([`d880daf`](https://github.com/in03/proxima/commit/d880daf003fb279e885a8241cfd16d049ba4ebe1))

* Merge pull request #18 from in03/dev

Merge dev updates to main ([`617a839`](https://github.com/in03/proxima/commit/617a83949764f8055efde90ce089ec2cc8e33de6))

* Merge branch &#39;main&#39; into dev ([`01c245c`](https://github.com/in03/proxima/commit/01c245c0bcda8832713a6f37e2a6de5f219c51ad))

* Merge branch &#39;dev&#39; into main ([`2db768c`](https://github.com/in03/proxima/commit/2db768ccd4c4d0720f46a5403c69f376fbc21822))

* Update README.md ([`890ca83`](https://github.com/in03/proxima/commit/890ca83e42d940e2978f539b80d3d6bbb30b93ce))

* Started docs ([`6c805cb`](https://github.com/in03/proxima/commit/6c805cbda1ff4988140be7d0824e8092ea3877b6))

* Added ability to call scripts directly to test ([`04cbb00`](https://github.com/in03/proxima/commit/04cbb00401f03ae1721467f867a160f0ee96cfbb))

* Moved fragile config settings to code ([`23b6562`](https://github.com/in03/proxima/commit/23b6562dc6f61f1bdb14a27709b1f587d4753e03))

* Fixed worker glitches, can start standalone ([`4b08d4e`](https://github.com/in03/proxima/commit/4b08d4eed530ffe445655c01702f2c48a5457f23))

* Updated default_settings Celery worker config ([`b2b3f9a`](https://github.com/in03/proxima/commit/b2b3f9aef1e0ffe92a76e9262e0f4b3d8ff19a79))

* Fixed initial settings error if no ./config dir ([`e97baef`](https://github.com/in03/proxima/commit/e97baef00b4b35d8a23a592ff09c360587ea3e30))

* Deleted old docker files ([`ca6e47c`](https://github.com/in03/proxima/commit/ca6e47cb98ad9450c033746d4bcab1bf10950975))

* Restructured package and updated terminology ([`c933412`](https://github.com/in03/proxima/commit/c933412cd3719b6a891fbccd115a0a9e3c527fa5))

* Cleanup LAUNCHING + dots in start_workers ([`1947cac`](https://github.com/in03/proxima/commit/1947cac5f06d56224b6bab898cb37b8ee385cc0e))

* Fixed &#39;some_action_taken&#39; undefined var ([`1b4fad8`](https://github.com/in03/proxima/commit/1b4fad83a79d3e2ed60a3952702d379ba24cbf22))

* Follow XDG Base Directory Specification ([`684dc56`](https://github.com/in03/proxima/commit/684dc56ab33a1302d8ed8302a7e520b08c378a5a))

* Merge branch &#39;main&#39; of https://github.com/in03/Resolve-Proxy-Encoder into main ([`389bb5e`](https://github.com/in03/proxima/commit/389bb5ec0d60611af33592184044f04a8de193d8))

* Fixed missing action taken flag ([`089eff2`](https://github.com/in03/proxima/commit/089eff266c91f16491acd1244058acb4da529c71))

* Update README.md ([`33a1adf`](https://github.com/in03/proxima/commit/33a1adfef78575c3819286af6e0d32019fdcb590))

* Update README.md ([`15930b2`](https://github.com/in03/proxima/commit/15930b2fd732a69d6b9d919b1cd5bd947248ec65))

* Update README.md ([`0d81e51`](https://github.com/in03/proxima/commit/0d81e51a511885118e1ed95d04053ca5364e995b))

* Better error handling for PyRemoteObjects ([`773b03a`](https://github.com/in03/proxima/commit/773b03ac886e61778e49a536a80cbd2ac52849bf))

* Internalised Resolve API import error ([`6357e09`](https://github.com/in03/proxima/commit/6357e0997af0195de3a9a19ccb42624a966046fd))

* Added import warning for Resolve API ([`6670b9c`](https://github.com/in03/proxima/commit/6670b9c67a19051abca96cdef10d199ebd507245))

* Fixed start_workers and celery app ([`3766d38`](https://github.com/in03/proxima/commit/3766d38b4742135da2d3e8e8c7d3ae2f52c442b4))

* Fixed loglevel error ([`dce36de`](https://github.com/in03/proxima/commit/dce36deb70680383393e4afe76d38ae48108ec0e))

* Fixed Resolve API access error

- Fixed Resolve API NoneType error
- Added missing dependency Redis
- Reworked clunky imports
- Moved common functions to helpers
- Settings check on import ([`ea5cab7`](https://github.com/in03/proxima/commit/ea5cab73e6d9eac671e81b33fa51bf02a083b9a2))

* Update cli.py ([`55bcf56`](https://github.com/in03/proxima/commit/55bcf5652f1d135db9a8fc27b47c459bb5d9e596))

* CLI update ([`65d1219`](https://github.com/in03/proxima/commit/65d12191a02c555b08be88b0a8de3823b6084ec2))

* Fixed more relative import errors ([`a3ca2d3`](https://github.com/in03/proxima/commit/a3ca2d3d707af112a9ae703ba54a75bdabf8d095))

* Fixed relative import errors ([`b73460a`](https://github.com/in03/proxima/commit/b73460a1b1438b28efdd12ad78af8522e4dbd058))

* Merge branch &#39;main&#39; of https://github.com/in03/Resolve-Proxy-Encoder ([`fa45b3c`](https://github.com/in03/proxima/commit/fa45b3c665dc4357bc2d055540dfa6b521baf69b))

* Initial package format testing

- Made into Python package
- CLI with Typer
- Using Poetry ([`4d1f19a`](https://github.com/in03/proxima/commit/4d1f19aefe77648970d35ec1c3b4828e734b633d))

* Delete RESOLVE_queue_proxies-old.py ([`f939587`](https://github.com/in03/proxima/commit/f9395875d43c0cc4a66c2234bd023eb370d900c3))

* Merge pull request #8 from in03/dependabot/pip/pywin32-301

Bump pywin32 from 300 to 301 ([`4ac9697`](https://github.com/in03/proxima/commit/4ac9697eef49b52a80cc656dccc6d96a9b2aab4e))

* Delete Link Proxies pseudocode.rtf ([`35158d6`](https://github.com/in03/proxima/commit/35158d626030a3ab33fa0a62f1ddcdbf162ea621))

* Bump pywin32 from 300 to 301

Bumps [pywin32](https://github.com/mhammond/pywin32) from 300 to 301.
- [Release notes](https://github.com/mhammond/pywin32/releases)
- [Changelog](https://github.com/mhammond/pywin32/blob/main/CHANGES.txt)
- [Commits](https://github.com/mhammond/pywin32/commits)

---
updated-dependencies:
- dependency-name: pywin32
  dependency-type: direct:production
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`ad371af`](https://github.com/in03/proxima/commit/ad371af2c5081efecff97b6b9b2267f3a4741ad2))

* Reverted changes. Got too messy. ([`3989b31`](https://github.com/in03/proxima/commit/3989b31fe673329caaed1af9dea4e87e36f92108))

* Revert &#34;Trying to include Settings_Manager&#34;

This reverts commit 497851460a41df706968913819162a39c06eded4. ([`bf1bae8`](https://github.com/in03/proxima/commit/bf1bae8fd6854448931b593d8b651e4ba99fd715))

* Trying to include Settings_Manager ([`4978514`](https://github.com/in03/proxima/commit/497851460a41df706968913819162a39c06eded4))

* Fixed linking

 - Implemented old linking method as legacy_link so we can continue developing post-encode method ([`88d0515`](https://github.com/in03/proxima/commit/88d05156a10d53632788b7268165099c4b36d405))

* Change serializer

- Changed serializer to Pickle, not working yet, will fix
- Passing MediaPoolItem method as object to Celery so we can link only encoded items afterwards instead of searching from scratch ([`0214cd7`](https://github.com/in03/proxima/commit/0214cd72ffd800a7a59e098e705eefcf99f8b5d3))

* Merge branch &#39;main&#39; of https://github.com/in03/Resolve-Proxy-Encoder into main ([`d72c3cb`](https://github.com/in03/proxima/commit/d72c3cb3c6b40cc3c50ad1996fbf6d7d16bfa373))

* Changed to Redis ([`eb578b7`](https://github.com/in03/proxima/commit/eb578b7a512973ee46838cb6888ade28b5136b4f))

* Update README.md ([`bf1ce91`](https://github.com/in03/proxima/commit/bf1ce911c48edb13e1f4b1fa1987ab0245683781))

* Update README.md ([`d8768e6`](https://github.com/in03/proxima/commit/d8768e64ddaa9ee607fbfcb84e56517cbd8c297c))

* Started docker support

- Working on proxy linking logic
- Began docker auto build support ([`4e049a1`](https://github.com/in03/proxima/commit/4e049a11dcf17538b21b4fd99381655b62006c04))

* Fixed virtualenv

- Cleaned up
- Added correct shebangs
- Realised a shared virtualenv over LAN is a terrible idea
- Added requirements.txt
- exit_on_seconds function updated
- Celery launches using default python now. Each worker must be setup using requirements.txt ([`c6b0187`](https://github.com/in03/proxima/commit/c6b0187ac9c739e127098e3c4e2d88875438b0ee))

* post-encode proxy linking

- Automatically link after encode
- Renamed some files and functions to by more line with Celery&#39;s naming conventions
- All scripts work off virtual env now
- Setup flower in container, removed local instance from start_worker.bat ([`5a57c18`](https://github.com/in03/proxima/commit/5a57c183a2667442f816406bd5be052476c41e3f))

* Fixed toast

Toast will fail to show if ascii colour byte in text ([`e59ae19`](https://github.com/in03/proxima/commit/e59ae19b00d38280e01734dc783791506cf2c6a4))

* Receives results

Can now receive job results on host machine ([`a5bbb57`](https://github.com/in03/proxima/commit/a5bbb572bce1b5c52a92bc180f26b5753df896e3))

* Started some_action_taken logic ([`06efb09`](https://github.com/in03/proxima/commit/06efb09ca144ea8b1d60e88a563ba2ca8c54665c))

* Changes to console output ([`af9ca74`](https://github.com/in03/proxima/commit/af9ca7410858abd25c8999e41e42f74cc1570622))

* Minor tweaks ([`db54c42`](https://github.com/in03/proxima/commit/db54c422e9de60dea988797a690cfbaad1c87658))

* Fixed non existing render path bug ([`6d4dfe7`](https://github.com/in03/proxima/commit/6d4dfe7795256c65e7d689aadab4005c20cc3d00))

* Flipping works! ([`afff30e`](https://github.com/in03/proxima/commit/afff30ef2a6d849f3d717e2e59169391e01013ea))

* Actually encodes now! ([`b957a10`](https://github.com/in03/proxima/commit/b957a10c60a930f1dbe566a0b79710ce1e9f1b70))

* Pre notification integration ([`a812e11`](https://github.com/in03/proxima/commit/a812e1152509094bbe69e980ece543661c76e603))

* can&#39;t remember why I need to commit again ([`523191d`](https://github.com/in03/proxima/commit/523191d1473aa2ac7c800d1c735d906de526a9cc))

* Got simulated job working! ([`3836d64`](https://github.com/in03/proxima/commit/3836d64c949a3311766f6953afe248498b200333))

* Minimum viable ([`25a22a1`](https://github.com/in03/proxima/commit/25a22a1868768857a5e19d0c26fa5cd2ac61ce70))

* Initial ([`8094086`](https://github.com/in03/proxima/commit/8094086e953a05fd8c4697b933389de3926b9ef4))

* Initial commit ([`d8617bd`](https://github.com/in03/proxima/commit/d8617bd67fbbeea490f81ef75e8686fde75c12e4))
