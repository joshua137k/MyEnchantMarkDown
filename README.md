


# MyEnchantMarkDown

O **MyEnchantMarkDown** é uma aplicação desktop desenvolvida em Python com PyQt5, que integra edição de Markdown e CSS. Ela permite que você escreva seu conteúdo normalmente em Markdown, compile-o para gerar um HTML e aplique estilos via CSS. A seguir, veja um breve guia com as principais funcionalidades:

---

## Funcionalidades

- **Editor de Markdown:**  
  Permite digitar o seu conteúdo usando a sintaxe Markdown tradicional.  
  Exemplo de Markdown:
  
  ```
  # Meu Título
  Este é um parágrafo com **negrito** e *itálico*. 
  ```


## Compilação para HTML:
Ao compilar o projeto (usando o atalho Ctrl+S ou o botão "Compile"), o conteúdo Markdown é transformado em HTML.
O HTML gerado vincula automaticamente o CSS para que os estilos definidos sejam aplicados.

## Editor de CSS:
Você pode criar e editar um arquivo CSS separado que será associado ao HTML compilado. Assim, pode personalizar a aparência do seu conteúdo.

## Incorporação de HTML no Markdown:
Como o Markdown permite embutir HTML, você pode incluir trechos de código HTML direto no documento para customizações mais avançadas.
Exemplos:

### Bloco HTML simples:
```
<div>
  **a)** How to go?
</div>
```

## Definindo um ID ou classe:

```
<div id="minhaSessao" class="secaoDestaque">
  Conteúdo personalizado com ID e classe.
</div>
```

## Utilizando a sintaxe estendida para aplicar classe a um elemento Markdown:
```
# Título Principal {.titleL}
```

Neste exemplo, o título receberá a classe CSS *titleL*, permitindo que você defina estilos específicos para ele no seu arquivo CSS.

# Como Funciona
* Criação e Edição:

    - Edite seu conteúdo no editor de Markdown.

    - Personalize os estilos no editor de CSS.

* Compilação:

    - Ao compilar, a ferramenta converte o Markdown para HTML e gera o arquivo index.html com o CSS vinculado.

    - O HTML resultante pode incluir tanto o conteúdo gerado a partir do Markdown quanto os trechos de HTML inseridos manualmente.

* Visualização:

    - Você pode usar o recurso de hospedagem local para abrir o arquivo HTML no navegador e ver a renderização completa com os estilos aplicados.

    - Sempre que compilar, o navegador pode atualizar automaticamente para refletir as mudanças.

# Exemplo Prático
Imagine que você deseja criar um documento que contenha um título estilizado e uma seção com conteúdo personalizado:


# Meu Projeto {.titleL}
```
Bem-vindo ao **MyEnchantMarkDown**! Esta aplicação permite que você:

- Escreva em Markdown normalmente.
- Compile seu documento para gerar HTML.
- Crie ou edite um arquivo CSS para personalizar o visual.
- Insira HTML embutido, definindo IDs e classes, para customizações avançadas.

<div class="minhaClasse">
  <p>Este é um exemplo de HTML embutido.</p>
  <p id="paragrafoEspecial">Você pode definir um <strong>ID</strong> ou <em>classe</em> em elementos HTML.</p>
</div>
```
* No exemplo acima:

    - O título recebe a classe titleL.

    - O bloco <div> demonstra a utilização de classes e, dentro dele, um parágrafo com um identificador específico.