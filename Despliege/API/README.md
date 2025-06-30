```bash
API/
├── model/   # Carpeta del modelo fine-tuned
│   └── flan-t5-large-code-commenter/ # Carpeta del modelo
│       └── adapter_config.json # Configuración de LoRA (Peft)
│       └── adapter_model.safetensors # Pesos del modelo fine-tuned con LoRA
│       └── README.md
│       └── special_tokens_map.json # Mapeo tokens especiales (<pad>, <eos>)
│       └── tokenizer_config.json # Configuración del tokenizador HuggingFace
│       └── tokenizer.json # Tokenizador serializado en .JSON
├── app.py  # Código de la API
├── README.md
└── requirements.txt # Dependencias (FastAPI, transformers, peft, black, etc.)
```