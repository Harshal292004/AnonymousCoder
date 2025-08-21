from openai import OpenAI
import json
client = OpenAI(
    base_url="https://api.novita.ai/openai",
    api_key="sk_XSAKOGHCVCRct-RfaLPMX7h8nKD5wKEVh2IbpTCN9eE",
)
model = "qwen/qwen3-embedding-8b"
def get_embeddings(text, model="qwen/qwen3-embedding-8b", encoding_format="float"):
    response = client.embeddings.create(
        model=model,
        input=text,
        encoding_format=encoding_format
    )
    return response
# Example usage
text = "The quick brown fox jumped over the lazy dog"
result = get_embeddings(text)
print(json.dumps(result.model_dump(), indent=2))
  