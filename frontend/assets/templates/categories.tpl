<% if (categories.length > 0) { %>
    <div class="row">
        <div class="small-12 columns">
            <h4><%- title %></h4>
            <ul>
                <% categories.each(function(category) { %>
                    <li><a href="<%- category.get('link') %>"><%- category.get('title') %></a></li>
                <% }) %>
            </ul>
        </div>
    </div>
<% } %>