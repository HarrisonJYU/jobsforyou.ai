from sentence_transformers import SentenceTransformer

class Embedding:

    def __init__(self):

        self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

    def get_embedding(self, doc):
        """
        return embedding for the given doc using
        the model 
        """

        embedding = self.model.encode(doc)
        return embedding.tolist()