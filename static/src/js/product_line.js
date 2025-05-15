odoo.define('odoo_pack_product.sale_order_line_color', function (require) {
    "use strict";
    
    var ListRenderer = require('web.ListRenderer');
    console.log("js file loaded"); 
    ListRenderer.include({
        _renderRow: function (record) {
            var $row = this._super.apply(this, arguments);
            // Check if this is a pack product
            if (record.data.is_pack_line) {
                $row.css('background-color', '#7FFFD4');
                $row.css('color', '#000000');            
            }
            if (record.data.is_pack) {
                $row.css('background-color', '#7FFFD4');
                $row.css('color', '#000000');
            }
            return $row;
        }   
    });
});