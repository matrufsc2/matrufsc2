<div class="content-page">
    <% if (post.has("title") && post.has("body")) { %>
	<div class="row">
		<div class="small-12 columns">
            <h1><%- post.get("title") %></h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li><a href="/blog/">Blog</a></li>
              <% if (post.get("category")) { %>
                <li><a href="<%- post.get('category').link %>"><%- post.get('category').title %></a></li>
              <% } %>
              <li class="current"><a href="<%- post.get('link') %>"><%- post.get("title") %></a></li>
            </ul>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <%= post.get("body") %>
        </div>
	</div>
    <% if (post.get("category")) { %>
    <div class="row">
		<div class="small-12 columns">
            <b>Categoria</b>: <a href="<%- post.get('category').link %>"><%- post.get("category").title %></a>
        </div>
	</div>
    <% } %>
    <div class="related-posts"></div>
    <% if (post.get("allow_comments")) { %>
    <div class="comments">
        <div class="row">
            <div class="small-12 columns">
                <h3><span class="fb-comments-count" data-href="<%- post.get('full_link') %>"></span> comentário(s):</h3>
            </div>
        </div>
        <div class="row">
            <div class="small-12 columns">
                <div class="fb-comments" data-href="<%- post.get('full_link') %>" data-width="100%"></div>
            </div>
        </div>
    </div>
    <% } %>
    <% } else { %>
    <div class="row">
		<div class="small-12 columns">
            <b>Carregando..</b>
        </div>
	</div>
    <% } %>
</div>