class PreparerConfig:
    def __init__(self, repo, tag, collections):
        self.repo = repo
        self.tag = tag
        self.collections = collections
    

class SearcherConfig:
    def __init__(self, repo, tag, topic, topic_format, output, qrels):
        self.repo = repo
        self.tag = tag
        self.topic = topic
        self.topic_format = topic_format
        self.output = output
        self.qrels = qrels
