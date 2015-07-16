<% if (posts.length > 0) { %>
    <div class="row">
        <div class="small-12 columns">
            <h4><%- title %></h4>
            <ul>
                <% posts.each(function(post) { %>
                    <li><a href="<%- post.get('link') %>"><%- post.get('title') %></a></li>
                <% }) %>
            </ul>
        </div>
    </div>
<% } %>