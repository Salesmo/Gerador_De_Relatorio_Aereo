import google.generativeai as geneai

print("Configurando API do Gemini...")
GOOGLE_GEMINI_API_KEY = "AIzaSyB2G_ZKM1cefh4o7YO0vvx0WRxStgxhKHw"
geneai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = geneai.GenerativeModel("gemini-2.0-flash-lite")
chat = model.start_chat(history=[])
print("API do Gemini configurado com sucesso!")


def get_report(json_texto, emit=None):
    prompt = f"""
    Você é um especialista em relatórios. Vasculhe toda a internet procurando os melhores modelos para relatório,
    então estude-o e aprenda-o.
    Agora, analise o JSON que enviarei abaixo e crie um relatório sobre ele, contendo o seguinte formato:
    Título: [Nome do aeroporto]
    logo abaixo do título: Relatório de Pousos – [Data]
    1: Resumo Geral do Dia -> Faça aqui um resumo geral de tudo que foi analisado. Esse tópico é para quem
    não tem tempo de ler o relatório completo. Aqui deve estar a principal informação de cada tópico, bem direto.
    2: Introdução -> Faça uma introdução sobre o que o relatório abordará (De acordo com os dados do JSON)
    3: Companhias Aéreas e Frequências -> Apresente números
    4: Cidades de Origem Mais Comuns -> Destaque o aeroporto e apresente números
    5: Análise de Pontualidade -> Crie uma tabela se precisar
    6: Modelos de Aeronaves Mais Frequentes -> Apresente números
    7: Irregularidades (Cancelados, Desconhecidos)
    8: Conclusão -> Faça uma conclusão, seguida de um comentário e uma recomendação que possa ser feito 
    com essa conclusão obtida.

    *Importante: Estruture tudo em um HTML, pois toda sua resposta será aplicada diretamente em uma página HTML
    para o usuário final, portanto, remova qualquer formatação de texto (asteriscos, etc) e formate sua mensagem
    em um HTML.

    Regras:
    Titulos do relatório devem ser em H2 (somente H2, nao extenda), com a classe "titulo-relatorio";
    Textos de cada titulo devem ser um parágrafo p (somente p, nao extenda), com a classe "paragrafo-relatorio"
    Qualquer destaque que queira adicionar no relatório, siga as seguintes instruções:
    cor -> classe "cor-relatorio_[cor]", sendo as UNICAS cores disponiveis: vermelho, verde, amarelo
    negrito -> classe "negrito-relatorio"
    italico -> classe "italico-relatorio".

    Por fim, lembre-se de traduzir Unknown, Landed, ou qualquer outra palavra em inglês, para português. 
    Não se esqueça de SEMPRE adicionar as classes nos títulos citados acima e de usar as marcações de cor,
    negrito, etc (Use-as, porém sem exagerar).

    JSON:
    {json_texto}
    """
    emit('message', {
            'type': 'alert',
            'text': f'Gerando relatório...'
        })
    resposta = model.generate_content(prompt)
    emit('message', {
            'type': 'alert',
            'text': f'Relatório gerado com sucesso!'
        })
    
    texto = resposta.text.strip()

    # 🔍 Remover blocos de markdown tipo ```html ... ```
    if texto.startswith("```html"):
        texto = texto.replace("```html", "").strip()
    if texto.endswith("```"):
        texto = texto[:texto.rfind("```")].strip()

    return texto
