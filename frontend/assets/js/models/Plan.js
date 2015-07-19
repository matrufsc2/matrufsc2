define("models/Plan", [
    "models/BaseModel",
    "models/Possibility",
    "underscore",
    "es6-promise"
], function (BaseModel, Possibility, _) {
    "use strict";

    return BaseModel.extend({
        "urlRoot": "/api/plans/",
        "defaults": {
            "id": null,
            "history": [],
            "data": []
        },
        "loadPlan": function (status, selectedDisciplines, possibilities, history, version, possibilityId) {
            return new Promise(_.bind(function (resolve, reject) {
                if (status.get("editing")) {
                    return reject("Saia do modo de edição antes de editar outro plano");
                }
                var possibility;
                possibilityId = possibilityId || 1;
                possibilityId = parseInt(possibilityId);
                if (!_.isNumber(possibilityId) || _.isNaN(possibilityId)) {
                    return reject("Plano inválido!");
                }
                version = parseInt(version);
                if (!_.isNumber(version) || _.isNaN(version)) {
                    possibility = this.get("data");
                } else {
                    possibility = _.findWhere(this.get("history"), {
                        "id": version
                    });
                    if (!possibility) {
                        return reject("Versão nao encontrada");
                    }
                    possibility = possibility.data;
                }
                if (!_.isArray(possibility)) {
                    possibility.id = 1;
                    possibility = [possibility, {"id": 2}, {"id": 3}, {"id": 4}];
                }
                possibilities.set(possibility);
                history.set(this.get("history"), {"sort": true});
                possibility = possibilities.get(possibilityId);
                if (!possibility) {
                    return reject("Plano não encontrado!");
                }
                return resolve(possibility.loadPossibility(status, selectedDisciplines));
            }, this));
        },
        "savePlan": function (possibilities, history, silent) {
            this.set({
                "data": possibilities.toJSON(),
                "history": this.get("history").concat([{
                    "id": Math.floor((new Date()).getTime() / 1000),
                    "data": possibilities.toJSON()
                }])
            }, {"silent": silent});
            history.set(this.get("history"), {"sort": true});
        }
    });
});