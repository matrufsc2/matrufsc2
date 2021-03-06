### CONTRIBUINDO

Para contribuir com código para o projeto, certifique-se de estar respeitando a [LICENÇA original](https://github.com/matrufsc2/matrufsc2/blob/develop/LICENSE.md) e de averiguar os seguintes aspectos:

- Garantir que, para todo recurso novo, tenha testes unitários de forma a garantir 100% de cobertura de código. (apenas quando essa condição for cumprida poderá ser realizado o deploy)
- Garantir testes em todos os navegadores a partir do IE 8.
- Evitar anexação de bibliotecas e frameworks **não** manejadas pelos gerenciadores de pacotes usados atualmente: Bower e pip.
- Seguir regras impostas pelo *jshint* (para Javascript) e pelo *pep8* (em breve, teremos um script para garantir esse tipo de qualidade).
- Não usar pré-processadores (Coffeescript, LESS, Typescript, SASS, etc.) no código incorporado na aplicação (bibliotecas podem usar pré-processadores desde que forneçam um pacote com o código compilado (vide o exemplo do ChaplinJS))
- No projeto, usaremos o git-flow para garantir um fluxo interessante com o Git. Certifique-se de enviar branchs que sigam tal padrão. =)