<div class="content-page">
	<div class="row">
		<div class="small-12 columns">
            <h1>Blog<% if(posts.getQuery()) { %> - Buscando por "<%- posts.getQuery() %>"<% } %></h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li<% if (!posts.getQuery()) { %> class="current"<% } %>><a href="/blog/">Blog</a></li>
              <% if(posts.getQuery()) { %><li class="current"><a href="/blog/?q=<%- posts.getQuery() %>">Resultados para "<%- posts.getQuery() %>"</a></li><% } %>
            </ul>
        </div>
	</div>
    <div class="row">
        <div class="small-8 columns">
        <% if (posts.length > 0) { %>
        <% posts.each(function(post) { %>
            <div class="row">
                <div class="small-12 columns">
                    <a href="<%- post.get('link') %>"><h2><%- post.get("title") %></h2></a>
                </div>
            </div>
            <div class="row">
                <div class="small-12 columns">
                    <%= post.get("summary") %>
                </div>
            </div>
        <% }); %>
        <div class="row">
            <div class="small-12 columns" id="pagination-container"></div>
        </div>
        <% } else { %>
            <b><%- firstTime ? "Carregando posts..": "Nenhum post encontrado" %></b>
        <% } %>
        </div>
        <div class="small-4 columns">
            <div class="row">
                <div class="small-12 columns search-form"></div>
            </div>
            <div class="row">
                <div class="small-12 columns categories"></div>
            </div>
        </div>
	</div>
</div>