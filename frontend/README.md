# Frontend

Bem vindo! Este repositório contém apenas o código **frontend** do [MatrUFSC2](http://matrufsc2.appspot.com), e, como tal, é totalmente desacoplado do seu backend.

## Objetivo

A idéia com este repositório é permitir que você facilmente implemente o seu próprio "Matr" para sua universidade usando uma ferramenta avançada e simples, que é genérica o suficiente para corresponder às necessidades de toda e qualquer universidade.
Criado sob o framework [ChaplinJS](http://chaplinjs.org), com a ajuda de ferramentas como a [Mimosa](http://mimosa.io), temos aqui um código que está em conforme com as mais novas e recentes tecnologias web, sendo adequado para uso por qualquer um. Segue aqui as nossas metas com este projeto:

- Criar um ambiente totalmente desacoplado de um backend, possibilitando assim a implementação do projeto por diversas universidades *apenas* trocando o seu backend.
- Criar uma plataforma estável, testada, que está em conformidade com os novos padrões da internet.

## LICENÇA

Leia o arquivo [LICENSE](https://github.com/matrufsc2/frontend/blob/develop/LICENSE.md).

## Dependências

Segue as dependências do projeto:

- [NodeJS](http://nodejs.org)

## Instalação

- Clone este repositório para o seu computador rodando o seguinte comando no terminal:

```sh
	git clone https://github.com/matrufsc2/frontend.git && cd frontend
```

- Execute o seguinte comando para instalar suas dependências: iniciar o servidor de desenvolvimento:

```sh
	npm install
```

- Inicie o servidor de desenvolvimento:
	
```sh
	npm start
```

- Pronto! O servidor estará rodando no endereço http://127.0.0.1:8000 

## Construindo o projeto

O projeto é muito simples de ser construido. Após clonar o projeto, basta rodar o seguinte comando para que o projeto seja devidamente otimizado para publicação na web:

```sh
	npm run-script build
```

## Testando o projeto

Para executar os testes, basta rodar:

```sh
	npm run-script auto-test
```

Todos os testes serão executados em todos os navegadores que você tiver instalado no seu computador e será criado um relatório na pasta coverage/lcov-report/

Se você não quiser executar testes automatizados, basta executar:

```sh
	echo "Running Coverage Server"
	node coverage_server.js &
```

**Para caso** queira obter relatórios de cobertura de código e depois rodar:

```sh
	npm test
```

Para iniciar o servidor de testes, que escuta em uma porta diferente: http://127.0.0.1:7357/