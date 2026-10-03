from __future__ import annotations

from collections.abc import Iterable

from amauxboze.contracts import PluginManifest, PluginRegistry


class DefaultPluginRegistry(PluginRegistry):
    def __init__(self):
        self._providers: dict[str, object] = {}
        self._manifests: dict[str, PluginManifest] = {}

    def register(self, manifest: PluginManifest, provider: object) -> None:
        if manifest.id in self._providers:
            raise ValueError(f"Plugin already registered: {manifest.id}")
        self._providers[manifest.id] = provider
        self._manifests[manifest.id] = manifest

    def get(self, plugin_id: str) -> object:
        try:
            return self._providers[plugin_id]
        except KeyError as exc:
            raise KeyError(f"Unknown plugin: {plugin_id}") from exc

    def manifests(self) -> Iterable[PluginManifest]:
        return tuple(self._manifests.values())
