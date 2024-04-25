from pathlib import Path

from core.git_processor import (
    BlobData,
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
    async def get_root_tree(self) -> Tree:
        repo = Repo(self.config.repo)
        assert repo
        self.repo = repo
        self.commit = repo.commit(self.commit_sha)
        return self.commit.tree

    async def process_blob(self, blob: Blob, depth: int) -> BlobData:
        if self.config.verbose:
            print(f'{"|" * (depth + 1)}- blob: {blob.path}')

        return BlobData(
            name=blob.name,
            path=str(blob.path),
            content=self.repo.git.show(self.commit.hexsha + ':' + str(blob.path)),
        )

    async def process_tree(self, tree: Tree, depth: int) -> TreeData:
        if self.config.verbose:
            print(f'{"|" * (depth + 1)} tree: {tree.path}')

        blob_datas: list[BlobData] = []
        for blob in tree.blobs:
            blob_datas.append(await self.process_blob(blob, depth))

        tree_datas: list[TreeData] = []
        for subtree in tree.trees:
            tree_datas.append(await self.process_tree(subtree, depth + 1))

        return TreeData(name=tree.name, path=str(tree.path), trees=tree_datas, blobs=blob_datas)
