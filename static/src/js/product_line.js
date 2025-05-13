odoo.define('pack_product.sale_order_line_color', function (require) {
    "use strict";
    
    var ListRenderer = require('web.ListRenderer');
    
    ListRenderer.include({
        _renderRow: function (record) {
            var $row = this._super.apply(this, arguments);
            
            // Check if this is a pack product
            if (record.data.is_pack_line) {
                $row.css('background-color', '#ffdddd');  // Light red background
                $row.css('color', '#cc0000');             // Darker red text
            }
            
            return $row;
        }
    });
});