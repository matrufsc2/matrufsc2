<ul class="pagination">
  <li class="arrow first-page <%- firstItemClass %>"><a href="#">&laquo;</a></li>
  <% if (firstPages.length > 0) { %>
      <% _.each(firstPages, function(page) { %>
        <li class="go-to-page"><a href=""><%- page %></a></li>
      <% }) %>
      <li class="unavailable"><a href="">&hellip;</a></li>
  <% } %>
  <% _.each(previousPages, function(page) { %>
    <li class="go-to-page"><a href=""><%- page %></a></li>
  <% }) %>
  <li class="current"><a href=""><%- currentPage %></a></li>
  <% _.each(nextPages, function(page) { %>
    <li class="go-to-page"><a href=""><%- page %></a></li>
  <% }) %>
  <% if (endPages.length > 0) { %>
      <li class="unavailable"><a href="">&hellip;</a></li>
      <% _.each(endPages, function(page) { %>
        <li class="go-to-page"><a href=""><%- page %></a></li>
      <% }) %>
  <% } %>
  <li class="arrow last-page <%- lastItemClass %>"><a href="#">&raquo;</a></li>
</ul>