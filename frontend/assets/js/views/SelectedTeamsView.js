define("views/SelectedTeamsView", [
		"templates",
		"views/BaseView",
		"chaplin",
		"underscore",
		"views/SelectedTeamView",
		"collections/Teams",
        "models/Team"
], function(templates, BaseView, Chaplin, _, selectedTeamView, Teams, Team){
	"use strict";
    function pad(n, width, z) {
        z = z || "0";
        n = n + "";
        return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
    }
	var SelectedTeamsView = BaseView.extend({
		"template" : templates.selectedTeams,
		"itemView": selectedTeamView,
		"listSelector": "tbody",
		"tagName": "table",
        "useCssAnimation": true,
        "animationStartClass": "animation-fade-in",
        "animationEndClass": "animation-fade-in-end",
        "animationDuration": 1500,
		"listen": {
			"addedToDOM": "applyFoundation"
		},
		"events": {
			"click #groupTeams": "groupTeams",
            "click #add-team": "addTeam"
		},
		"initialize": function(options){
			this.collection = null;
			this.selectedDisciplines = options.selectedDisciplines;
            this.status = options.status;
			this.collection = new Teams();
            this.discipline = null;
			this.updateCollection();
			BaseView.prototype.initialize.apply(this, []);
			Chaplin.CollectionView.prototype.initialize.apply(this, []);
			this.listenTo(this.status, "change:discipline", this.selectDiscipline);
			this.listenTo(this.status, "change:editing", this.selectDiscipline);
			this.groupEnabled = this.checkGroupTeamsEnabled();
		},
		"checkGroupTeamsEnabled": function(){
			return this.$("#groupTeams").is(":checked");
		},
		"groupTeams": function(){
			this.groupEnabled = this.checkGroupTeamsEnabled();
			this.group();
			_.each(this.getItemViews(), function(view) {
				view.render();
			}, this);
		},
		"group": function(){
            if (!this.discipline) {
                return;
            }
            if(!this.groupEnabled) {
                this.discipline.teams.each(function(team){
                    team.startGrouping = false;
                    team.endGrouping = false;
                    this.collection.add(team);
                }, this);
				return;
			}
			var onGetSchedule = function(schedule) {
				return schedule.get("hourStart")+""+schedule.get("minuteStart")+":"+schedule.get("dayOfWeek")+":"+schedule.get("classRepeat");
			};
			var onGetTeam = function(team) {
				return _.map(team.schedules.sortBy(onGetSchedule), onGetSchedule).join("|");
			};
            var teams_schedules = {};
			this.discipline.teams.each(function(team) {
                var key = onGetTeam(team);
                if (!teams_schedules[key]) {
                    teams_schedules[key] = [];
                }
                teams_schedules[key].push(team);
            });
            _.each(teams_schedules, function(teams) {
                var teamsLastIndex = teams.length - 1;
                _.each(teams, function(team, index){
                    team.startGrouping = index === 0;
                    team.endGrouping = index === teamsLastIndex;
                    this.collection.add(team);
                }, this);
            }, this);
		},
		"updateCollection": function(){
			var selectedDiscipline = this.status.get("discipline");
			var discipline = this.selectedDisciplines.get(selectedDiscipline);
            this.collection.reset();
			if(!selectedDiscipline || !discipline) {
				return;
			}
			this.discipline = discipline;
			this.groupTeams();
		},
        "addTeam": function(e){
            e.preventDefault();
            if (!this.isEditing()) {
                return alert("Impossivel adicionar turma em disciplina não-personalizada");
            }
            var code, discipline;
            discipline = this.discipline;
            code = 1;
            while (discipline.teams.findWhere({"code": pad(code, 4)})) {
                ++code;
            }
            var team = new Team({
                "id": pad(code, 4),
                "code": pad(code, 4),
                "vacancies_offered": 1,
                "vacancies_filled": 0,
                "teachers": [{
                    "name": "Você"
                }],
                "schedules": []
            });
            team.discipline = discipline;
            discipline.teams.add(team);
            this.updateCollection();
            team.set({
                "_selected": true
            });
        },
		"selectDiscipline": function(){
			this.render();
			this.updateCollection();
		},
		"initItemView": function(model) {
			if (this.itemView) {
				return new this.itemView({
					"autoRender": false,
					"model": model,
                    "discipline": this.discipline,
                    "status": this.status,
                    "isEditingDiscipline": this.isEditing(),
                    "isEditingTeam": this.isEditing() && this.discipline.team && this.discipline.team.id === model.id,
					"selectedDisciplines": this.selectedDisciplines
				});
			} else {
				throw new Error("The CollectionView#itemView property " + "must be defined or the initItemView() must be overridden.");
			}
		},
        "isEditing": function(){
            return this.status.get("editing") === true && this.discipline && this.discipline.get("_custom");
        },
		"getTemplateData": function(){
			return {
                "is_editing": this.isEditing()
			};
		},
		"render": function(){
			BaseView.prototype.render.apply(this, []);
			Chaplin.CollectionView.prototype.render.apply(this, []);
		}
	});
	_.extend(SelectedTeamsView.prototype,
		_.omit(
			Chaplin.CollectionView.prototype,
			_.keys(SelectedTeamsView.prototype),
			_.keys(BaseView.prototype)
		)
	);
	return SelectedTeamsView;
});