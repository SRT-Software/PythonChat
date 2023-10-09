from abc import ABC

from langchain.text_splitter import CharacterTextSplitter
import re
from modelscope.pipelines import pipeline
from typing import (Iterable, List)
from langchain.docstore.document import Document


class SemanticTextSplitter(CharacterTextSplitter, ABC):
    def __init__(self, pdf: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.pdf = pdf

    def split_text(self, text: str) -> list:
        # use_document_segmentation参数指定是否用语义切分文档，此处采取的文档语义分割模型为达摩院开源的nlp_bert_document-segmentation_chinese-base，论文见https://arxiv.org/abs/2107.09278
        # 如果使用模型进行文档语义切分，那么需要安装modelscope[nlp]：pip install "modelscope[nlp]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
        # 考虑到使用了三个模型，可能对于低配置gpu不太友好，因此这里将模型load进cpu计算，有需要的话可以替换device为自己的显卡id
        if self.pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub('\s', " ", text)
            text = re.sub("\n\n", "", text)

        #text = '2020年，钱鹤、吴华强团队基于多阵列忆阻器，搭建了一个全硬件构成的完整存算一体系统，在这个系统上高效运行了卷积神经网络算法，成功验证了图像识别功能，比图形处理器芯片的能效高两个数量级，大幅提升了计算设备的算力，实现了以更小的功耗和更低的硬件成本完成复杂的计算。存算一体架构，就如同“在家办公”的新型工作模式，彻底消除了往返通勤的能量消耗，避免了往返通勤带来的时间延迟，还大大节约了办公场所的运营成本，在边缘计算和云计算中有广泛的应用前景。'
        p = pipeline(
            task="document-segmentation",
            model='damo/nlp_bert_document-segmentation_chinese-base',
            device="cpu")
        result = p(documents=text)
        sent_list = [i for i in result["text"].split("\n\t") if i]
        return sent_list

    def split_documents(self, documents: Iterable[Document]) -> List[Document]:
        """Split documents."""
        texts, metadatas = [], []
        index = 0
        for doc in documents:
            print('index', index)
            index += 1
            print(doc)
            text_list = self.split_text(doc.page_content)
            for txt in text_list:
                texts.append(txt)
            for i in range(len(text_list)):
                metadatas.append(doc.metadata)

        documents = []
        for i in range(len(texts)):
            doc = Document(page_content=texts[i], metadatas=metadatas[i])
            documents.append(doc)
        return documents
