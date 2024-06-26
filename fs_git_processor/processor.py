from pathlib import Path
from typing import Any

from core.git_processor import (
    BlobData,
    CommitMeta,
    GitProcessor,
    GitProcessorConfigShape,
    TreeData,
)
from git import Blob, Repo, Tree


class FsGitProcessorConfigShape(GitProcessorConfigShape):
    repo: Path


class FsGitProcessor(
    GitProcessor[FsGitProcessorConfigShape, Tree, Blob], config_shape=FsGitProcessorConfigShape
):
    def __init__(self, config_dict: dict[str, Any], sha: str) -> None:
        super().__init__(config_dict, sha)
        repo = Repo(self.config.repo)
        assert repo
        self.repo = repo
        self.commit = repo.commit(self.sha)

    async def get_root_tree(self) -> Tree:
        return self.commit.tree

    async def process_blob(self, blob: Blob, depth: int) -> BlobData:
        return BlobData(
            name=blob.name,
            path=str(blob.path),
            content=self.repo.git.show(self.commit.hexsha + ':' + str(blob.path)),
        )

    async def process_tree(self, tree: Tree, depth: int) -> TreeData:
        blob_datas: list[BlobData] = []
        for blob in tree.blobs:
            blob_datas.append(await self.process_blob(blob, depth))

        tree_datas: list[TreeData] = []
        for subtree in tree.trees:
            tree_datas.append(await self.process_tree(subtree, depth + 1))

        return TreeData(name=tree.name, path=str(tree.path), trees=tree_datas, blobs=blob_datas)

    async def get_commit_meta(self) -> CommitMeta:
        return CommitMeta(
            author_email=self.commit.author.email,
            committer_email=self.commit.committer.email,
            committed_date=self.commit.committed_datetime,
            authored_date=self.commit.authored_datetime,
            message=self.commit.message,
        )
