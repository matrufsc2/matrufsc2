define('views/PlansView', [
    'views/BaseView',
    'templates',
    'underscore',
    'collections/Plans'
], function(BaseView, templates, _, Plans) {
    'use strict';
    return BaseView.extend({
        'template': templates.plan,
        'events': {
            'click #open-button': 'openPlan',
            'click #save-button': 'savePlan'
        },
        'initialize': function(options) {
            this.status = options.status;
            this.plan = options.plan;
            this.user = options.user;
            this.history = options.history;
            this.listenTo(this.user, 'change', this.render);
            this.listenTo(this.user, 'change', this.checkPreviousData);
            this.selectedDisciplines = options.selectedDisciplines;
            this.checkPreviousData();
        },
        'getCode': function(){
            var code = this.$('#plan-code').val();
            if (!code.length) {
                this.$('#code-empty').foundation('reveal', 'open');
                return;
            }
            return code;
        },
        'getTemplateData': function(){
            return {'user': this.user};
        },
        'savePlan': function(e){
            if (e) {
                e.preventDefault();
            }
            var code = this.getCode();
            if (!code) {
                return;
            }
            if (code !== this.plan.get('code')) {
                this.plan.unset('id', {'silent': true});
            }
            if (!this.user.get('is_authenticated')) {
                this.plan.savePlan(this.status, this.selectedDisciplines, this.history, true);
                this.plan.set({
                    'code': code
                }, {'silent': true});
                localStorage.setItem("plan-data", JSON.stringify(this.plan.toJSON()));
                localStorage.setItem("plan-mode", "save");
                this.$('#plan-not-authenticated').foundation('reveal', 'open');
                return;
            }
            var button = this.$('#save-button');
            if(button.is('.disabled')) {
                return;
            }
            button.addClass('disabled').html('Salvando');
            this.plan.once('sync', function(){
                button.html('Salvo!');
                setTimeout(function(){
                    button.removeClass('disabled').html('Salvar');
                }, 2000);
            }, this);
            if (this.plan.isNew()) {
                // Try to find the ID for the code specified
                var collection = new Plans();
                collection.url = '/api/plans/?code='+code;
                collection.fetch().bind(this).then(function(){
                    if (collection.length) {
                        this.plan.set(collection.at(0));
                    }
                    this.plan.savePlan(this.status, this.selectedDisciplines, this.history);
                    this.plan.set({
                        'code': code
                    });
                    this.plan.save({});
                });
            } else {
                this.plan.savePlan(this.status, this.selectedDisciplines, this.history, true);
                this.plan.set({
                    'code': code
                }, {'silent': true});
                this.plan.save({}, {
                    'error': _.bind(function(){
                        // When the code is the same, the server return 404 and we need to
                        // remove ID of the known model, remove disabled class and call click on button again
                        this.plan.unset('id');
                        button.removeClass('disabled');
                        button.trigger('click');
                    }, this)
                });
            }
        },
        'openPlan': function(e){
            var code = this.getCode();
            if (!code) {
                return;
            }
            if (!this.user.get('is_authenticated')) {
                localStorage.setItem('plan-data', JSON.stringify({"code": code}));
                localStorage.setItem('plan-mode', 'open');
                this.$('#plan-not-authenticated').foundation('reveal', 'open');
                return;
            }
            var button = this.$('#open-button');
            if(button.is('.disabled')) {
                return;
            }
            button.addClass('disabled').html('Abrindo');
            if (e) {
                e.preventDefault();
            }
            var collection = new Plans();
            collection.url = '/api/plans/?code='+code;
            return collection.fetch().bind(this).then(function(){
                if (!collection.length) {
                    this.$('#plan-not-found').foundation('reveal', 'open');
                    return;
                }
                this.plan.set(collection.models[0].toJSON(), {'silent': true});
                this.plan.unset('_version', {'silent': true});
                this.plan.loadPlan(this.status, this.selectedDisciplines, this.history);
                button.removeClass('disabled').html('Abrir');
            });
        },
        'checkPreviousData': function(){
            var mode = localStorage.getItem('plan-mode');
            var data = localStorage.getItem('plan-data');
            if (!data || !data.length || !mode || !this.user.get('is_authenticated')) {
                return;
            }
            try {
                data = JSON.parse(data);
            } catch(ex) {
                return;
            }
            this.$("#plan-code").val(data.code);
            if (mode === 'open') {
                this.$('#open-button').trigger('click');
            } else if (mode === 'save') {
                this.plan.once('loaded', function(){
                    this.$('#save-button').trigger('click');
                }, this);
                this.plan.set(data);
                this.plan.loadPlan(this.status, this.selectedDisciplines, this.history);
            }
            localStorage.removeItem('plan-mode');
            localStorage.removeItem('plan-data');
        }
    });
});