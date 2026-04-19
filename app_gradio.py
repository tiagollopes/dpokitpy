from dpokitpy.guard import Guard
import gradio as gr
import json

guard = Guard()

def analisar_texto(texto):
    try:
        resultado = guard.find(texto)

        # Se o objeto tiver método to_dict(), usa ele
        if hasattr(resultado, "to_dict"):
            return resultado.to_dict()

        # Se já vier como dict ou list, retorna direto
        if isinstance(resultado, (dict, list)):
            return resultado

        # Se não for JSON, mostra como texto
        return {"resultado": str(resultado)}

    except Exception as e:
        return {"erro": str(e)}

demo = gr.Interface(
    fn=analisar_texto,
    inputs=gr.Textbox(
        lines=8,
        placeholder="Digite ou cole um texto aqui. Ex: CPF 52998224725",
        label="Texto para análise"
    ),
    outputs=gr.JSON(label="Resultado"),
    title="dpokitpy",
    description="Teste visual da biblioteca dpokitpy com Gradio"
)

if __name__ == "__main__":
    demo.launch()
