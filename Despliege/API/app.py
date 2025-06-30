from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import black
from tempfile import NamedTemporaryFile

app = FastAPI()

# Cargamos el modelo
model_path = "model/flan-t5-large-code-commenter"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


class CodeInput(BaseModel):
    code_clean: str


def generate_comment(code_clean, tokenizer, model, max_length=512):
    prompt = (
        "Add detailed comments and a docstring to the following Python function:\n\n"
        f"{code_clean}\n\n### Commeted by IA"
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(
        device
    )
    outputs = model.generate(**inputs, max_length=max_length)

    output_text = tokenizer.decode(
        outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    # Reemplazar "\n" literales si existen
    output_text = output_text.replace("\\n", "\n")

    # Arreglos heurísticos simples
    output_text = output_text.replace(': """', ':\n    """')
    output_text = output_text.replace('""" ', '"""\n')
    output_text = output_text.replace('"""', '\n    """')  # indentar docstring
    output_text = output_text.replace('    """', '    """\n')

    # Insertar saltos de línea en instrucciones comunes
    for keyword in [
        "return",
        "print(",
        "raise",
        "try:",
        "except",
    ]:
        output_text = output_text.replace(f" {keyword}", f"\n    {keyword}")

    return output_text.strip()


def format_code_with_black(code: str) -> str:
    try:
        with NamedTemporaryFile("w+", suffix=".py", delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_file.flush()
            black.format_file_in_place(
                Path(tmp_file.name),
                fast=False,
                mode=black.FileMode(),
                write_back=black.WriteBack.YES,
            )
            tmp_file.seek(0)
            return tmp_file.read()
    except Exception as e:
        print(f"[ERROR] No se pudo formatear con black: {e}")
        return code  # Si black falla, devolver sin formatear


@app.post("/comment")
def comment_code(input_data: CodeInput):
    commented = generate_comment(input_data.code_clean, tokenizer, model)
    formatted = format_code_with_black(commented)

    print("SALIDA FORMATADA:")
    print(repr(formatted))  # Para ver saltos de línea reales

    return {"commented_code": formatted}
