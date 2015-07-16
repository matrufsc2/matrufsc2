<div class="content-page">
	<div class="row">
		<div class="small-12 columns">
            <h1>Ajuda</h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li class="current"><a href="/ajuda/">Ajuda</a></li>
            </ul>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <p>
                Preparamos alguns conteúdos sobre variados assuntos que consideramos importantes para você,
                estudante da UFSC. Se informe, e, se sentir falta de algo, mande sua sugestão para
                <a href="http://facebook.com/messages/MatrUFSC2">a nossa página oficial do Facebook</a>. =)
            </p>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <ul class="small-block-grid-4" data-equalizer>
                <li style="background: <%- getRandomColor() %>" data-equalizer-watch>
                    <a href="/ajuda/perguntas-frequentes/" class="link-bold-title"><b>Perguntas Frequentes</b></a>
                    <p>
                        Perguntas e respostas comuns relacionadas ao MatrUFSC2 e a universidade em geral
                    </p>
                </li>
                <% if (sections.length > 0) { %>
                    <% sections.each(function(section){ %>
                        <li style="background: <%- getRandomColor() %>" data-equalizer-watch>
                            <a href="<%- section.get('link') %>" class="link-bold-title"><b><%- section.get("title") %></b></a>
                            <%= section.get("description") %>
                        </li>
                    <% }); %>
                <% } %>
            </ul>
        </div>
	</div>
</div>