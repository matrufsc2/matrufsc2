<td>
	<input type="checkbox" id="selectedTeam" <%- team.get("_selected") ? 'checked="checked"':'' %> />
</td>
<td>
	<%- team.get("code") %>
</td>
<td>
	<%- team.get("vacancies_filled") %>/<%- team.get("vacancies_offered") %>
</td>
<td>
	<%- _.pluck(team.get("teachers"), 'name').join(", ") %>
</td>