**INTRODUÇÃO**

O MatrUFSC2 nasceu com a intenção de ser um substituto ao MatrUFSC original. Criado sob principios da web moderna, usaremos bibliotecas e arquiteturas avançadas para levar ao usuário recursos inovadores e fáceis de usar.

Como novidades ao projeto original, temos como objetivo:

- Re-escrever o projeto original, criando uma arquitetura original, fácil de programar e conhecida pela comunidade opensource ao redor do mundo.
- Otimizar o sistema para funcionamento nos mais variados ambiente, incluindo ambiente mobile.
- Aprimorar a experiência do usuário ao permitir simulação mesmo quando o usuário estiver offline.
- Criar testes automatizados para detectarmos problemas antes mesmo dos usuários notá-los.

Estaremos aprimorando o código com o passar do tempo. No momento, estaremos focando em re-escrever o backend para então fornecermos um ambiente frontend consistente, que, a principio, será baseado no framework [ChaplinJS](http://chaplinjs.org), e que ajudará na otimização do projeto com o uso de boas práticas.

===========================================================================

**LICENÇA**

Leia o arquivo [LICENSE](https://github.com/matrufsc2/matrufsc2/blob/develop/LICENSE.md).

===========================================================================
1. Instalação

Para rodar o CAPIM, é necessário ter os seguintes programas/pacotes
instalados no servidor:

- Python 2.7 (Python 3 não é o foco atualmente)

No ubuntu, os comandos são:

$ sudo apt-get install python-pip

$ sudo pip install -r requirements.txt

$ python matrufsc2.py

Como usamos Bottle, ao executar o último comando você já poderá acessar http://127.0.0.1:8080/ para ver a aplicação funcionando.

2. Banco de dados

O banco de dados é baixado e atualizado automaticamente conforme os semestres passam. Como a UFSC disponibiliza os dados publicamente, o sistema faz o download diariamente dos dados, um processo que deve durar menos de 1 minuto com uma boa conexão, e usa as API's disponíveis para executar os dados. (assim, manteremos compatibilidade tanto com Google App Engine quanto com servidores WSGI normais).