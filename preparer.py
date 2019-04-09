import os


class Preparer:

    def __init__(self, preparer_config=None):
        self.config = preparer_config

    def set_config(self, preparer_config):
        self.config = preparer_config

    def prepare(self, client, collection_path_guest, generate_save_tag):
        """
        Builds an image that has been initialized and has indexed the collection.

        The `init` hook is used by the image to perform additional
        initialization tasks (which may be a no-op). The developer is free
        to determine what should be directly baked into the image and what
        should be executed in the init hook.

        The `index` hook is used by the image to index a particular
        collection, which is provided to the script as the first argument
        (`collection_name`). This argument maps into the path
        `/input/collection/collection_name`, where the container can
        expect the document collection to be mounted.
        """

        print("Preparing image...")

        # Mapping from collection name to path on host
        name_to_path_host = dict(map(lambda x: x.split("="), self.config.collections))

        # Mapping from collection name to path in container
        name_to_path_guest = dict(map(lambda name: (name, os.path.join(collection_path_guest, name)), name_to_path_host.keys()))

        volumes = {}

        for name in name_to_path_host.keys():
            path_host, path_guest = name_to_path_host[name], name_to_path_guest[name]
            volumes[path_host] = {
                "bind": path_guest,
                "mode": "ro"
            }

        # The first step is to pull an image from an OSIRRC participant,
        # start up a container, run its `init` and `index` hooks, and then
        # use `docker commit` to save the image after the index has been
        # built. The rationale for doing this is that indexing may take a
        # while, but only needs to be done once, so in essence we are
        # "snapshotting" the system with the indexes.
        base = client.containers.run("{}:{}".format(self.config.repo, self.config.tag),
                                     command="sh -c '/init; /index --collections {}'".format(" ".join(name_to_path_host.keys())),
                                     volumes=volumes, detach=True)

        print("Waiting for init and index to finish...")
        base.wait()

        print("Committing image...")
        base.commit(repository=self.config.repo, tag=generate_save_tag(self.config.tag, self.config.save_tag))
