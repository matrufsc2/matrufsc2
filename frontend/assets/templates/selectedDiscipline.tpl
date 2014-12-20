<td class="text-center">
    <fieldset class="switch tiny show-for-small-only" tabindex="0">
		<input type="checkbox" class="selectedDiscipline" id="selectedDiscipline-<%- discipline.id %>" <%- discipline.isDisciplineEnabled() ? 'checked="checked"':'' %> />
		<label for="selectedDiscipline-<%- discipline.id %>"></label>
    </fieldset>
    <input type="checkbox" class="selectedDiscipline hide-for-small-only" <%- discipline.isDisciplineEnabled() ? 'checked="checked"':'' %> />
</td>
<td title="<%- discipline.get('_title') %>" class="title <%- discipline.has('_title') ? 'has-tip': '' %>" data-tooltip><%- discipline.get("code") %> - <%- discipline.get("name") %></td>
<td><%- discipline.team ? discipline.team.get("code") : (!discipline.teams.isSynced() ? "Carregando..." : "-")  %></td>
<td><%- discipline.team ? discipline.team.getNumberOfLessons() : '-' %></td>
<td><%- discipline.semester ? discipline.semester.get("name") : '-' %></td>
<td><a href='#'><i class="icon-up"></i></a></td>
<td><a href='#'><i class="icon-down"></i></a></td>
<td><a href='#'><i class="icon-delete"></i></a></td>