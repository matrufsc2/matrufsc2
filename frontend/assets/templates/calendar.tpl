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
	<tr class="hour-<%- i %>">
		<td>
			<%- hour %>
		</td>
		<% for(var j=1; j < 7; ++j){ %>
			<td style="text-align: center;<%- events[i] && events[i][j] ?  'background-color: '+events[i][j].color+'; color:'+events[i][j].fontColor : '' %>; opacity:<%- events[i] && events[i][j] ? (events[i][j].enabled?1:0.5) : 1 %>" title="<%= events[i] && events[i][j] ? events[i][j].name : default_name %>" data-row="<%= i %>" data-column="<%= j %>" <%= events[i] && events[i][j] && events[i][j].custom ? "data-schedule='"+events[i][j].schedule+"'" : "" %>><%- events[i] && events[i][j] ? events[i][j].title:default_title %></td>
		<% } %>
	</tr>
	<% } %>
</tbody>
			
			