# UCMA | File System Git Processor Plugin

Git processor plugin, which can be used to analyze a local Git repository.

**Install**

``` bash
poetry add git+https://github.com/Universal-code-metrics-analyzer/fs-git-processor@v0.1.0
```

**Runner configuration**

``` yaml
# config.yml

git_processor:
  plugin: fs_git_processor
  config:
    # a path to Git repository to analyze
    repo: /Users/example/Documents/my-project
```
