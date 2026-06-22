from transformers import AutoModelForSemanticSegmentation

model_name = "nvidia/segformer-b0-finetuned-ade-512-512"
model = AutoModelForSemanticSegmentation.from_pretrained(model_name)

labels = model.config.id2label

for k, v in labels.items():
    print(f"{k}: {v}")