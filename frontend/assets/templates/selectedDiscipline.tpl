<td class="text-center">
    <fieldset class="switch tiny show-for-small-only" tabindex="0">
		<input type="checkbox" class="selectedDiscipline" id="selectedDiscipline-<%- discipline.id %>" <%- discipline.isDisciplineEnabled() ? 'checked="checked"':'' %> />
		<label for="selectedDiscipline-<%- discipline.id %>"></label>
    </fieldset>
    <input type="checkbox" class="selectedDiscipline hide-for-small-only" <%- discipline.isDisciplineEnabled() ? 'checked="checked"':'' %> />
</td>
<td title="<%- discipline.get('_title') %>" class="title <%- !is_editing && discipline.has('_title') ? 'has-tip': '' %>" data-tooltip><% if(is_editing) {
    %><a title="Editar nome da disciplina" class="has-tip discipline-name" href="#" data-tooltip><%- discipline.get("code") %> - <%- discipline.get("name") %></a><% } else { %><%- discipline.get("code") %> - <%- discipline.get("name") %><% } %></td>
<td class="text-center"><%- discipline.team ? discipline.team.get("code") : (!discipline.teams.isSynced() ? "Carregando..." : "-")  %></td>
<td class="text-center"><%- discipline.team ? discipline.team.getNumberOfLessons() : '-' %></td>
<td class="text-center"><%- discipline.semester ? discipline.semester.get("name") : '-' %></td>
<td class="text-center"><a href='#' title="<%= !is_editing || !can_edit ? 'Editar disciplina': 'Salvar' %>"><i class="icon-<%= !is_editing || !can_edit ? 'edit': 'ok' %> <%= can_edit ? '': 'disabled' %>"></i></a></td>
<td class="text-center"><a href='#'><i class="icon-up"></i></a></td>
<td class="text-center"><a href='#'><i class="icon-down"></i></a></td>
<td class="text-center"><a href='#'><i class="icon-delete"></i></a></td>