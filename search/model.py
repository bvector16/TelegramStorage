from transformers import AutoTokenizer, AutoModel
from torch.nn.functional import cosine_similarity
from asyncio import to_thread
from typing import List
import torch


class Searcher:
    def __init__(self):
        # self.model_name = "cointegrated/rubert-tiny2"
        # self.model_name = "ai-forever/ruBert-base"
        self.model_name = "deepvk/RuModernBERT-base"
        self.__tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.__model = AutoModel.from_pretrained(self.model_name)

    def _embed_bert_cls(self, texts):
        t = self.__tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.inference_mode():
            model_output = self.__model(**{k: v.to(self.__model.device) for k, v in t.items()})
        embeddings = model_output.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings)
        return embeddings.cpu()

    def _search(self, search_adress: str, existing_adresses: List[str]) -> List[str]:
        embeddings = self._embed_bert_cls([search_adress] + existing_adresses)
        search_emb = embeddings[0, :]
        exist_emb = embeddings[1:, :]
        similarity = cosine_similarity(search_emb, exist_emb)
        print(existing_adresses, similarity)
        sort_indexes = similarity.argsort(descending=True)[:3]
        result_array = [existing_adresses[i] for i in sort_indexes]
        return result_array

    async def search(self, search_adress: str, existing_adresses: List[str]) -> List[str]:
        return await to_thread(self._search, search_adress, existing_adresses)

    def health(self):
        return self.__model is None


searcher = Searcher()
