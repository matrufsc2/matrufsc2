<td class="text-center">
    <% if(is_editing_discipline) { %>
        <% if (is_editing_team) { %>
            <a href="#" title="Salvar Turma"><i class="icon-ok"></i></a>
        <% } else { %>
            <a href="#" title="Editar Turma"><i class="icon-edit"></i></a>
        <% } %>
    <% } else { %>
    <fieldset class="switch tiny show-for-small-only" tabindex="0">
		<input type="checkbox" class="selectedTeam" id="selectedTeam-<%- team.id %>" <%- team.get("_selected") ? 'checked="checked"':'' %> />
		<label for="selectedTeam-<%- team.id %>"></label>
    </fieldset>
    <input type="checkbox" class="selectedTeam hide-for-small-only" <%- team.get("_selected") ? 'checked="checked"':'' %> />
    <% } %>
</td>
<td>
    <a data-dropdown="menu<%- team.id %>" aria-controls="menu<%- team.get('id') %>" aria-expanded="false" class="has-tip" title="Clique para ver opções" data-tooltip><%= team.get("code") %></a>
    <ul id="menu<%- team.id %>" class="f-dropdown" data-dropdown-content aria-hidden="true" tabindex="-1">
      <% if (is_editing_discipline) { %><li><a href="#" class="removeTeam">Apagar turma</a></li> <% } %>
      <li><a href="#" class="deselectAnothers">Selecionar só essa turma</a></li>
    </ul>
</td>
<td>
	<%- team.get("vacancies_filled") %>/<%- team.get("vacancies_offered") %>
</td>
<td>
	<%- _.pluck(team.get("teachers"), 'name').join(", ") %>
</td>