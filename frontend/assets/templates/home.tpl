<div class="home-page">
	<div id="filters" class="row"></div>
	<div class="row">
		<div class="small-12 columns" id="disciplines-resume"></div>
	</div> 
	<div id="calendar-container" class="row">
		<div class="small-12 medium-7 columns" id="calendar"></div>
		<div class="small-12 medium-5 columns" id="teams-table-container"></div>
	</div>
</div>
<ol class="joyride-list" data-joyride>
	<li data-text="Iniciar" data-options="prev_button: false">
		<h4>Bem vindo!</h4>
		<p>O MatrUFSC2 é uma iniciativa independente criada para reformular um sistema muito útil para todos os
		alunos da UFSC. Pretendemos, aqui, melhorar sua experiência de uso, e neste tutorial mostraremos alguns conceitos
		básicos sobre o sistema.</p>
	</li>
	<li data-text="Próximo" data-prev-text="Anterior" data-id="semester-field">
		<h4>Campo "Semestre"</h4>
		<p>Aqui, você pode selecionar o semestre que você deseja consultar.
		Por padrão. Esse campo detecta qual é o proximo semestre disponivel e e selecionado automaticamente.</p>
		<p>Observe que o sistema ainda <b>não</b> tem os semestres anteriores cadastrados, mas isso sera resolvido a partir dos proximos semestres,
		pois permitiremos que o semestre 2015-1 em diante se mantenha registrado. (por pelo menos 4 anos)</p>

	</li>
	<li data-text="Próximo" data-prev-text="Anterior" data-id="campus-field">
		<h4>Campo "Campus"</h4>
		<p>Este campo permite que você selecione o Campus com o qual deseja trabalhar. Disponibilizamos esta opção pois a UFSC está
		disponível por toda SC, e seria ruim (para você, e para nós também) possibilitar a filtragem de todas as disciplinas que a UFSC
		fornece de maneira global.
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="discipline-field">
		<h4>Campo "Disciplina"</h4>
		<p>Usando este campo, você pode adicionar as disciplinas que pretende fazer no próximo semestre. Basta clicar nesse campo e começar a digitar para
		fazer a busca pelas disciplinas disponiveis no campus e no semestre selecionados.</p>
		<p>Note que você pode fazer as buscas tanto pelo <b>Código</b> da disciplina quanto pelo seu <b>Nome</b>. E para adicionar a disciplina na lista de
		disciplinas selecionadas você pode usar a tecla <b>Enter</b> em seu teclado ou mesmo clicar sob a disciplina.</p>
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="disciplines-resume">
		<h4>Lista de disciplinas selecionadas</h4>
		<p>Aqui você pode ver e manipular a lista de disciplinas selecionadas. Caso se arrependa de ter adicionado uma disciplina, basta
		clicar no botão <i class="icon-delete"></i> localizado na linha de cada disciplina e ela será removida da sua lista de disciplinas selecionadas.</p>
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="disciplines-resume">
		<h4>Lista de disciplinas selecionadas - Selecionando turmas</h4>
		<p>Clicando no código de uma disciplina desta tabela abre a lista de turmas dessa disciplina. Onde você pode ativar ou desativar
		determinadas turmas desta disciplina, conforme sua vontade. (mas explicaremos mais sobre isso mais adiante).</p>
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="combinationStatus">
		<h4>Lista de disciplinas selecionadas - Combinações</h4>
		<p>Quando você adiciona disciplinas, o sistema captura as turmas e checa a quantidade de combinações possível disponível
		para as turmas selecionadas.</p>
		<p>Esse contador mostra qual a combinação selecionada atualmente e a quantidade de combinações disponíveis. Você pode usar as setas disponíveis
		ao lado desse contador para modificar a combinação selecionada atualmente</p>
		<p>Note que o sistema considera como sendo combinações diferentes <b>turmas diferentes que tem horários iguais</b>. Por isso,
			pode acontecer de, quando você clicar nas setas, o <b>quadro de horários</b> não mudar, mas acredite: Turmas diferentes estão sendo consideradas
			para cada combinação</p>
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="disciplines-resume">
		<h4>Lista de disciplinas selecionadas - Conflitos</h4>
		<p>Às vezes, pode acontecer de <b>haver disciplinas selecionadas, mas não existir combinações possíveis</b>. Isso normalmente
		acontece pois duas ou mais turmas conflitam <b>completamente</b> entre si. Quando isso acontece, o sistema mostra um "-" para
		cada turma de cada disciplina mostrada nesta tabela, o quadro de horários é zerado e uma (ou mais) disciplinas começam a piscar.</p>
		<p>Nesse caso, há duas opções: Clicar no icone <i class="icon-delete"></i> e tirar a(s) disciplina(s) da lista de disciplinas
		selecionadas, ou então fazer experimentos com as outras disciplinas para encontrar uma combinação válida.</p>
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="calendar" data-options="tip_location: top">
		<h4>Quadro de horários</h4>
		<p>Aqui é mostrado, de forma visual e intuitiva, os horários das turmas que você selecionou. Note que cada
		bloco mostrado aqui contém o código da disciplina, e não da turma selecionada. Mas voce pode ver facilmente as turmas
		consideradas aqui na lista de disciplinas selecionadas, mostrada logo acima.</p>
	</li>

	<li data-text="Próximo" data-prev-text="Anterior" data-id="teams-table-container" data-options="tip_location: top">
		<h4>Lista de Turmas</h4>
		<p>Esta tabela é a lista de turmas. Ela só é preenchida quando você seleciona uma disciplina, clicando no código dela, na
		lista de disciplinas selecionadas. Aqui, você pode desativar ou ativar as turmas que você tem interesse em pegar. Note que,
		por padrão, todas as turmas são ativadas por padrão. E como tal, basta desativar as turmas que você <b>não</b> tem interesse em pegar</p>
	</li>

	<li data-button="Terminar" data-options="prev_button: false">
		<h4>Fim</h4>
		<p>Por enquanto é isso. Não se esqueça de, após simular seu quadro de horários aqui, <b>efetivar realmente sua matrícula no <a href="http://cagr.ufsc.br/" target="_blank">CAGR</a></b>. Isso é super importante caso você seja estudante da UFSC e queira estudar na UFSC semestre que vem!</p>
		<p>Boa sorte na matrícula! :D</p>
		<p><em>Equipe MatrUFSC</em></p>
	</li>
</ol>