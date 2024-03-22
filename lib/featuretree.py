#!/usr/bin/env python3


class FeatureTree:
    """Keys are dot-separated hierarchical feature ids. Nodes with value=None are considered empty."""

    def __init__(self):
        self.children = dict()
        self.value = None

    def get_node(self, feature_id):
        if not feature_id:
            return self
        k, _, subfeature_id = feature_id.partition(".")
        return self.children[k].get_node(subfeature_id)

    def __setitem__(self, feature_id, v):
        if not feature_id:
            self.value = v
            return
        k, _, subfeature_id = feature_id.partition(".")
        if k not in self.children:
            self.children[k] = FeatureTree()
        self.children[k][subfeature_id] = v

    def __getitem__(self, feature_id):
        if not feature_id:
            return self.value
        k, _, subfeature_id = feature_id.partition(".")
        return self.children[k][subfeature_id]

    def descendent_keys(self, prefix=""):
        for k, v in self.children.items():
            ident = f"{prefix}{k}"
            if v.value is not None:
                yield ident
            yield from v.descendent_keys(f"{ident}.")

    def dir(self, prefix=""):
        """List filenames for a sensible directory structure."""

        for k, v in self.children.items():
            feature_id = f"{prefix}{k}"

            # nodes without value -> intermediate directory (implicitly)
            if v.value is None:
                yield from v.dir(f"{feature_id}.")
                continue

            # nodes with value but without children -> a file
            parent_dir = prefix.replace(".", "/")
            if not v.children:
                yield f"{parent_dir}{feature_id}"
                continue

            parent_dir = f"{parent_dir}{k}/"

            # nodes with value and children -> a directory containing itself and all its children (flattened) as files
            yield f"{parent_dir}/{feature_id}"
            for descendent_feature_id in v.descendent_keys(f"{feature_id}."):
                yield f"{parent_dir}/{descendent_feature_id}"
