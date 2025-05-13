from odoo import models, fields, api

class PackProductLine(models.Model):
    _name = 'pack.product.line'
    _description = 'Product Pack Component'
    _order = 'sequence,id'

    pack_product_id = fields.Many2one(
        'product.template',
        string='Pack Product',
        required=True,
        ondelete='cascade'
    )
    component_id = fields.Many2one(
        'product.template',
        string='Component',
        required=True,
        # domain="[('id', '!=', parent.pack_product_id)]"  # Changed domain syntax
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='component_id.uom_id',
        readonly=True
    )

    @api.onchange('component_id')
    def _onchange_component_id(self):
        message = {}
        if self.component_id.is_pack and self.component_id.id != self.pack_product_id.id:
            components = self.get_all_components_and_pack(self)
            if self.pack_product_id.id.origin in [comp.component_id.id for comp in components]:
                self.component_id = False
                message = {
                    'warning': {
                        'title': "Invalid Selection",
                        'message': "You cannot select a component that is part of another pack."
                    }
                }
            else:
                message = {
                    'warning': {
                        'title': "Confirm Selection",
                        'message': "You are selecting a pack as a component. Are you sure you want to proceed?"
                    }
                }
        if isinstance(self.pack_product_id.id, models.NewId) and self.component_id.id == self.pack_product_id.id.origin:
            self.component_id = False
            message = {
                'warning': {
                    'title': "Invalid Selection",
                    'message': "You cannot select the pack itself as a component."
                }
            }
        return message


    def get_all_components_and_pack(self, component_line):
        """Get all components of the pack"""
        components = []
        if component_line.component_id.is_pack:
            for sub_component in component_line.component_id.pack_component_ids:
                components.append(sub_component)
                components.extend(self.get_all_components(sub_component))
        return components
    