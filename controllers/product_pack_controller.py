from odoo import http
from odoo.http import request

class ProductPackController(http.Controller):

    @http.route('/sale/get_pack_components', type='json', auth='user')
    def get_pack_components(self, product_id, quantity):
        product = request.env['product.template'].browse(product_id)
        if not product or not product.is_pack:
            return []
        print("Fetching pack components for product:", product.name)
        return product.get_all_pack_components(quantity)
