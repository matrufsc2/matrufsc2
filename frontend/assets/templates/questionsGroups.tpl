<div class="content-page">
	<div class="row">
		<div class="small-12 columns">
            <h1>Perguntas Frequentes</h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li><a href="/ajuda/">Ajuda</a></li>
              <li class="current"><a href="/ajuda/perguntas-frequentes/">Perguntas Frequentes</a></li>
            </ul>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <p>
                Preparamos algumas perguntas e respostas sobre variados assuntos que consideramos importantes para você,
                estudante da UFSC. Se informe, e, se sentir falta de algo, mande sua sugestão para
                <a href="http://facebook.com/messages/MatrUFSC2" target="_blank">a nossa página oficial do Facebook</a>. =)
            </p>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <ul class="small-block-grid-4" data-equalizer>
                <% if (questionsGroups.length > 0) { %>
                    <% questionsGroups.each(function(model){ %>
                        <li style="background: <%- getRandomColor() %>" data-equalizer-watch>
                            <a href="<%- model.get('link') %>" class="link-bold-title"><b><%- model.get("title") %></b></a>
                            <%= model.get("description") %>
                        </li>
                    <% }); %>
                <% } else { %>
                    <li data-equalizer-watch><%- firstTime ? "Carregando perguntas..": "Nenhuma pergunta encontrada" %></li>
                <% } %>
            </ul>
        </div>
	</div>
</div>