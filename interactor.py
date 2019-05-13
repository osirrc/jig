import json
import sys


class Interactor:

    def __init__(self, interactor_config=None):
        self.config = interactor_config

    def set_config(self, interactor_config):
        self.config = interactor_config

    def interact(self, client, generate_save_tag):
        """
        Starts a container from a saved image that has already been initialized/indexed.

        The 'interact' hook is used by the image to perform any additional initialization
        necessary, if any, for the user interaction that follows. Assume that any running
        process started by the 'init'/'index' hooks is gone.
        """

        save_tag = generate_save_tag(self.config.tag, self.config.load_from_snapshot)
        exists = len(client.images.list(filters={"reference": "{}:{}".format(self.config.repo, save_tag)})) != 0
        if not exists:
            sys.exit("Must prepare image first...")

        interact_args = {
            "opts": {key: value for (key, value) in map(lambda x: x.split("="), self.config.opts)}
        }

        print("Starting a container from saved image...")
        # create with sh command to override any default command
        container = client.containers.create("{}:{}".format(self.config.repo, save_tag), command="sh", tty=True, publish_all_ports=True)
        container.start()

        print("Running interact script in container...")
        log = container.exec_run("sh -c '/interact --json {}'".format(json.dumps(json.dumps(interact_args))),
                                 stdout=True, stderr=True, stream=True)

        print("Logs for interact in container with ID {}...".format(container.id))
        for line in log[1]:
            print(str(line.decode('utf-8')), end="")

        print("You can now interact with container with ID {}".format(container.id))

        if self.config.exit_jig:
            print("Exiting...")
            print("Don't forget to stop and remove the container after you are done!")
            return

        wait = input("Press ENTER to stop and remove container")
        print("Stopping container {}...".format(container.id))
        container.stop()
        print("Removing container {}...".format(container.id))
        container.remove()
