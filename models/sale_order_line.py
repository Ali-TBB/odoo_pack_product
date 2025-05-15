from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    is_pack_component = fields.Boolean(string="Is Pack Component", store=True)
    pack_parent_line_id = fields.Many2one('sale.order.line', string="Parent Pack Line")
    is_pack_line = fields.Boolean(related='product_id.is_pack', store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.order_id or not self.product_id:
            return

        if self.product_id.is_pack:
            component_lines = []
            for component in self.product_id.pack_component_ids:
                # Handle recursive sub-packs
                if component.component_id.is_pack:
                    sub_components = self.product_id.product_tmpl_id.get_all_components(component)
                    for sub in sub_components:
                        component_lines.append((0, 0, {
                            'product_id': sub.component_id.id,
                            'product_uom_qty': sub.quantity * self.product_uom_qty,
                            'price_unit': sub.component_id.list_price,
                            'is_pack_component': True,
                            'pack_parent_line_id': self.id,
                            'product_uom': sub.component_id.uom_id.id,
                            'tax_id': [(6, 0, sub.component_id.taxes_id.ids)],
                        }))
                else:
                    component_lines.append((0, 0, {
                        'product_id': component.component_id.id,
                        'product_uom_qty': component.quantity * self.product_uom_qty,
                        'price_unit': component.component_id.list_price,
                        'is_pack_component': True,
                        'pack_parent_line_id': self.id,
                        'product_uom': component.component_id.uom_id.id,
                        'tax_id': [(6, 0, component.component_id.taxes_id.ids)],
                    }))

            # Important: return the updated lines directly to the form
            return {
                'value': {
                    'price_unit': self.product_id.pack_price,
                    'order_line': component_lines,
                }
            }

        else:
            # Not a pack: clear sub-lines
            return {
                'value': {
                    'order_line': [],
                }
            }

    @api.model
    def create(self, vals):
        line = super().create(vals)
        if line.product_id.is_pack:
            # Create actual component lines after main line is created
            line._create_pack_components()
        return line

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals:
            for line in self:
                if line.product_id.is_pack:
                    # Remove old components and create new ones
                    self.env['sale.order.line'].search([
                        ('pack_parent_line_id', '=', line.id),
                        ('order_id', '=', line.order_id.id)
                    ]).unlink()
                    line._create_pack_components()
        return res

    def _create_pack_components(self):
        """Create actual pack component lines"""
        self.ensure_one()
        if self.product_id.is_pack:
            new_components = []
            for component in self.product_id.pack_component_ids:
                if component.component_id.is_pack:
                    # If the component is also a pack, create its components too
                    sub_components = self.product_id.get_all_components(component)
                    for sub_component in sub_components:
                        new_components.append({
                            'order_id': self.order_id.id,
                            'product_id': sub_component.component_id.id,
                            'product_uom_qty': sub_component.quantity * self.product_uom_qty,
                            'price_unit': sub_component.component_id.list_price,
                            'is_pack_component': True,
                            'pack_parent_line_id': self.id,
                            'product_uom': sub_component.component_id.uom_id.id,
                            'tax_id': [(6, 0, sub_component.component_id.taxes_id.ids)]
                        })
                else:
                    new_components.append({
                        'order_id': self.order_id.id,
                        'product_id': component.component_id.id,
                        'product_uom_qty': component.quantity * self.product_uom_qty,
                        'price_unit': component.component_id.list_price,
                        'is_pack_component': True,
                        'pack_parent_line_id': self.id,
                        'product_uom': component.component_id.uom_id.id,
                        'tax_id': [(6, 0, component.component_id.taxes_id.ids)]
                    })
            # Create the component lines in the order
            print("Creating pack components:", new_components)
            # Use create method to ensure proper creation
            self.env['sale.order.line'].create(new_components)
        



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """Override to exclude pack component prices from totals"""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if not line.product_id.is_pack:  # Only count non-component lines
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def action_open_pack_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Pack Product',
            'res_model': 'pack.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            },
        }

    
