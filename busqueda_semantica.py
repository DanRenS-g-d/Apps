import pandas as pd
from sentence_transformers import SentenceTransformer, util
import subprocess
import torch
import re
import datetime
import sys
import os
from typing import List

# Constants
EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
EXCEL_PATH = os.getenv("EXCEL_PATH", "unified_supermarket_data.xlsx")
OLLAMA_PATH = os.getenv("OLLAMA_PATH", "ollama")
OLLAMA_MODEL = "mistral:instruct"
SIMILARITY_THRESHOLD = 0.35
TOP_K_RESULTS = 50
INPUT_TXT = "productos.txt"

def check_ollama_model_installed(model_name: str) -> bool:
    try:
        result = subprocess.run([OLLAMA_PATH, "list"], capture_output=True, text=True, timeout=10)
        return model_name.split(":")[0] in result.stdout
    except Exception:
        return False

# Verificar modelo Ollama
if not check_ollama_model_installed("mistral"):
    print(f"❌ El modelo '{OLLAMA_MODEL}' no está instalado en Ollama. Usa 'ollama pull mistral'.")
    sys.exit(1)

def load_data() -> pd.DataFrame:
    print("📂 Loading data...")
    try:
        xls = pd.ExcelFile(EXCEL_PATH)
        datos = []
        for hoja in xls.sheet_names:
            df_hoja = xls.parse(hoja)
            if 'Título' not in df_hoja.columns:
                print(f"⚠️ Sheet skipped (missing 'Título' column): {hoja}")
                continue
            df_hoja = df_hoja.assign(Categoría=hoja)
            df_hoja['Supermercado'] = df_hoja.get('Supermercado', 'Ara').replace('Desconocido', 'Ara')
            datos.append(df_hoja)
        if not datos:
            raise ValueError("No valid sheets found with 'Título' column")
        return pd.concat(datos, ignore_index=True)
    except Exception as e:
        print(f"❌ Failed to load data: {str(e)}")
        sys.exit(1)

def clean_refined_query(text: str) -> str:
    text = re.sub(r'(?i)\bproducto[s]?:\s*', '', text)
    return text.strip()

def refine_query_with_ollama(query: str) -> str:
    if len(query.split()) <= 1:
        return query

    print("🤖 Refining query...", end='', flush=True)
    prompt = (
        f"Refina esta consulta de productos de supermercado de manera concisa. "
        f"La consulta puede estar en español. "
        f"Devuelve ÚNICAMENTE la consulta refinada, SIN explicaciones, SIN ejemplos, SIN comentarios. "
        f"Consulta: '{query}'"
    )
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", OLLAMA_MODEL, prompt],
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='ignore'
        )
        refined = result.stdout.strip()
        refined = clean_refined_query(refined)

        if not refined or len(refined.split()) > 10:
            print("⚠️ Refinement invalid, using original query.")
            return query

        print("✅")
        return refined
    except Exception as e:
        print(f"⚠️ Ollama error: {str(e)}")
        return query

def split_message_into_queries(message: str) -> List[str]:
    lines = message.strip().split('\n')
    return [line.strip() for line in lines if line.strip()]

def main():
    print("🧠 Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    df = load_data()

    for col in ['Título', 'Categoría', 'Subcategoría']:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].astype(str).fillna('')

    combined_text = (df['Título'] + " " + df['Categoría'] + " " + df['Subcategoría'])
    combined_text = combined_text.str.replace(r'\s+', ' ', regex=True).str.strip().str.lower()

    print("🔢 Calculating embeddings (this may take a while)...")
    product_embeddings = model.encode(combined_text.tolist(), convert_to_tensor=True, show_progress_bar=True)

    # Leer lista de productos desde productos.txt
    if not os.path.exists(INPUT_TXT):
        print(f"❌ Archivo '{INPUT_TXT}' no encontrado.")
        sys.exit()

    with open(INPUT_TXT, "r", encoding="utf-8") as f:
        raw_input = f.read().strip()

    if not raw_input:
        print("⚠️ El archivo de productos está vacío. Abortando.")
        sys.exit()

    queries = split_message_into_queries(raw_input)

    all_results = []

    for single_query in queries:
        print(f"\n🔍 Searching for: '{single_query}'")

        refined_query = refine_query_with_ollama(single_query)
        if refined_query != single_query:
            print(f"🔧 Refined query: '{refined_query}'")

        refined_query = refined_query.lower()

        query_embedding = model.encode(refined_query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, product_embeddings)[0]

        top_results = torch.topk(cos_scores, k=TOP_K_RESULTS)
        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            if score < SIMILARITY_THRESHOLD:
                continue
            row = df.iloc[idx.item()]
            price = row.get('Precio', 'N/A')
            if price == 'N/A' or pd.isna(price):
                continue
            results.append((
                single_query,
                row.get('Supermercado', 'Ara'),
                row['Título'],
                float(price),
                row.get('Categoría', 'N/A'),
                round(score.item(), 2)
            ))

        if results:
            best = sorted(results, key=lambda x: x[3])[0]
            all_results.append(best)
        else:
            print(f"⚠️ No relevant products found for '{single_query}'.")

    if all_results:
        results_df = pd.DataFrame(all_results, columns=['Consulta', 'Supermercado', 'Nombre', 'Precio', 'Categoría', 'Similitud'])

        print("\n📊 Cheapest products found:")
        for _, row in results_df.iterrows():
            print(f"🔎 {row['Consulta']} → 🛒 {row['Supermercado']} | {row['Nombre']} | ${row['Precio']} | Score: {row['Similitud']:.2f}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"productos_mas_baratos_{timestamp}.xlsx"
        results_df.to_excel(filename, index=False)
        print(f"\n💾 Results saved to '{filename}'")
    else:
        print("⚠️ No products found.")

    try:
        os.remove(INPUT_TXT)
        print("🧹 Deleted temporary 'productos.txt'")
    except Exception as e:
        print(f"⚠️ Could not delete productos.txt: {str(e)}")

if __name__ == "__main__":
    main()

