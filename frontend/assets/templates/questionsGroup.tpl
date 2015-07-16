<div class="content-page">
    <% if (model.has("title")) { %>
	<div class="row">
		<div class="small-12 columns">
            <h1><%- model.get("title") %></h1>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <ul class="breadcrumbs">
              <li><a href="/">Página Inicial</a></li>
              <li><a href="/ajuda/">Ajuda</a></li>
              <li><a href="/ajuda/perguntas-frequentes/">Perguntas Frequentes</a></li>
              <li class="current"><a href="<%- model.get('link') %>"><%- model.get("title") %></a></li>
            </ul>
        </div>
	</div>
	<div class="row">
		<div class="small-12 columns">
            <%= model.get("description") %>
        </div>
	</div>
    <div class="row">
		<div class="small-12 columns">
            <ul class="accordion" data-accordion>
              <% model.eachQuestion(function(question, questionId) { %>
              <li class="accordion-navigation">
                <a href="#question<%- questionId %>"><%- question["question"] %></a>
                <div id="question<%- questionId %>" class="content <%- questionId == 0 ? 'active': '' %>">
                    <%= question["answer"] %>
                </div>
              </li>
              <% }) %>
            </ul>
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