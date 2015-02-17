<thead>
	<tr>
		<th></th>
		<th>
			Turma
		</th>
		<th>
			Vagas
		</th>
		<th>
			Professores
		</th>
	</tr>
</thead>
<tbody></tbody>
<tfoot>
    <% if (is_editing) { %>
    <tr>
        <td colspan="4"><a href="#" id="add-team">Adicionar Turma</a></td>
    </tr>
    <% } else { %>
	<tr>
		<td>
			<input type="checkbox" id="groupTeams" checked="checked"/>
		</td>
		<td colspan="3">
			<label for="groupTeams">Agrupar turmas com horários iguais</label>
		</td>
	</tr>
    <% } %>
</tfoot>