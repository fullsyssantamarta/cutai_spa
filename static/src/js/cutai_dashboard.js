// Dashboard JS
odoo.define('cutai_laser_clinic.Dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var CutaiDashboard = AbstractAction.extend({
        contentTemplate: 'CutaiDashboard',
    });

    core.action_registry.add('cutai_dashboard', CutaiDashboard);

    return CutaiDashboard;
});
