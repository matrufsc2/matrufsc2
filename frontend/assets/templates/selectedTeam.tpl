<td class="text-center">
    <fieldset class="switch tiny show-for-small-only" tabindex="0">
		<input type="checkbox" class="selectedTeam" id="selectedTeam-<%- team.id %>" <%- team.get("_selected") ? 'checked="checked"':'' %> />
		<label for="selectedTeam-<%- team.id %>"></label>
    </fieldset>
    <input type="checkbox" class="selectedTeam hide-for-small-only" <%- team.get("_selected") ? 'checked="checked"':'' %> />
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