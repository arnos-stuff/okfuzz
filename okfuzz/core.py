from transformers import AutoModel

def load_model(model_name):
    return AutoModel.from_pretrained(model_name)


model = AutoModel.from_pretrained("prajjwal1/bert-tiny")