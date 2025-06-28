# Web Scraping Eorzea Database

Repositório do projeto de análise de armas do Final Fantasy XIV.

Passos concluídos:

- Coleta: Extrair os dados de armas do Final Fanatsy XIV com as seguintes informações:

    - Nome da arma

    - Nível do item (item level)

    - Nível mínimo para uso (required level)

    - Classe(s) que pode(m) usar

    - Tipo da arma (espada, cajado, lança...)

    - Atributos principais (Strength, Vitality, Mind...)

    - Dano físico / Auto-ataque / Delay

    - Raridade (com base na cor do contorno do ícone)

---

- A implementar:

- Coleta: extrair a Fonte do item (ex: vendido por NPC, drop de monstro...)

- Análise: 

    - Qual tipo de arma tem maior dano médio?
    - Como o dano físico aumenta conforme o nível do item?
    - Qual classe tem mais opções de armas disponíveis?
    - Quais armas têm os maiores bônus de força ou vitalidade?
    - Qual é a distribuição de raridade entre todas as armas?

- Data-viz: criar gráficos simples com matplotlib ou seaborn, como:

    - Gráfico de barras: quantidade de armas por tipo
    - Boxplot: distribuição de dano por raridade
    - Gráfico de dispersão: item level vs. dano
    - Tabela resumo: top 10 armas com maior dano físico
