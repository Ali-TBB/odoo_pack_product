from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is a Pack')
    pack_component_ids = fields.One2many(
        'pack.product.line',
        'pack_product_id',
        string='Pack Components'
    )
    pack_description = fields.Char(
        string='Pack Description',
        compute = '_compute_pack_description',
        store=True
    )
    pack_price = fields.Float(
        string='Pack Price',
        compute='_compute_pack_price',
        inverse='_inverse_pack_price',
        store=True,
        help="Automatically calculated sum of component prices"
    )

    @api.depends('pack_component_ids', 'pack_component_ids.component_id.list_price', 
                'pack_component_ids.quantity')
    def _compute_pack_price(self):
        for product in self:
            if product.is_pack and product.pack_component_ids:
                total = sum(
                    comp.component_id.list_price * comp.quantity
                    for comp in product.pack_component_ids
                )
                product.pack_price = total
            else:
                product.pack_price = 0.0

    def _inverse_pack_price(self):
        """Allow manual override of pack price while keeping component prices"""
        for product in self:
            if product.is_pack:
                product.list_price = product.pack_price

    @api.depends('pack_component_ids', 'name')
    def _compute_pack_description(self):
        for product in self:
            if product.is_pack and product.pack_component_ids:
                components = ", ".join(
                    [f"{line.quantity} x {line.component_id.name}" 
                     for line in product.pack_component_ids]
                )
                product.pack_description = (
                    f"{product.name} - Includes: {components}\n"
                )
            else:
                product.pack_description = False

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.is_pack:
            record._compute_pack_price()
            record.list_price = record.pack_price
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'pack_component_ids' in vals or 'is_pack' in vals:
            for product in self:
                if product.is_pack:
                    product._compute_pack_price()
                    product.list_price = product.pack_price
        return res

    def get_all_components(self, component_line):
        """Get all components of the pack"""
        components = []
        if component_line.component_id.is_pack:
            for sub_component in component_line.component_id.pack_component_ids:
                if not sub_component.component_id.is_pack:
                    # If the component is not a pack, add it directly
                    components.append(sub_component)
                else:
                    # Recursively get components of sub-components
                    components.extend(self.get_all_components(sub_component))
        return components

    def get_all_pack_components(self, quantity=1.0):
        components = []
        for line in self.pack_component_ids:
            if line.component_id.is_pack:
                sub_components = self.get_all_components(line)
                for sub in sub_components:
                    components.append({
                        'product_id': sub.component_id.id,
                        'name': sub.component_id.name,
                        'quantity': sub.quantity * quantity,
                        'uom_id': sub.component_id.uom_id.id,
                        'price_unit': sub.component_id.list_price,
                        'tax_ids': sub.component_id.taxes_id.ids,
                    })
            else:
                components.append({
                    'product_id': line.component_id.id,
                    'name': line.component_id.name,
                    'quantity': line.quantity * quantity,
                    'uom_id': line.component_id.uom_id.id,
                    'price_unit': line.component_id.list_price,
                    'tax_ids': line.component_id.taxes_id.ids,
                })
        return components
