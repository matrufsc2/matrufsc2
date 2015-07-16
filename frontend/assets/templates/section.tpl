<div class="content-page">
	<div class="row">
		<div class="small-12 columns">
            <h1>Ajuda - Seção <%- section.get("title") %><% if(articles.getQuery()) { %> - Buscando por "<%- articles.getQuery() %>"<% } %></h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li><a href="/ajuda/">Ajuda</a></li>
              <li<% if (!articles.getQuery()) { %> class="current"<% } %>><a href="<%- section.get('link') %>"><%- section.get("title") %></a></li>
              <% if(articles.getQuery()) { %><li class="current"><a href="/blog/?q=<%- articles.getQuery() %>">Resultados para "<%- articles.getQuery() %>"</a></li><% } %>
            </ul>
        </div>
	</div>
    <div class="row">
        <div class="small-8 columns">
            <% if (articles.length > 0) { %>
            <% articles.each(function(article) { %>
                <div class="row">
                    <div class="small-12 columns">
                        <a href="<%- article.get('link') %>"><h2><%- article.get("title") %></h2></a>
                    </div>
                </div>
                <div class="row">
                    <div class="small-12 columns">
                        <%= article.get("summary") %>
                    </div>
                </div>
            <% }); %>
            <div class="row">
                <div class="small-12 columns" id="pagination-container"></div>
            </div>
            <% } else { %>
                    <b><%- firstTime ? "Carregando artigos..": "Nenhum artigo encontrado" %></b>
            <% } %>
        </div>
        <div class="small-4 columns">
            <div class="row">
                <div class="small-12 columns search-form"></div>
            </div>
            <div class="row">
                <div class="small-12 columns sections"></div>
            </div>
        </div>
	</div>
</div>