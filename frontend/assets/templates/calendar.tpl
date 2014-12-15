<thead>
	<tr>
		<th>
		</th>
		<th>
			Segunda
		</th>
		<th>
			Terça
		</th>
		<th>
			Quarta
		</th>
		<th>
			Quinta
		</th>
		<th>
			Sexta
		</th>
		<th>
			Sábado
		</th>
	</tr>
</thead>
<tbody>
	<% for(var i = 0; i< hours.length;i++){
		var hour = hours[i];
	%>
	<tr>
		<td>
			<%- hour %>
		</td>
		<% for(var j=1; j < 7; ++j){ %>
			<td style="text-align: center;background-color: <%- events[i] && events[i][j] ? events[i][j].color : '#ffffff' %>; opacity:<%- events[i] && events[i][j] ? (events[i][j].enabled?1:0.5) : 1 %>" title="<%- events[i] && events[i][j] ? events[i][j].name : '' %>"><%- events[i] && events[i][j] ? events[i][j].title||"":"" %></td>
		<% } %>
	</tr>
	<% } %>
</tbody>
			
			