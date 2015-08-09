<div class="row">
    <div class="small-12 columns">
        <a href="#" title="Mostrar Gerenciador" class="toggle-combinations-manager"><b>Gerenciador de combinações</b></a>
    </div>
</div>
<form style="display: none;">
    <div class="row">
        <div class="small-12 columns">
            <b>Horas-aula</b>
        </div>
    </div>
    <div class="row">
        <div class="small-3 columns">
            <label for="minimum-ha" class="right">Minimo:</label>
        </div>
        <div class="small-3 columns">
            <input type="number" id="minimum-ha" placeholder="Numero minimo de horas aula por semana de acordo com o curriculo do seu curso (carga horaria minima)" maxlength="3" />
        </div>
        <div class="small-3 columns">
            <label for="maximum-ha" class="right">Máximo:</label>
        </div>
        <div class="small-3 columns">
            <input type="number" id="maximum-ha" placeholder="Numero maximo de horas aula por semana de acordo com o curriculo do seu curso (carga horaria maxima)" maxlength="3" />
        </div>
    </div>
    <div class="row">
        <div class="small-12 columns">
            <b>Disciplinas</b>
        </div>
    </div>
    <div class="row">
        <div class="small-3 columns">
            <label for="minimum-disciplines" class="right">Minimo:</label>
        </div>
        <div class="small-3 columns">
            <input type="number" id="minimum-disciplines" placeholder="Numero minimo de disciplinas que você deseja pegar" maxlength="3" />
        </div>
        <div class="small-3 columns">
            <label for="maximum-disciplines" class="right">Máximo:</label>
        </div>
        <div class="small-3 columns">
            <input type="number" id="maximum-disciplines" placeholder="Numero maximo de disciplinas que você deseja pegar" maxlength="3" />
        </div>
    </div>
    <div class="row">
        <div class="small-12 columns">
            <b>Periodos:</b>
        </div>
    </div>
    <div class="row">
        <div class="small-4 columns">
            <input type="checkbox" class="period" name="morning" id="period-morning" checked/> <label for="period-morning">Manhã</label>
        </div>
        <div class="small-4 columns">
            <input type="checkbox" class="period" name="afternoon" id="period-afternoon" checked/> <label for="period-afternoon">Tarde</label>
        </div>
        <div class="small-4 columns">
            <input type="checkbox" class="period" name="night" id="period-night" checked/> <label for="period-night">Noite</label>
        </div>
    </div>
    <div class="row">
        <div class="small-12 columns">
            <b>Dias:</b>
        </div>
    </div>
    <div class="row">
        <div class="small-6 columns">
            <input type="checkbox" class="dayOfWeek" name="1" id="dayOfWeek-monday" checked/><label for="dayOfWeek-monday">Segunda-Feira</label>
        </div>
        <div class="small-6 columns">
            <input type="checkbox" class="dayOfWeek" name="2" id="dayOfWeek-tuesday" checked/><label for="dayOfWeek-tuesday">Terça-Feira</label>
        </div>
    </div>
    <div class="row">
        <div class="small-6 columns">
            <input type="checkbox" class="dayOfWeek" name="3" id="dayOfWeek-wednesday" checked/><label for="dayOfWeek-wednesday">Quarta-Feira</label>
        </div>
        <div class="small-6 columns">
            <input type="checkbox" class="dayOfWeek" name="4" id="dayOfWeek-thursday" checked/><label for="dayOfWeek-thursday">Quinta-Feira</label>
        </div>
    </div>
    <div class="row">
        <div class="small-6 columns">
            <input type="checkbox" class="dayOfWeek" name="5" id="dayOfWeek-friday" checked/><label for="dayOfWeek-friday">Sexta-Feira</label>
        </div>
        <div class="small-6 columns">
            <input type="checkbox" class="dayOfWeek" name="6" id="dayOfWeek-saturday" checked/><label for="dayOfWeek-saturday">Sábado</label>
        </div>
    </div>
    <div class="row">
        <div class="small-12 columns">
            <a href="#" class="button expand">Salvar</a>
        </div>
    </div>
</form>
