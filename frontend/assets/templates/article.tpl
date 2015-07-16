<div class="content-page">
    <% if (article.has("title") && article.has("body")) { %>
	<div class="row">
		<div class="small-12 columns">
            <h1><%- article.get("title") %></h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li><a href="/ajuda/">Ajuda</a></li>
              <li><a href="<%- article.get('section').link %>"><%- article.get('section').title %></a></li>
              <li class="current"><a href="<%- article.get('link') %>"><%- article.get("title") %></a></li>
            </ul>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <%= article.get("body") %>
        </div>
	</div>
    <% } else { %>
    <div class="row">
		<div class="small-12 columns">
            <b>Carregando..</b>
        </div>
	</div>
    <% } %>
</div>