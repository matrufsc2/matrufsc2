# MatrUFSC2

O MatrUFSC2 nasceu com a intenção de ser um substituto ao MatrUFSC original. Criado sob principios da web moderna, usaremos bibliotecas e arquiteturas avançadas para levar ao usuário recursos inovadores e fáceis de usar.

Note que o backend (no caso, o código deste repositório) agora é uma aplicação do Google App Engine e, portanto, **não** é mais compatível com servidores WSGI por padrão. (e isso pode vir a mudar no futuro)

# Objetivos

Como novidades ao projeto original, temos como objetivo:

- Re-escrever o projeto original, criando uma arquitetura original, fácil de programar e conhecida pela comunidade opensource ao redor do mundo.
- Otimizar o sistema para funcionamento nos mais variados ambiente, incluindo ambiente mobile.
- Aprimorar a experiência do usuário ao permitir simulação mesmo quando o usuário estiver offline.
- Criar testes automatizados para detectarmos problemas antes mesmo dos usuários notá-los.

Estaremos aprimorando o código com o passar do tempo. No momento, estaremos focando em re-escrever o [frontend](http://github.com/matrufsc2/frontend) e o backend para fornecermos uma experiência concisa tanto para o desenvolvedor quanto para o usuário.


## LICENÇA

Leia o arquivo [LICENSE](https://github.com/matrufsc2/matrufsc2/blob/develop/LICENSE.md).

## Dependências

Segue as dependências do projeto:

- [Python 2.7](http://python.org)
- [NodeJS](http://nodejs.org)
- [SDK do Google App Engine](https://developers.google.com/appengine/downloads)
- [pip](http://pip.readthedocs.org/en/latest/)

## Instalação

- Clone o projeto rodando:

```sh
    git clone git@github.com:matrufsc2/matrufsc2.git && cd matrufsc2
```
- Instale suas dependências:

```sh
    pip install -r requirements.txt
```

- Precisamos instalar as dependências do frontend! Basta executar o seguinte comando para fazê-lo:

```sh
    cd frontend && npm install && npm run-script build
```

- Rode o seguinte comando:

```sh
    <caminho para a SDK do Google>/dev_appserver.py .
```

Pronto! O Servidor estará em execução no endereço http://127.0.0.1:8080/