# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ShowComponentWizard(models.TransientModel):
    _name = 'show.component.wizard'
    _description = 'Show Component Wizard'

    component_line_ids = fields.One2many(
        'show.component.wizard.line', 'wizard_id', string='All Components'
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if not active_id:
            return defaults

        product = self.env['product.template'].browse(active_id)

        # Collect all base lines of the pack
        all_components = []
        for line in product.pack_component_ids:
            if line.component_id.is_pack:
                nested = product.get_all_components(line)
                all_components.extend(nested)
            else:
                all_components.append(line)

        # Fill wizard lines
        defaults['component_line_ids'] = [(0, 0, {
            'component_id': comp.component_id.id,
            'quantity': comp.quantity,
            'uom_id': comp.uom_id.id,
        }) for comp in all_components]

        return defaults

class ShowComponentWizardLine(models.TransientModel):
    _name = 'show.component.wizard.line'
    _description = 'Component Line in Wizard'

    wizard_id = fields.Many2one('show.component.wizard', string='Wizard')
    component_id = fields.Many2one('product.template', string='Component')
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
