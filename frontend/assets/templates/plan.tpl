<form class="form-line">
    <div class="row collapse">
        <div class="small-8 columns">
            <input type="text" placeholder="Informe seu identificador.." id="plan-code"/>
        </div>
        <div class="small-2 columns">
            <a href="#" class="button postfix" id="open-button">Abrir</a>
        </div>
        <div class="small-2 columns">
            <a href="#" class="button postfix" id="save-button">Salvar</a>
        </div>
    </div>
</form>
<div id="code-empty" class="reveal-modal" data-reveal>
  <h2>Informe o identificador!</h2>
  <p>Você precisa informar o identificador do plano que você deseja abrir ou salvá-lo para que possamos encontrar algo no sistema. Deixá-lo em branco <b>não é uma opção</b>.</p>
  <a class="close-reveal-modal">&#215;</a>
</div>
<div id="plan-not-found" class="reveal-modal" data-reveal>
  <h2>Erro!</h2>
  <p>Nenhum plano foi encontrado para o identificador informado! Se você está tentando ver o plano de um amigo, peça para ele
  a URL de compartilhamento do código. =)</p>
  <a class="close-reveal-modal">&#215;</a>
</div>
<div id="plan-not-authenticated" class="reveal-modal" data-reveal>
  <h2>Faça o login!</h2>
  <p><a href="<%- user.get('login_url') %>" class="auth">Faça o login</a> <b>gratuito</b> usando sua conta Google para poder salvar ou abrir planos no MatrUFSC2. Seu login será totalmente criptografado e
  seu login e senha não serão salvos nos nossos servidores. Assim que você fizer login tentaremos abrir ou salvar o plano no código informado, conforme seu desejo. =)</p>
  <p><a class="button alert auth" href="<%- user.get('login_url') %>" class="auth">Fazer o login</a></p>
  <a class="close-reveal-modal">&#215;</a>
</div>