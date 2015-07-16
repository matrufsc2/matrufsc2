<div class="content-page">
    <% if (model.has("title") && model.has("body")) { %>
	<div class="row">
		<div class="small-12 columns">
            <h2><%- model.get("title") %></h2>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <%= model.get("body") %>
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